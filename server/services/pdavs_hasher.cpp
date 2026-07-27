#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <omp.h>

namespace {

std::string read_stdin() {
    std::ostringstream buffer;
    buffer << std::cin.rdbuf();
    return buffer.str();
}

void skip_ws(const std::string &text, std::size_t &pos) {
    while (pos < text.size() && std::isspace(static_cast<unsigned char>(text[pos]))) {
        ++pos;
    }
}

std::string parse_json_string(const std::string &text, std::size_t &pos) {
    if (pos >= text.size() || text[pos] != '"') {
        throw std::runtime_error("expected JSON string");
    }
    ++pos;
    std::string out;
    while (pos < text.size()) {
        char ch = text[pos++];
        if (ch == '"') {
            return out;
        }
        if (ch == '\\') {
            if (pos >= text.size()) {
                throw std::runtime_error("unterminated escape sequence");
            }
            char esc = text[pos++];
            switch (esc) {
                case '"': out.push_back('"'); break;
                case '\\': out.push_back('\\'); break;
                case '/': out.push_back('/'); break;
                case 'b': out.push_back('\b'); break;
                case 'f': out.push_back('\f'); break;
                case 'n': out.push_back('\n'); break;
                case 'r': out.push_back('\r'); break;
                case 't': out.push_back('\t'); break;
                case 'u': {
                    if (pos + 4 > text.size()) {
                        throw std::runtime_error("short unicode escape");
                    }
                    unsigned code = 0;
                    for (int i = 0; i < 4; ++i) {
                        char c = text[pos++];
                        code <<= 4;
                        if (c >= '0' && c <= '9') code |= static_cast<unsigned>(c - '0');
                        else if (c >= 'a' && c <= 'f') code |= static_cast<unsigned>(10 + c - 'a');
                        else if (c >= 'A' && c <= 'F') code |= static_cast<unsigned>(10 + c - 'A');
                        else throw std::runtime_error("invalid unicode escape");
                    }
                    if (code <= 0x7F) {
                        out.push_back(static_cast<char>(code));
                    } else if (code <= 0x7FF) {
                        out.push_back(static_cast<char>(0xC0 | (code >> 6)));
                        out.push_back(static_cast<char>(0x80 | (code & 0x3F)));
                    } else {
                        out.push_back(static_cast<char>(0xE0 | (code >> 12)));
                        out.push_back(static_cast<char>(0x80 | ((code >> 6) & 0x3F)));
                        out.push_back(static_cast<char>(0x80 | (code & 0x3F)));
                    }
                    break;
                }
                default:
                    throw std::runtime_error("unsupported JSON escape");
            }
        } else {
            out.push_back(ch);
        }
    }
    throw std::runtime_error("unterminated JSON string");
}

std::vector<std::pair<std::string, std::string>> parse_flat_json_object(const std::string &text) {
    std::size_t pos = 0;
    skip_ws(text, pos);
    if (pos >= text.size() || text[pos] != '{') {
        throw std::runtime_error("expected JSON object");
    }
    ++pos;

    std::vector<std::pair<std::string, std::string>> items;
    skip_ws(text, pos);
    if (pos < text.size() && text[pos] == '}') {
        return items;
    }

    while (pos < text.size()) {
        skip_ws(text, pos);
        std::string key = parse_json_string(text, pos);
        skip_ws(text, pos);
        if (pos >= text.size() || text[pos] != ':') {
            throw std::runtime_error("expected colon");
        }
        ++pos;
        skip_ws(text, pos);
        std::string value = parse_json_string(text, pos);
        items.emplace_back(std::move(key), std::move(value));
        skip_ws(text, pos);
        if (pos >= text.size()) {
            throw std::runtime_error("unexpected end of JSON");
        }
        if (text[pos] == ',') {
            ++pos;
            continue;
        }
        if (text[pos] == '}') {
            ++pos;
            break;
        }
        throw std::runtime_error("expected comma or end of object");
    }

    skip_ws(text, pos);
    if (pos != text.size()) {
        throw std::runtime_error("trailing JSON data");
    }
    return items;
}

int b64_value(char c) {
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}

std::vector<unsigned char> base64_decode(const std::string &input) {
    std::string clean;
    clean.reserve(input.size());
    for (char c : input) {
        if (!std::isspace(static_cast<unsigned char>(c))) {
            clean.push_back(c);
        }
    }

    if (clean.size() % 4 != 0) {
        throw std::runtime_error("invalid base64 length");
    }

    std::vector<unsigned char> output;
    output.reserve((clean.size() / 4) * 3);

    for (std::size_t i = 0; i < clean.size(); i += 4) {
        int v0 = clean[i] == '=' ? 0 : b64_value(clean[i]);
        int v1 = clean[i + 1] == '=' ? 0 : b64_value(clean[i + 1]);
        int v2 = clean[i + 2] == '=' ? 0 : b64_value(clean[i + 2]);
        int v3 = clean[i + 3] == '=' ? 0 : b64_value(clean[i + 3]);
        if (v0 < 0 || v1 < 0 || (clean[i + 2] != '=' && v2 < 0) || (clean[i + 3] != '=' && v3 < 0)) {
            throw std::runtime_error("invalid base64 character");
        }

        unsigned triple = (static_cast<unsigned>(v0) << 18) |
                          (static_cast<unsigned>(v1) << 12) |
                          (static_cast<unsigned>(v2) << 6) |
                          static_cast<unsigned>(v3);
        output.push_back(static_cast<unsigned char>((triple >> 16) & 0xFF));
        if (clean[i + 2] != '=') {
            output.push_back(static_cast<unsigned char>((triple >> 8) & 0xFF));
        }
        if (clean[i + 3] != '=') {
            output.push_back(static_cast<unsigned char>(triple & 0xFF));
        }
    }
    return output;
}

std::string hex_encode(const unsigned char *data, std::size_t size) {
    static const char *digits = "0123456789abcdef";
    std::string out;
    out.reserve(size * 2);
    for (std::size_t i = 0; i < size; ++i) {
        unsigned char b = data[i];
        out.push_back(digits[b >> 4]);
        out.push_back(digits[b & 0x0F]);
    }
    return out;
}

class SHA256 {
public:
    SHA256() { reset(); }

    void reset() {
        bit_len_ = 0;
        buffer_len_ = 0;
        state_ = {
            0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
            0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u
        };
    }

    void update(const unsigned char *data, std::size_t len) {
        bit_len_ += static_cast<std::uint64_t>(len) * 8ULL;
        for (std::size_t i = 0; i < len; ++i) {
            buffer_[buffer_len_++] = data[i];
            if (buffer_len_ == 64) {
                transform(buffer_.data());
                buffer_len_ = 0;
            }
        }
    }

    std::array<unsigned char, 32> final() {
        std::array<unsigned char, 32> digest{};
        std::size_t i = buffer_len_;

        buffer_[i++] = 0x80;
        if (i > 56) {
            while (i < 64) {
                buffer_[i++] = 0x00;
            }
            transform(buffer_.data());
            i = 0;
        }
        while (i < 56) {
            buffer_[i++] = 0x00;
        }

        for (int shift = 7; shift >= 0; --shift) {
            buffer_[56 + (7 - shift)] = static_cast<unsigned char>((bit_len_ >> (shift * 8)) & 0xFF);
        }
        transform(buffer_.data());

        for (int j = 0; j < 8; ++j) {
            digest[j * 4 + 0] = static_cast<unsigned char>((state_[j] >> 24) & 0xFF);
            digest[j * 4 + 1] = static_cast<unsigned char>((state_[j] >> 16) & 0xFF);
            digest[j * 4 + 2] = static_cast<unsigned char>((state_[j] >> 8) & 0xFF);
            digest[j * 4 + 3] = static_cast<unsigned char>(state_[j] & 0xFF);
        }
        return digest;
    }

private:
    std::array<std::uint32_t, 8> state_{};
    std::array<unsigned char, 64> buffer_{};
    std::size_t buffer_len_ = 0;
    std::uint64_t bit_len_ = 0;

    static std::uint32_t rotr(std::uint32_t x, std::uint32_t n) {
        return (x >> n) | (x << (32U - n));
    }

    static std::uint32_t choose(std::uint32_t e, std::uint32_t f, std::uint32_t g) {
        return (e & f) ^ (~e & g);
    }

    static std::uint32_t majority(std::uint32_t a, std::uint32_t b, std::uint32_t c) {
        return (a & b) ^ (a & c) ^ (b & c);
    }

    static std::uint32_t big_sigma0(std::uint32_t x) {
        return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
    }

    static std::uint32_t big_sigma1(std::uint32_t x) {
        return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
    }

    static std::uint32_t small_sigma0(std::uint32_t x) {
        return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
    }

    static std::uint32_t small_sigma1(std::uint32_t x) {
        return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
    }

    void transform(const unsigned char *chunk) {
        static const std::array<std::uint32_t, 64> k = {
            0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
            0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
            0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
            0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
            0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
            0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
            0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
            0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
            0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
            0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
            0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
            0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
            0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
            0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
            0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
            0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u
        };

        std::array<std::uint32_t, 64> w{};
        for (int i = 0; i < 16; ++i) {
            w[i] = (static_cast<std::uint32_t>(chunk[i * 4]) << 24) |
                   (static_cast<std::uint32_t>(chunk[i * 4 + 1]) << 16) |
                   (static_cast<std::uint32_t>(chunk[i * 4 + 2]) << 8) |
                   static_cast<std::uint32_t>(chunk[i * 4 + 3]);
        }
        for (int i = 16; i < 64; ++i) {
            w[i] = small_sigma1(w[i - 2]) + w[i - 7] + small_sigma0(w[i - 15]) + w[i - 16];
        }

        std::uint32_t a = state_[0];
        std::uint32_t b = state_[1];
        std::uint32_t c = state_[2];
        std::uint32_t d = state_[3];
        std::uint32_t e = state_[4];
        std::uint32_t f = state_[5];
        std::uint32_t g = state_[6];
        std::uint32_t h = state_[7];

        for (int i = 0; i < 64; ++i) {
            std::uint32_t temp1 = h + big_sigma1(e) + choose(e, f, g) + k[i] + w[i];
            std::uint32_t temp2 = big_sigma0(a) + majority(a, b, c);
            h = g;
            g = f;
            f = e;
            e = d + temp1;
            d = c;
            c = b;
            b = a;
            a = temp1 + temp2;
        }

        state_[0] += a;
        state_[1] += b;
        state_[2] += c;
        state_[3] += d;
        state_[4] += e;
        state_[5] += f;
        state_[6] += g;
        state_[7] += h;
    }
};

std::array<unsigned char, 32> sha256_bytes(const std::vector<unsigned char> &data) {
    SHA256 sha;
    if (!data.empty()) {
        sha.update(data.data(), data.size());
    }
    return sha.final();
}

std::array<unsigned char, 32> hmac_sha256_bytes(const std::vector<unsigned char> &key,
                                                const std::vector<unsigned char> &message) {
    std::vector<unsigned char> normalized_key = key;
    if (normalized_key.size() > 64) {
        auto hashed = sha256_bytes(normalized_key);
        normalized_key.assign(hashed.begin(), hashed.end());
    }
    normalized_key.resize(64, 0x00);

    std::array<unsigned char, 64> ipad{};
    std::array<unsigned char, 64> opad{};
    for (int i = 0; i < 64; ++i) {
        ipad[i] = static_cast<unsigned char>(normalized_key[i] ^ 0x36);
        opad[i] = static_cast<unsigned char>(normalized_key[i] ^ 0x5c);
    }

    SHA256 inner;
    inner.update(ipad.data(), ipad.size());
    if (!message.empty()) {
        inner.update(message.data(), message.size());
    }
    auto inner_digest = inner.final();

    SHA256 outer;
    outer.update(opad.data(), opad.size());
    outer.update(inner_digest.data(), inner_digest.size());
    return outer.final();
}

std::string json_escape(const std::string &text) {
    std::string out;
    out.reserve(text.size() + 16);
    for (char ch : text) {
        switch (ch) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b"; break;
            case '\f': out += "\\f"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(ch) < 0x20) {
                    std::ostringstream oss;
                    oss << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                        << static_cast<int>(static_cast<unsigned char>(ch));
                    out += oss.str();
                } else {
                    out.push_back(ch);
                }
        }
    }
    return out;
}

}  // namespace

int main(int argc, char **argv) {
    try {
        int workers = 1;
        if (argc >= 2) {
            workers = std::max(1, std::atoi(argv[1]));
        }
        omp_set_num_threads(workers);

        const std::string payload = read_stdin();
        const auto items = parse_flat_json_object(payload);

        std::vector<std::pair<std::string, std::string>> hashes(items.size());
        const std::vector<unsigned char> hmac_key = []() {
            const std::string key = "pdavs-secret-key-vjti-2024";
            return std::vector<unsigned char>(key.begin(), key.end());
        }();

        auto start = std::chrono::high_resolution_clock::now();

        #pragma omp parallel for schedule(static)
        for (int i = 0; i < static_cast<int>(items.size()); ++i) {
            const std::string &name = items[static_cast<std::size_t>(i)].first;
            const std::string &b64 = items[static_cast<std::size_t>(i)].second;
            std::vector<unsigned char> raw = base64_decode(b64);
            auto digest = hmac_sha256_bytes(hmac_key, raw);
            hashes[static_cast<std::size_t>(i)] = {name, hex_encode(digest.data(), digest.size())};
        }

        auto end = std::chrono::high_resolution_clock::now();
        double processing_time_s = std::chrono::duration<double>(end - start).count();

        std::ostringstream out;
        out << "{\"hashes\":{";
        for (std::size_t i = 0; i < hashes.size(); ++i) {
            if (i > 0) out << ',';
            out << '"' << json_escape(hashes[i].first) << '\"' << ':'
                << '"' << hashes[i].second << '"';
        }
        out << "},\"processing_time_s\":" << std::fixed << std::setprecision(9)
            << processing_time_s << "}";
        std::cout << out.str();
        return 0;
    } catch (const std::exception &ex) {
        std::cerr << "pdavs_hasher error: " << ex.what() << std::endl;
        return 1;
    }
}
