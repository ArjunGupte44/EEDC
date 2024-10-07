#include <iostream>
#include <vector>
#include <stack>
#include <utility>
#include <omp.h>

const size_t LINE_SIZE = 64;

struct Node {
    Node *l = nullptr, *r = nullptr;
    int check() const {
        if (l == nullptr && r == nullptr) return 1;  // Early check if leaf
        int total = 1;
        std::stack<const Node*> toVisit;
        if (l) toVisit.push(l);
        if (r) toVisit.push(r);
        while (!toVisit.empty()) {
            const Node* current = toVisit.top();
            toVisit.pop();
            ++total;
            if (current->l) toVisit.push(current->l);
            if (current->r) toVisit.push(current->r);
        }
        return total;
    }
};

class NodePool {
public:
    NodePool(size_t initialSize) {
        nodes.resize(initialSize);
        clear();
    }

    Node* alloc() {
        if (index < nodes.size()) {
            return &nodes[index++];
        }
        return nullptr;
    }

    void clear() {
        index = 0;
        for (Node& node : nodes) {
            node.l = nullptr;
            node.r = nullptr;
        }
    }

private:
    std::vector<Node> nodes;
    size_t index = 0;
};

Node* make_iterative(int depth, NodePool& store) {
    if (depth <= 0) return nullptr;

    Node* root = store.alloc();
    std::stack<std::pair<Node*, int>> nodeStack;
    nodeStack.push(std::make_pair(root, depth));

    while (!nodeStack.empty()) {
        auto topPair = nodeStack.top();
        Node* node = topPair.first;
        int currentDepth = topPair.second;
        nodeStack.pop();

        if (currentDepth > 1) {
            Node* l = store.alloc();
            Node* r = store.alloc();
            if (l) node->l = l;
            if (r) node->r = r;

            if (node->l) nodeStack.push(std::make_pair(node->l, currentDepth - 1));
            if (node->r) nodeStack.push(std::make_pair(node->r, currentDepth - 1));
        }
    }

    return root;
}

int main(int argc, char *argv[]) {
    int min_depth = 4;
    int max_depth = 10;
    if (argc == 2) {
        max_depth = atoi(argv[1]);
    }
    int stretch_depth = max_depth + 1;

    #pragma omp parallel sections
    {
        #pragma omp section
        {
            NodePool store(1 << (stretch_depth + 1));
            Node* c = make_iterative(stretch_depth, store);
            if (c) std::cout << "stretch tree of depth " << stretch_depth << "\t " << "check: " << c->check() << std::endl;
        }
    }

    NodePool long_lived_store(1 << (max_depth + 1));
    Node* long_lived_tree = make_iterative(max_depth, long_lived_store);

    std::vector<std::string> outputLines((max_depth - min_depth) / 2 + 1);

    #pragma omp parallel for schedule(guided, 1) shared(outputLines)
    for (int d = min_depth; d <= max_depth; d += 2) {
        int iterations = 1 << (max_depth - d + min_depth);
        int c = 0;

        NodePool store(iterations * (1 << (d - 1)));

        for (int i = 1; i <= iterations; ++i) {
            Node* a = make_iterative(d, store);
            if (a) {
                c += a->check();
            }
            store.clear();
        }

        char buffer[LINE_SIZE];
        snprintf(buffer, LINE_SIZE, "%d\t trees of depth %d\t check: %d\n",
                 iterations, d, c);
        outputLines[(d - min_depth) / 2] = buffer;
    }

    for (const auto& line : outputLines) {
        printf("%s", line.c_str());
    }

    if (long_lived_tree) {
        std::cout << "long lived tree of depth " << max_depth << "\t "
                  << "check: " << long_lived_tree->check() << "\n";
    }

    return 0;
}
