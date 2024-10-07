#include <iostream>
#include <vector>
#include <string>
#include <omp.h>
#include <sstream>
#include <queue>

class Node {
public:
    Node *l, *r;

    Node() : l(nullptr), r(nullptr) {}

    int check() const {
        int count = 0;
        std::vector<const Node*> stack;
        stack.push_back(this);
        while (!stack.empty()) {
            const Node* current = stack.back();
            stack.pop_back();
            ++count;
            if (current->l) stack.push_back(current->l);
            if (current->r) stack.push_back(current->r);
        }
        return count;
    }
};

class NodePool {
public:
    std::vector<Node> pool;
    size_t index;

    NodePool(size_t capacity) : pool(capacity), index(0) {}

    Node* alloc() {
        if (index < pool.size()) {
            return &pool[index++];
        }
        return nullptr;
    }

    void clear() {
        index = 0;
    }
};

Node* make(int depth, NodePool& store) {
    if (depth <= 0) return nullptr;
    std::queue<std::pair<Node*, int>> queue;
    Node* root = store.alloc();
    if (!root) return nullptr;
    queue.push({root, depth});

    while (!queue.empty()) {
        auto [node, d] = queue.front();
        queue.pop();
        if (d > 0) {
            node->l = store.alloc();
            node->r = store.alloc();
            if (node->l) queue.push({node->l, d - 1});
            if (node->r) queue.push({node->r, d - 1});
        }
    }
    return root;
}

int main(int argc, char* argv[]) 
{
    int min_depth = 4;
    int max_depth = std::max(min_depth + 2, (argc == 2 ? std::atoi(argv[1]) : 10));

    {
        NodePool stretch_pool(1 << (max_depth + 2));
        Node* stretch_tree = make(max_depth + 1, stretch_pool);
        std::cout << "stretch tree of depth " << (max_depth + 1) << "\t check: " 
                  << (stretch_tree ? stretch_tree->check() : 0) << std::endl;
    }

    std::vector<std::string> outputs((max_depth / 2) + 1);
    NodePool long_lived_store(1 << (max_depth + 1));
    Node *long_lived_tree = make(max_depth, long_lived_store);

    for (int d = min_depth; d <= max_depth; d += 2) {
        int iterations = 1 << (max_depth - d + min_depth);
        int total_check = 0;

        #pragma omp parallel reduction(+:total_check)
        {
            NodePool store(1 << (d + 1));
            #pragma omp for schedule(static)
            for (int i = 0; i < iterations; ++i) {
                Node *a = make(d, store);
                if (a) total_check += a->check();
                store.clear();
            }
        }

        std::ostringstream oss;
        oss << iterations << "\t trees of depth " << d << "\t check: " << total_check << '\n';
        outputs[(d - min_depth) / 2] = oss.str();
    }

    for (const auto& output : outputs)
        std::cout << output;

    std::cout << "long lived tree of depth " << max_depth << "\t " 
              << "check: " << (long_lived_tree ? long_lived_tree->check() : 0) << std::endl;

    return 0;
}