#include <iostream>
#include <cmath>
#include <vector>
#include <omp.h>
#include <cstring> // Include cstring for memcpy

int64_t factorial(int n) {
    static int64_t fact[20] = {0};
    if (fact[n] != 0) return fact[n];
    if (n <= 1) return fact[n] = 1;
    return fact[n] = n * factorial(n - 1);
}

class Permutation {
public:
    Permutation(int n, int64_t start);
    void advance();
    int64_t countFlips() const;
private:
    int* count;
    int8_t* current;
    int size;
};

Permutation::Permutation(int n, int64_t start) : size(n) {
    count = new int[n];
    current = new int8_t[n];
    for (int i = 0; i < n; ++i) {
        count[i] = 0;
        current[i] = i;
    }
    for (int i = n - 1; i >= 0; --i) {
        int64_t f = factorial(i);
        int d = start / f;
        start %= f;
        count[i] = d;
        for (int j = 0; j < d; ++j) {
            int8_t tmp = current[j];
            for (int k = j; k < i; ++k) {
                current[k] = current[k + 1];
            }
            current[i] = tmp;
        }
    }
}

void Permutation::advance() {
    for (int i = 1;; ++i) {
        int first = current[0];
        for (int j = 0; j < i; ++j) {
            current[j] = current[j + 1];
        }
        current[i] = first;
        if (++count[i] <= i) break;
        count[i] = 0;
    }
}

int64_t Permutation::countFlips() const {
    int flips = 0;
    int8_t* temp = new int8_t[size];
    memcpy(temp, current, size * sizeof(int8_t)); // Copy the array
    while (temp[0] != 0) {
        ++flips;
        int first = temp[0];
        for (int i = 0, j = first; i < j; ++i, --j) {
            std::swap(temp[i], temp[j]);
        }
    }
    delete[] temp;
    return flips;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Please provide an integer n as an argument." << std::endl;
        return 1;
    }
    
    int n = std::atoi(argv[1]);
    int64_t totalPermutations = factorial(n);
    int blockCount = 24;
    if (blockCount > totalPermutations) blockCount = 1;
    int64_t blockLength = totalPermutations / blockCount;
    
    int64_t maxFlips = 0, checksum = 0;
    
    #pragma omp parallel for schedule(static) reduction(max:maxFlips) reduction(+:checksum)
    for (int64_t blockStart = 0; blockStart < totalPermutations; blockStart += blockLength) {
        Permutation permutation(n, blockStart);
        for (int64_t index = 0; index < blockLength; ++index) {
            const int flips = permutation.countFlips();
            checksum += (index % 2 == 0) ? flips : -flips;
            if (flips > maxFlips) maxFlips = flips;
            permutation.advance();
        }
    }
    std::cout << checksum << std::endl;
    std::cout << "Pfannkuchen(" << n << ") = " << maxFlips << std::endl;

    return 0;
}