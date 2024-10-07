#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint> // for int64_t
#include <omp.h>

using namespace std;

// Use local variable for factorial to prevent unnecessary static allocation overhead
void initializeFact(int n, int64_t fact[])
{
    fact[0] = 1;
    for (int i = 1; i <= n; ++i)
        fact[i] = i * fact[i - 1];
}

class Permutation {
  public:
    Permutation(int n, int64_t start, int64_t fact[]);
    void advance();
    int64_t countFlips() const;

  private:
    vector<int> count;
    vector<int8_t> current;
};

// Initialize the current value of a permutation
// and the cycle count values used to advance.
Permutation::Permutation(int n, int64_t start, int64_t fact[])
{
    count.resize(n);
    current.resize(n);

    // Initialize count
    for (int i = n - 1; i >= 0; --i)
    {
        int d = start / fact[i];
        start = start % fact[i];
        count[i] = d;
    }

    // Initialize current.
    for (int i = 0; i < n; ++i)
        current[i] = i;

    for (int i = n - 1; i >= 0; --i)
    {
        int d = count[i];
        auto b = current.begin();
        rotate(b, b + d, b + i + 1);
    }
}

// Advance the current permutation to the next in sequence.
void Permutation::advance()
{
    for (int i = 1; ;++i)
    {
        // Tried using std::rotate here but that was slower.
        auto first = current[0];
        for (int j = 0; j < i; ++j)
            current[j] = current[j + 1];
        current[i] = first;

        ++(count[i]);
        if (count[i] <= i)
            break;
        count[i] = 0;
    }
}

// Count the flips required to flip 0 to the front of the vector.
inline int64_t Permutation::countFlips() const
{
    const int n = current.size();
    int64_t flips = 0;
    auto first = current[0];
    if (first > 0)
    {
        flips = 1;

        vector<int8_t> temp(current.begin(), current.end());

        // Flip temp until the element at the first index is 0
        while (temp[first] > 0) {
            ++flips;
            const int8_t newFirst = temp[first];
            temp[first] = first;
            int64_t low = 1, high = first - 1;
            while(low < high) {
                swap(temp[low], temp[high]);
                ++low;
                --high;
            }
            first = newFirst;
        }
    }
    return flips;
}

int main(int argc, char **argv)
{
    const int n = atoi(argv[1]);

    // Compute some factorials for later use.
    int64_t fact[32];
    initializeFact(n, fact);

    // blockCount works best if it is set to a multiple of the number
    // of CPUs

    int blockCount = 24;
    if (blockCount > fact[n])
        blockCount = 1;
    const int64_t blockLength = fact[n] / blockCount;

    int64_t maxFlips = 0, checksum = 0;

    // Iterate over each block.
    #pragma omp parallel for \
        reduction(max:maxFlips) \
        reduction(+:checksum)

    for (int64_t blockStart = 0;
         blockStart < fact[n]; 
         blockStart += blockLength)
    {
        // first permutation for this block.
        Permutation permutation(n, blockStart, fact);

        // Iterate over each permutation in the block.
        auto index = blockStart;
        while (index < blockStart + blockLength)
        {
            const int64_t flips = permutation.countFlips();

            if (flips) {
                if (index % 2 == 0)
                    checksum += flips;
                else
                    checksum -= flips;

                if (flips > maxFlips)
                    maxFlips = flips;
            }

            ++index;

            // next permutation for this block.
            permutation.advance();
        }
    }

    // Output the results to stdout.
    cout << checksum << endl;
    cout << "Pfannkuchen(" << n << ") = " << maxFlips << endl;

    return 0;
}