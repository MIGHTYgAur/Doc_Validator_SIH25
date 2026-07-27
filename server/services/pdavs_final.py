"""
PDAVS Pipeline — Parallel Document Authenticity Validation System
=================================================================
Supports two document modes:

  MODE 1: synthetic  (default)
    Generates structured academic transcript .txt files.
    Uses schema-based named section extraction.
    Good for: tamper localisation experiments.

  MODE 2: real
    Reads real files you supply (PDF, DOCX, any binary).
    PDFs are read as fixed-size CHUNK_SIZE byte blocks (RAG-style chunking).
    DOCX uses paragraph-level extraction; others fall back to byte chunks.
    Good for: benchmark / speedup experiments with realistic file sizes.

Stages:
  generate   — create N synthetic .txt transcripts
  issue      — hash all docs in a folder, store reference
  tamper     — make tampered copies of synthetic docs
  verify     — check docs against stored reference
  benchmark  — time sequential vs parallel on a folder of files

Usage (terminal):
  # synthetic pipeline end to end
  python pdavs_pipeline.py all --n 100

  # benchmark on real files you already have
  python pdavs_pipeline.py benchmark --real-dir /path/to/your/pdfs

  # issue + verify real files
  python pdavs_pipeline.py issue  --real-dir /path/to/your/pdfs
  python pdavs_pipeline.py verify --real-dir /path/to/your/pdfs

Dependencies:
  pip install faker python-docx pdfplumber
  (pdfplumber only needed for PDF page-level extraction)
"""

import hmac
import hashlib
import base64
import json
import random
import time
import argparse
import multiprocessing
import subprocess
from pathlib import Path
from faker import Faker

# ── Config ────────────────────────────────────────────────────────────────────

DOCS_DIR      = Path("docs/200kb_docs")
TAMPERED_DIR  = Path("docs/tampered_long_pdfs")
REFERENCE_DIR = Path("reference")
RESULTS_DIR   = Path("results")

# HMAC secret key — in production load from HSM / env variable
HMAC_KEY = b"pdavs-secret-key-vjti-2024"

# Byte chunk size for raw-file mode (64 KB — matches paper description)
CHUNK_SIZE = 64 * 1024

# Schema for synthetic transcripts: field_name → (start_line, end_line) inclusive
SCHEMA = {
    "header":      (0,  1),
    "identity":    (2,  6),
    "grades":      (7,  15),
    "summary":     (16, 17),
    "attestation": (18, 20),
}

TAMPER_TYPES = ["grade_flip", "name_swap", "roll_edit", "seal_modify", "whitespace"]

fake = Faker("en_IN")
random.seed(42)

LAST_CPP_PROCESSING_TIME_S = 0.0


def _resolve_cpp_hasher() -> Path | None:
    """Return the compiled C++ hasher executable if it exists."""
    here = Path(__file__).resolve().parent
    candidates = [here / "pdavs_hasher.exe", here / "pdavs_hasher"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

# ── Core Helpers ──────────────────────────────────────────────────────────────

def ensure_dirs():
    for d in [DOCS_DIR, TAMPERED_DIR, REFERENCE_DIR, RESULTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def hmac_hash_bytes(data: bytes) -> str:
    """HMAC-SHA256 of raw bytes. All extraction paths converge here."""
    return hmac.new(HMAC_KEY, data, hashlib.sha256).hexdigest()


def hmac_hash_str(text: str) -> str:
    """Convenience wrapper for text sections."""
    return hmac_hash_bytes(text.encode("utf-8"))


def merkle_root(hashes: list) -> str:
    """
    Build Merkle root from a list of hex digests.
    Odd number of nodes: duplicate last (standard convention).
    """
    nodes = list(hashes)
    if not nodes:
        return hashlib.sha256(b"").hexdigest()
    while len(nodes) > 1:
        if len(nodes) % 2 != 0:
            nodes.append(nodes[-1])
        nodes = [
            hashlib.sha256((nodes[i] + nodes[i+1]).encode()).hexdigest()
            for i in range(0, len(nodes), 2)
        ]
    return nodes[0]

# ── Section Extraction — Three Strategies ─────────────────────────────────────

def extract_sections_schema(doc_path: Path) -> dict:
    """
    STRATEGY 1 — Schema-based named extraction.
    For synthetic .txt transcripts only.
    Returns {field_name: text_string}.
    Localisation output: named field (grades, identity, etc.)
    """
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    sections = {}
    for name, (start, end) in SCHEMA.items():
        sections[name] = "\n".join(lines[start: end + 1])
    return sections


def extract_sections_pdf(doc_path: Path) -> dict:
    """
    STRATEGY 2 — Fixed-size byte-chunk extraction for PDF files.
    Reads raw PDF bytes in CHUNK_SIZE blocks (like RAG chunking, not page-wide).
    Returns {chunk_000: bytes, chunk_001: bytes, ...}.
    No pdfplumber dependency — works on any valid or partially corrupt PDF.
    """
    data = doc_path.read_bytes()
    total = len(data)
    n_chunks = max(1, (total + CHUNK_SIZE - 1) // CHUNK_SIZE)
    sections = {}
    for i in range(n_chunks):
        start = i * CHUNK_SIZE
        end   = min(start + CHUNK_SIZE, total)
        sections[f"chunk_{i:03d}"] = data[start:end]
    return sections


def extract_sections_docx(doc_path: Path) -> dict:
    """
    STRATEGY 3 — Paragraph-level extraction for DOCX files.
    Non-empty paragraphs = sections.
    Returns {para_000: bytes, para_001: bytes, ...}.
    Falls back to byte chunking if python-docx not installed.
    """
    try:
        from docx import Document
        doc = Document(doc_path)
        sections = {}
        idx = 0
        for para in doc.paragraphs:
            if para.text.strip():
                sections[f"para_{idx:03d}"] = para.text.encode("utf-8")
                idx += 1
        if sections:
            return sections
    except ImportError:
        pass
    return extract_sections_bytes(doc_path)


def extract_sections_bytes(doc_path: Path) -> dict:
    """
    STRATEGY 4 — Fixed-size byte chunking.
    Works on ANY file: PDF, PNG, binary cert, zip, anything.
    Returns {chunk_000: bytes, chunk_001: bytes, ...}.
    Localisation output: chunk index (maps to byte offset = idx * CHUNK_SIZE).
    This is the universal fallback.
    """
    data = doc_path.read_bytes()
    total = len(data)
    n_chunks = max(1, (total + CHUNK_SIZE - 1) // CHUNK_SIZE)
    sections = {}
    for i in range(n_chunks):
        start = i * CHUNK_SIZE
        end   = min(start + CHUNK_SIZE, total)
        sections[f"chunk_{i:03d}"] = data[start:end]
    return sections


def extract_sections(doc_path: Path) -> dict:
    """
    Universal dispatcher — picks extraction strategy by file extension.

      .txt  → schema-based named sections  (synthetic transcripts)
      .pdf  → page-level via pdfplumber    (falls back to byte chunks)
      .docx → paragraph-level             (falls back to byte chunks)
      other → 64KB byte chunks            (any file, always works)

    All strategies return {section_name: str | bytes}.
    The hashing layer handles both types transparently.
    """
    suffix = doc_path.suffix.lower()
    if suffix == ".txt":
        return extract_sections_schema(doc_path)
    elif suffix == ".pdf":
        return extract_sections_pdf(doc_path)
    elif suffix == ".docx":
        return extract_sections_docx(doc_path)
    else:
        return extract_sections_bytes(doc_path)


# ── Parallel Hashing ──────────────────────────────────────────────────────────

def _hash_one_section(args):
    """
    Pool worker: hash a single (name, content) pair.
    Must be a top-level function so multiprocessing can pickle it.
    Handles both str and bytes content.
    """
    name, content = args
    if isinstance(content, bytes):
        return name, hmac_hash_bytes(content)
    return name, hmac_hash_str(content)


def _normalize_section_bytes(content) -> bytes:
    """Normalize section content to raw bytes for the C++ hasher."""
    if isinstance(content, bytes):
        return content
    return content.encode("utf-8")


def hash_parallel_cpp(sections: dict, workers: int) -> dict:
    """
    Call the OpenMP C++ hasher.

    Python sends a flat JSON object of base64-encoded section bytes on stdin.
    The C++ utility computes HMAC-SHA256 hashes in parallel and returns JSON
    with the hashes plus the internal processing time.
    """
    cpp_exe = _resolve_cpp_hasher()
    if cpp_exe is None:
        raise FileNotFoundError("pdavs_hasher executable not found")

    payload = json.dumps(
        {k: base64.b64encode(_normalize_section_bytes(v)).decode("ascii") for k, v in sections.items()},
        separators=(",", ":"),
    )
    result = subprocess.run(
        [str(cpp_exe), str(max(1, workers))],
        input=payload.encode("utf-8"),
        capture_output=True,
        check=True,
    )

    data = json.loads(result.stdout.decode("utf-8"))
    global LAST_CPP_PROCESSING_TIME_S
    LAST_CPP_PROCESSING_TIME_S = float(data.get("processing_time_s", 0.0))
    return data["hashes"]


def hash_sections_parallel(sections: dict, workers: int = 1) -> dict:
    """
    Hash all sections of one document.
    workers=1  → sequential (benchmarking baseline).
    workers>1  → multiprocessing.Pool across sections.

    Note: section-level parallelism only pays off for large documents
    with many chunks (real files). For small synthetic docs the
    sequential path is faster. File-level parallelism is in benchmark.
    """
    global LAST_CPP_PROCESSING_TIME_S
    items = list(sections.items())
    cpp_exe = _resolve_cpp_hasher()
    if cpp_exe is not None:
        return hash_parallel_cpp(sections, workers)
    if workers == 1 or len(items) < 4:
        start = time.perf_counter()
        result = dict(_hash_one_section(item) for item in items)
        LAST_CPP_PROCESSING_TIME_S = time.perf_counter() - start
        return result
    start = time.perf_counter()
    with multiprocessing.Pool(processes=workers) as pool:
        result = dict(pool.map(_hash_one_section, items))
    LAST_CPP_PROCESSING_TIME_S = time.perf_counter() - start
    return result

# ── Stage 1: Generate Synthetic Documents ─────────────────────────────────────

COURSES = [
    "Data Structures & Algorithms",
    "Operating Systems",
    "Database Management Systems",
    "Computer Networks",
    "Software Engineering",
    "Machine Learning",
    "Computer Organisation",
    "Engineering Mathematics",
]
PROGRAMMES = [
    "B.Tech Computer Engineering",
    "B.Tech Information Technology",
    "B.Tech Electronics Engineering",
]
DIVISIONS = ["A", "B", "C"]


def random_grade() -> float:
    return round(random.choice([x / 2 for x in range(10, 21)]), 1)


def generate_document(index: int) -> str:
    """
    Synthetic academic transcript as plain text.
    Line layout matches SCHEMA exactly — do not reorder lines.
    """
    name      = fake.name()
    roll      = f"23108{index:04d}"
    programme = random.choice(PROGRAMMES)
    year      = random.randint(2021, 2023)
    division  = random.choice(DIVISIONS)
    semester  = random.randint(3, 8)
    courses   = random.sample(COURSES, 8)
    grades    = {c: random_grade() for c in courses}
    cgpa      = round(sum(grades.values()) / len(grades), 2)
    result    = "PASS" if cgpa >= 5.0 else "FAIL"
    date      = fake.date_between(start_date="-1y", end_date="today").strftime("%d-%b-%Y")
    seal      = f"VJTI-REG-{year}-{index:05d}"

    lines = [
        # header: lines 0-1
        "VEERMATA JIJABAI TECHNOLOGICAL INSTITUTE, MUMBAI",
        "OFFICIAL ACADEMIC TRANSCRIPT",
        # identity: lines 2-6
        f"Name          : {name}",
        f"Roll Number   : {roll}",
        f"Programme     : {programme}",
        f"Year          : {year}",
        f"Division      : {division}",
        # grades: lines 7-15 (semester + 8 courses)
        f"Semester      : {semester}",
        *[f"{c:<40}: {g}" for c, g in grades.items()],
        # summary: lines 16-17
        f"CGPA          : {cgpa}",
        f"Result        : {result}",
        # attestation: lines 18-20
        f"Date          : {date}",
        f"Registrar     : Dr. {fake.last_name()}",
        f"Seal          : {seal}",
    ]
    return "\n".join(lines)


def stage_generate(n: int):
    """Generate N synthetic transcripts into DOCS_DIR."""
    ensure_dirs()
    print(f"\n[GENERATE] Creating {n} documents in {DOCS_DIR}/")
    for i in range(n):
        path = DOCS_DIR / f"transcript_{i:04d}.txt"
        path.write_text(generate_document(i), encoding="utf-8")
    print(f"[GENERATE] Done — {n} documents written.")

# ── Stage 2: Issue ────────────────────────────────────────────────────────────

def issue_document(doc_path: Path, workers: int = 1) -> dict:
    """
    Hash one document's sections and build Merkle root.
    Works for any file type via the universal extractor.
    """
    sections       = extract_sections(doc_path)
    section_hashes = hash_sections_parallel(sections, workers)
    root           = merkle_root(list(section_hashes.values()))
    return {
        "document":       doc_path.name,
        "section_hashes": section_hashes,
        "merkle_root":    root,
        "n_sections":     len(section_hashes),
        "file_bytes":     doc_path.stat().st_size,
        "hash_processing_time_s": round(LAST_CPP_PROCESSING_TIME_S, 6),
    }


def _get_doc_paths(real_dir: Path = None) -> list:
    """
    Return list of document paths to process.
    real_dir given → all files in that directory (any type).
    Otherwise      → synthetic .txt files in DOCS_DIR.
    """
    if real_dir:
        exts = {".pdf", ".docx", ".txt", ".png", ".jpg", ".bin", ".xml", ".json"}
        paths = [p for p in sorted(real_dir.iterdir())
                 if p.is_file() and p.suffix.lower() in exts]
        if not paths:
            # no recognised extensions — take all files in directory
            paths = [p for p in sorted(real_dir.iterdir()) if p.is_file()]
        return paths
    return sorted(DOCS_DIR.glob("*.txt"))


def stage_issue(workers: int = 1, real_dir: Path = None):
    """Issue all documents — hash sections, store references in REFERENCE_DIR."""
    ensure_dirs()
    doc_paths = _get_doc_paths(real_dir)
    if not doc_paths:
        print(f"[ISSUE] No documents found in {real_dir or DOCS_DIR}.")
        return

    label = f"real files from {real_dir}" if real_dir else "synthetic docs"
    print(f"\n[ISSUE] Issuing {len(doc_paths)} {label} (workers={workers}) ...")

    # Use file-level parallelism when workers>1 to avoid spawning a Pool per document.
    if workers == 1:
        for path in doc_paths:
            record = issue_document(path, workers=1)
            ref_path = REFERENCE_DIR / (path.stem + ".json")
            ref_path.write_text(json.dumps(record, indent=2))
    else:
        path_strs = [str(p) for p in doc_paths]
        with multiprocessing.Pool(processes=workers) as pool:
            records = pool.map(_issue_worker, path_strs)
        for record in records:
            ref_path = REFERENCE_DIR / (Path(record["document"]).stem + ".json")
            ref_path.write_text(json.dumps(record, indent=2))

    print(f"[ISSUE] Done — references stored in {REFERENCE_DIR}/")

# ── Stage 3: Tamper (synthetic only) ─────────────────────────────────────────

def apply_tamper(lines: list, tamper_type: str) -> tuple:
    """
    Apply one controlled byte-level alteration to document lines.
    Returns (modified_lines, tamper_type, line_changed).
    """
    lines = list(lines)

    if tamper_type == "grade_flip":
        line_idx = random.randint(8, 15)
        parts = lines[line_idx].rsplit(":", 1)
        try:
            val = float(parts[1].strip())
            new_val = min(10.0, val + 0.5) if val < 10.0 else val - 0.5
            lines[line_idx] = f"{parts[0]}: {new_val}"
        except (ValueError, IndexError):
            pass

    elif tamper_type == "name_swap":
        parts = lines[2].split(":", 1)
        lines[2] = f"{parts[0]}: {fake.name()}"
        line_idx = 2

    elif tamper_type == "roll_edit":
        parts = lines[3].split(":", 1)
        roll = parts[1].strip()
        roll = roll[:-1] + str((int(roll[-1]) + 1) % 10)
        lines[3] = f"{parts[0]}: {roll}"
        line_idx = 3

    elif tamper_type == "seal_modify":
        parts = lines[20].split(":", 1)
        lines[20] = f"{parts[0]}: FAKE-SEAL-0000"
        line_idx = 20

    elif tamper_type == "whitespace":
        lines[0] = lines[0] + " "
        line_idx = 0

    else:
        line_idx = -1

    return lines, tamper_type, line_idx


def _tamper_pdf_bytes(src_path: Path, dst_path: Path) -> dict:
    """
    Byte-level tamper for PDF files: XOR a few bytes deep inside the file
    (past the header) so the mutation lands in real content, not just metadata.
    Saves tampered copy to dst_path. Returns tamper metadata.
    """
    data = bytearray(src_path.read_bytes())

    total = len(data)
    n_chunks = max(1, (total + CHUNK_SIZE - 1) // CHUNK_SIZE)

    # Pick a random chunk so the tamper is not biased toward chunk_000.
    # For chunk_000, keep the mutation past the PDF header.
    chunk_idx = random.randrange(n_chunks)
    chunk_start = chunk_idx * CHUNK_SIZE
    chunk_end = min(chunk_start + CHUNK_SIZE, total)
    offset = random.randint(max(chunk_start, 256), max(chunk_start, chunk_end - 1))

    n_bytes = min(4, total - offset)
    for i in range(n_bytes):
        data[offset + i] ^= 0xFF          # bit-flip: guaranteed change
    dst_path.write_bytes(bytes(data))
    return {
        "tamper_type":  "byte_flip",
        "byte_offset":  offset,
        "bytes_changed": n_bytes,
        "chunk_index":  chunk_idx,
    }


def stage_tamper(real_dir: Path = None):
    """
    Create one tampered copy of each document with a controlled alteration.
      .txt files (synthetic) → random schema-level text mutation (existing logic).
      .pdf files             → raw byte-flip at a fixed offset inside the file.
    Tampered copies and metadata JSON go into TAMPERED_DIR.
    """
    ensure_dirs()

    if real_dir:
        pdf_paths = sorted(real_dir.glob("*.pdf"))
        txt_paths = []
    else:
        pdf_paths = sorted(DOCS_DIR.glob("*.pdf"))
        txt_paths = sorted(DOCS_DIR.glob("*.txt"))

    if not txt_paths and not pdf_paths:
        print("[TAMPER] No documents found. Run 'generate' first or pass --real-dir.")
        return

    # ── PDF tamper ────────────────────────────────────────────────────────────
    if pdf_paths:
        print(f"\n[TAMPER] Byte-flipping {len(pdf_paths)} PDF(s) ...")
        for path in pdf_paths:
            dst  = TAMPERED_DIR / path.name
            meta = _tamper_pdf_bytes(path, dst)
            (TAMPERED_DIR / (path.stem + "_tamper.json")).write_text(
                json.dumps(meta, indent=2)
            )
            print(f"         {path.name} → offset {meta['byte_offset']} "
                  f"({meta['bytes_changed']} bytes flipped, chunk_{meta['chunk_index']:03d})")

    # ── Synthetic .txt tamper (unchanged logic) ───────────────────────────────
    if txt_paths:
        print(f"\n[TAMPER] Tampering {len(txt_paths)} synthetic .txt document(s) ...")
        type_counts = {t: 0 for t in TAMPER_TYPES}

        for path in txt_paths:
            lines       = path.read_text(encoding="utf-8").splitlines()
            tamper_type = random.choice(TAMPER_TYPES)
            new_lines, ttype, line_no = apply_tamper(lines, tamper_type)
            type_counts[ttype] += 1

            (TAMPERED_DIR / path.name).write_text("\n".join(new_lines), encoding="utf-8")
            (TAMPERED_DIR / (path.stem + "_tamper.json")).write_text(json.dumps({
                "tamper_type":  ttype,
                "line_changed": line_no,
            }))

        print(f"[TAMPER] Done. Alteration breakdown:")
        for t, c in type_counts.items():
            print(f"         {t:<20} : {c}")

# ── Stage 4: Verify ───────────────────────────────────────────────────────────

def verify_document(doc_path: Path, workers: int = 1) -> dict:
    """
    Two-phase verification against stored reference.
    Phase 1 (fast): compare Merkle roots. Match → PASS immediately.
    Phase 2 (slow): compare per-section hashes to localise tamper.
    Works for any file type.
    """
    ref_path = REFERENCE_DIR / (doc_path.stem + ".json")
    if not ref_path.exists():
        return {"document": doc_path.name, "status": "NO_REFERENCE"}

    ref         = json.loads(ref_path.read_text())
    sections    = extract_sections(doc_path)
    live_hashes = hash_sections_parallel(sections, workers)
    live_root   = merkle_root(list(live_hashes.values()))

    if live_root == ref["merkle_root"]:
        return {
            "document": doc_path.name,
            "status": "PASS",
            "tampered_sections": [],
            "hash_processing_time_s": round(LAST_CPP_PROCESSING_TIME_S, 6),
        }

    tampered = [
        name for name in live_hashes
        if live_hashes[name] != ref["section_hashes"].get(name)
    ]
    return {
        "document":          doc_path.name,
        "status":            "FAIL",
        "tampered_sections": tampered,
        "hash_processing_time_s": round(LAST_CPP_PROCESSING_TIME_S, 6),
    }


def stage_verify(source: str = "tampered", workers: int = 1, real_dir: Path = None):
    """
    Verify documents and print summary.
      source='original' → sanity check, originals should all PASS.
      source='tampered' → detection check, tampered should all FAIL.
      real_dir          → verify those real files against stored references.
    """
    ensure_dirs()

    if real_dir:
        doc_paths = _get_doc_paths(real_dir)
        label = f"real files from {real_dir}"
    elif source == "tampered":
        doc_paths = sorted(TAMPERED_DIR.glob("*.txt"))
        label = "tampered synthetic docs"
    else:
        doc_paths = sorted(DOCS_DIR.glob("*.txt"))
        label = "original synthetic docs"

    if not doc_paths:
        print("[VERIFY] No documents found.")
        return

    print(f"\n[VERIFY] Verifying {len(doc_paths)} {label} (workers={workers}) ...")

    results        = []
    correct_local  = 0
    total_tampered = 0

    # File-level parallelism: map verification across documents when workers>1.
    if workers == 1:
        for path in doc_paths:
            result = verify_document(path, workers=1)
            results.append(result)

            # localisation accuracy — only measurable for synthetic tampered docs
            meta_path = TAMPERED_DIR / (path.stem + "_tamper.json")
            if meta_path.exists() and result["status"] == "FAIL":
                total_tampered += 1
                meta = json.loads(meta_path.read_text())
                expected = {
                    "grade_flip":  "grades",
                    "name_swap":   "identity",
                    "roll_edit":   "identity",
                    "seal_modify": "attestation",
                    "whitespace":  "header",
                }.get(meta["tamper_type"], "unknown")
                if expected in result.get("tampered_sections", []):
                    correct_local += 1
    else:
        path_strs = [str(p) for p in doc_paths]
        with multiprocessing.Pool(processes=workers) as pool:
            results = pool.map(_verify_worker, path_strs)

        # localisation accuracy for each result (use document name from result)
        for result in results:
            meta_path = TAMPERED_DIR / (Path(result["document"]).stem + "_tamper.json")
            if meta_path.exists() and result["status"] == "FAIL":
                total_tampered += 1
                meta = json.loads(meta_path.read_text())
                expected = {
                    "grade_flip":  "grades",
                    "name_swap":   "identity",
                    "roll_edit":   "identity",
                    "seal_modify": "attestation",
                    "whitespace":  "header",
                }.get(meta["tamper_type"], "unknown")
                if expected in result.get("tampered_sections", []):
                    correct_local += 1

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    print(f"\n{'─'*55}")
    print(f"  Documents verified : {len(results)}")
    print(f"  PASS               : {passed}")
    print(f"  FAIL (detected)    : {failed}")
    if total_tampered > 0:
        acc = 100 * correct_local / total_tampered
        print(f"  Localisation acc.  : {correct_local}/{total_tampered} = {acc:.1f}%")
    print(f"{'─'*55}")

    out = RESULTS_DIR / f"verify_{source}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"[VERIFY] Full results → {out}")

# ── Stage 5: Benchmark ────────────────────────────────────────────────────────

def _verify_worker(path_str: str) -> dict:
    """Top-level pool worker — takes path as string (required for pickling)."""
    return verify_document(Path(path_str), workers=1)


def _issue_worker(path_str: str) -> dict:
    """Top-level pool worker for issuing a document (file-level parallelism)."""
    return issue_document(Path(path_str), workers=1)


def _time_processing_only(paths: list, workers: int) -> float:
    """Sum only the C++ hashing processing time across a batch of documents."""
    total = 0.0
    for path in paths:
        sections = extract_sections(path)
        hash_sections_parallel(sections, workers)
        total += LAST_CPP_PROCESSING_TIME_S
    return total


def stage_benchmark(real_dir: Path = None):
    """
        Benchmark section hashing processing time across batch sizes.

    Synthetic .txt files (~1KB):
            Expect tiny processing times.

    Real files (PDF/DOCX, 100KB+):
            The C++ OpenMP hasher should show clearer scaling as chunk count grows.

        Output: printed table + results/benchmark.csv
    """
    ensure_dirs()
    all_paths = _get_doc_paths(real_dir)

    if not all_paths:
        print(f"[BENCHMARK] No documents found in {real_dir or DOCS_DIR}.")
        return

    n_docs    = len(all_paths)
    sizes_kb  = [p.stat().st_size / 1024 for p in all_paths]
    avg_kb    = sum(sizes_kb) / len(sizes_kb)
    mode      = f"real ({real_dir})" if real_dir else "synthetic"

    batch_sizes   = sorted(set([min(10,n_docs), min(25,n_docs), min(50,n_docs), n_docs]))
    worker_counts = [1, 2, 4]

    print(f"\n[BENCHMARK] Mode           : {mode}")
    print(f"            Total files    : {n_docs}")
    print(f"            Avg size       : {avg_kb:.1f} KB")
    print(f"            Chunk size     : {CHUNK_SIZE//1024} KB")
    if avg_kb < 50:
        print(f"\n  NOTE: Small files detected (avg {avg_kb:.1f} KB).")
        print(f"  Processing time will be tiny; larger PDFs are more meaningful.")

    print(f"\n{'Batch':>8} {'Workers':>8} {'Time(s)':>10} "
          f"{'Speedup':>10} {'Eff%':>8} {'Regime':>20}")
    print("─" * 72)

    rows     = []
    baseline = {}

    for n in batch_sizes:
        paths = all_paths[:n]
        for w in worker_counts:
            t = _time_processing_only(paths, w)
            if w == 1:
                baseline[n] = t

            speedup = baseline[n] / t if t > 0 else 1.0
            eff     = 100 * speedup / w
            regime  = ("overhead-dominated" if speedup < 0.8
                       else "limited scaling"  if speedup < 1.5
                       else "good scaling")

            print(f"{n:>8} {w:>8} {t:>10.4f} {speedup:>10.2f} "
                  f"{eff:>8.1f} {regime:>20}")
            rows.append({
                "batch": n, "workers": w,
                "time_s": round(t, 4),
                "speedup": round(speedup, 2),
                "efficiency_pct": round(eff, 1),
                "avg_file_kb": round(avg_kb, 1),
                "regime": regime,
            })

    csv_path = RESULTS_DIR / "benchmark.csv"
    with open(csv_path, "w") as f:
        f.write("batch,workers,time_s,speedup,efficiency_pct,avg_file_kb,regime\n")
        for r in rows:
            f.write(f"{r['batch']},{r['workers']},{r['time_s']},"
                    f"{r['speedup']},{r['efficiency_pct']},"
                    f"{r['avg_file_kb']},{r['regime']}\n")

    print(f"\n[BENCHMARK] Saved → {csv_path}")

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDAVS — Parallel Document Authenticity Validation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdavs_pipeline.py all --n 100
  python pdavs_pipeline.py benchmark --real-dir ~/Downloads/papers
  python pdavs_pipeline.py issue  --real-dir ~/Documents/certs
  python pdavs_pipeline.py verify --real-dir ~/Documents/certs
        """
    )
    parser.add_argument(
        "stage",
        choices=["generate", "issue", "tamper", "verify", "benchmark", "all"],
    )
    parser.add_argument("--n",       type=int,  default=50,
                        help="Synthetic docs to generate (default 50)")
    parser.add_argument("--workers", type=int,  default=1,
                        help="Section-level hash workers (default 1)")
    parser.add_argument("--source",  choices=["original","tampered"],
                        default="tampered",
                        help="Which docs to verify (default: tampered)")
    parser.add_argument("--real-dir", type=Path, default=None, metavar="DIR",
                        help="Folder of real files for issue/verify/benchmark")

    args = parser.parse_args()
    rd   = args.real_dir

    if args.stage == "generate":
        stage_generate(args.n)

    elif args.stage == "issue":
        stage_issue(args.workers, real_dir=rd)

    elif args.stage == "tamper":
        stage_tamper(real_dir=rd)

    elif args.stage == "verify":
        stage_verify(args.source, args.workers, real_dir=rd)

    elif args.stage == "benchmark":
        stage_benchmark(real_dir=rd)

    elif args.stage == "all":
        stage_generate(args.n)
        stage_issue(workers=1)
        stage_tamper(real_dir=None)
        stage_verify(source="original", workers=1)
        stage_verify(source="tampered", workers=1)
        stage_benchmark()
        if rd:
            print("\n" + "="*55)
            print("  BENCHMARK — REAL FILES")
            print("="*55)
            stage_benchmark(real_dir=rd)


if __name__ == "__main__":
    main()