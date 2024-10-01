```cpp
#include <iostream>
#include <omp.h>
#include <memory>

class Node {
public:
    std::shared_ptr<Node> l = nullptr;
    std::shared_ptr<Node> r = nullptr;

    int check() const {
        if (l) return l->check() + 1 + r->check();
        else return 1;
    }
};

std::shared_ptr<Node> make(int d) {
    if (d > 0) {
        auto node = std::make_shared<Node>();
        node->l = make(d-1);
        node->r = make(d-1);
        return node;
    } else {
        return std::make_shared<Node>();
    }
}

int main() {
    const int min_depth = 4;
    const int max_depth = 10;
   
    // Stretch tree
    {
        auto stretch_tree = make(max_depth + 1);
        std::cout << "Stretch tree of depth " << max_depth + 1 << "\t check: " << stretch_tree->check() << std::endl;
    }

    std::shared_ptr<Node> long_lived_tree = make(max_depth);

    #pragma omp parallel for
    for (int d = min_depth; d <= max_depth; d += 2) {
        int iterations = 1 << (max_depth - d + min_depth);
        int check_sum = 0; // Change c to a thread-local variable

        for (int i = 0; i < iterations; ++i) {
            check_sum += make(d)->check();
        }

        // Use a critical section to ensure the output is not jumbled.
        #pragma omp critical 
        {
            std::cout << iterations << "\t trees of depth " << d << "\t check: " << check_sum << "\n";
        }
    }

    std::cout << "Long-lived tree of depth " << max_depth << "\t check: " << long_lived_tree->check() << "\n";

    return 0;
}
```