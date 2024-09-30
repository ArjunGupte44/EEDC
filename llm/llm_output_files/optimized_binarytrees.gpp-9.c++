```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <sstream>
#include <omp.h>
#include <algorithm>

const size_t LINE_SIZE = 64;

struct Node {
    std::shared_ptr<Node> l, r;

    int check() const {
        if (l)
            return l->check() + 1 + r->check();
        else return 1;
    }
};

std::shared_ptr<Node> make(int d) {
    auto root = std::make_shared<Node>();

    if(d > 0){
        root->l = make(d - 1);
        root->r = make(d - 1);
    }

    return root;
}

int main(int argc, char *argv[]) {
    int min_depth = 4;
    int max_depth = std::max(min_depth + 2, (argc == 2 ? atoi(argv[1]) : 10));
    int stretch_depth = max_depth + 1;

    // Alloc then dealloc stretchdepth tree
    {
        auto stretch_tree = make(stretch_depth);
        std::cout << "stretch tree of depth " << stretch_depth << "\t "
                  << "check: " << stretch_tree->check() << std::endl;
    }

    auto long_lived_tree = make(max_depth);
    std::vector<std::string> outputs(max_depth + 1); // store strings instead of ostringstream

    #pragma omp parallel for schedule(dynamic)
    for (int d = min_depth; d <= max_depth; d += 2) {
        int iterations = 1 << (max_depth - d + min_depth);
        int c = 0;

        for (int i = 1; i <= iterations; ++i) {
            auto a = make(d);
            c += a->check();
        }

        std::ostringstream oss;
        oss << iterations << "\t trees of depth " << d << "\t check: " << c << "\n";
        outputs[d] = oss.str(); // store the string representation
    }

    // print all results
    for (int d = min_depth; d <= max_depth; d += 2)
        std::cout << outputs[d];

    std::cout << "long lived tree of depth " << max_depth << "\t "
              << "check: " << (long_lived_tree->check()) << "\n";

    return 0;
}
```