#include <iostream>
#include <vector>
#include <omp.h>

class Node {
public:
    Node* left = nullptr;
    Node* right = nullptr;

    int check() const {
        // Traversing recursively to count all nodes
        int node_count = 1; // Include self
        if (left) node_count += left->check();
        if (right) node_count += right->check();
        return node_count;
    }
};

class NodePool {
public:
    Node* alloc() {
        if (!nodes_.empty()) {
            Node* node = nodes_.back();
            nodes_.pop_back();
            return node;
        }
        Node* node = new Node();
        allocated_.push_back(node);
        return node;
    }

    void recycle(Node* node) {
        if (node == nullptr) return;
        node->left = nullptr;
        node->right = nullptr;
        nodes_.push_back(node);
    }

    ~NodePool() {
        for (Node* node : allocated_) {
            delete node;
        }
    }

private:
    std::vector<Node*> nodes_; // Recycled nodes
    std::vector<Node*> allocated_; // All allocated nodes
};

Node* makeTree(int depth, NodePool& pool) {
    if (depth <= 0) return nullptr;
    Node* node = pool.alloc();
    node->left = makeTree(depth - 1, pool);
    node->right = makeTree(depth - 1, pool);
    return node;
}

void freeTree(Node* node, NodePool& pool) {
    if (node == nullptr) return;
    freeTree(node->left, pool);
    freeTree(node->right, pool);
    pool.recycle(node);
}

int main(int argc, char *argv[]) {
    int min_depth = 4;
    int max_depth = (argc == 2 ? std::max(min_depth + 2, atoi(argv[1])) : 10);
    int stretch_depth = max_depth + 1;

    {
        NodePool temporaryPool;
        Node* c = makeTree(stretch_depth, temporaryPool);
        std::cout << "stretch tree of depth " << stretch_depth << "\t"
                  << "check: " << c->check() << std::endl;
        freeTree(c, temporaryPool);
    }

    NodePool longTermPool;
    Node* longLivedTree = makeTree(max_depth, longTermPool);

    #pragma omp parallel for schedule(dynamic,1)
    for (int d = min_depth; d <= max_depth; d += 2) {
        int iterations = 1 << (max_depth - d + min_depth);
        int local_check_sum = 0; // Local to each thread

        NodePool pool;

        for (int i = 0; i < iterations; ++i) {
            Node* a = makeTree(d, pool);
            local_check_sum += a->check();
            freeTree(a, pool);
        }

        #pragma omp critical
        {
            // Correctly accumulate thread-local results to global output
            std::cout << iterations << "\t trees of depth " << d 
                      << "\t check: " << local_check_sum << std::endl;
        }
    }

    std::cout << "long lived tree of depth " << max_depth << "\t check: "
              << longLivedTree->check() << "\n";
    freeTree(longLivedTree, longTermPool);

    return 0;
}