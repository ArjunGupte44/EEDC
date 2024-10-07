#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <omp.h>
#include <deque>

class Node {
public:
    Node* l = nullptr;
    Node* r = nullptr;

    int check() const {
        if (l)
            return l->check() + 1 + r->check();
        else return 1;
    }
};

class NodePool {
    std::deque<Node> pool;
public:
    Node* allocate() {
        pool.emplace_back();
        return &pool.back();
    }

    void clear() {
        pool.clear();
    }
};

Node* make(NodePool& pool, int d) {
    Node* root = pool.allocate();
    if (d > 0) {
        root->l = make(pool, d - 1);
        root->r = make(pool, d - 1);
    }
    return root;
}

int main(int argc, char *argv[]) {
    int min_depth = 4;
    int max_depth = std::max(min_depth+2, (argc == 2 ? std::atoi(argv[1]) : 10));
    int stretch_depth = max_depth + 1;

    // Stretch tree is not used further, no need to keep it allocated
    {
        NodePool pool;
        auto c = make(pool, stretch_depth);
        std::cout << "stretch tree of depth " << stretch_depth << "\t "
                  << "check: " << c->check() << std::endl;
    }

    NodePool long_lived_pool;
    auto long_lived_tree = make(long_lived_pool, max_depth);

    std::vector<std::string> output(max_depth + 1);

    #pragma omp parallel for schedule(dynamic) ordered
    for (int d = min_depth; d <= max_depth; d += 2) {
        int iterations = 1 << (max_depth - d + min_depth);
        int c = 0;

        for (int i = 1; i <= iterations; ++i) {
            NodePool pool;
            auto a = make(pool, d);
            c += a->check();
        }

        std::stringstream ss;
        ss << iterations << "\t trees of depth " << d << "\t check: " << c << std::endl;
        #pragma omp ordered
        output[d] = ss.str();
    }

    for (const auto &str : output) {
        if (!str.empty()) {
            std::cout << str;
        }
    }
    
    std::cout << "long lived tree of depth " << max_depth << "\t "
              << "check: " << (long_lived_tree->check()) << std::endl;
    return 0;
}
