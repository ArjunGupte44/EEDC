#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <omp.h>

struct Node {
    Node *l, *r;

    int check() const {
        int count = 1;
        if (l) count += l->check();
        if (r) count += r->check();
        return count;
    }
};

class NodePool {
public:
    NodePool(size_t max_nodes) : max_nodes(max_nodes), index(0) {
        storage.reserve(max_nodes);
    }

    Node* allocate_node() {
        if (index >= max_nodes) {
            throw std::bad_alloc();
        }
        if (index >= storage.size()) {
            storage.push_back(Node{nullptr, nullptr});
        }
        return &storage[index++];
    }

    void reset() { index = 0; }

private:
    std::vector<Node> storage;
    size_t max_nodes;
    size_t index;
};

Node* make_tree(int d, NodePool &pool) {
    if (d <= 0) {
        return nullptr;
    }

    Node *root = pool.allocate_node();
    root->l = make_tree(d - 1, pool);
    root->r = make_tree(d - 1, pool);
    return root;
}

int main(int argc, char *argv[]) {
    const int min_depth = 4;
    const int max_depth = std::max(min_depth + 2, (argc == 2 ? std::atoi(argv[1]) : 10));
    const int stretch_depth = max_depth + 1;

    {
        size_t node_count = (1 << (stretch_depth + 1)) - 1;
        NodePool stretch_pool(node_count);

        Node *stretch_tree = make_tree(stretch_depth, stretch_pool);
        std::cout << "stretch tree of depth " << stretch_depth << "\t check: " << stretch_tree->check() << std::endl;
    }

    NodePool long_lived_pool((1 << (max_depth + 1)) - 1);
    Node *long_lived_tree = make_tree(max_depth, long_lived_pool);
    
    std::vector<std::string> outputs((max_depth / 2) + 1);
    
    #pragma omp parallel for
    for (int d = min_depth; d <= max_depth; d += 2) {
        int c = 0;
        int iterations = 1 << (max_depth - d + min_depth);
        size_t local_node_count = (1 << (d + 1)) - 1;
        
        NodePool local_pool(local_node_count);
        for (int i = 0; i < iterations; ++i) {
            Node *a = make_tree(d, local_pool);
            c += a->check();
            local_pool.reset();
        }

        std::ostringstream os;
        os << iterations << "\ttrees of depth " << d << "\tcheck: " << c << "\n";
        outputs[(d - min_depth) / 2] = os.str();
    }

    for (const auto &output : outputs) {
        std::cout << output;
    }

    std::cout << "long lived tree of depth " << max_depth << "\t check: " << long_lived_tree->check() << "\n";

    return 0;
}