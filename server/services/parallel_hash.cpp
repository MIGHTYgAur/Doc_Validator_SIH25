#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <iomanip>
#include <openssl/sha.h>
#include <omp.h>

std::string sha256(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) return "ERROR: Cannot open file";

    SHA256_CTX ctx;
    SHA256_Init(&ctx);

    const size_t bufferSize = 1 << 12;
    char buffer[bufferSize];

    while (file.good()) {
        file.read(buffer, bufferSize);
        SHA256_Update(&ctx, buffer, file.gcount());
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_Final(hash, &ctx);

    std::stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];

    return ss.str();
}

int main() {
    std::vector<std::string> files = {
        "doc1.pdf", "doc2.pdf", "doc3.pdf", "doc4.pdf"
    };
    std::vector<std::string> results(files.size());

    double start = omp_get_wtime();

    #pragma omp parallel for
    for (int i = 0; i < files.size(); ++i) {
        results[i] = sha256(files[i]);
        #pragma omp critical
        std::cout << "Thread " << omp_get_thread_num() 
                  << " hashed: " << files[i] << std::endl;
    }

    double end = omp_get_wtime();

    std::cout << "\n--- Hash Results ---\n";
    for (int i = 0; i < results.size(); ++i)
        std::cout << files[i] << " -> " << results[i] << "\n";

    std::cout << "\nTotal Time: " << (end - start) << " seconds\n";
    return 0;
}
