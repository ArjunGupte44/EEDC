#include <iostream>
#include <vector>
#include <algorithm>
#include <omp.h>

class Node 
{
public:
    Node *l, *r;
    int check() const 
    {
        if (l)
            return l->check() + 1 + r->check();
        else return 1;
    }
};

class NodePool
{
public:
    NodePool(size_t reserve_size)
    {
        nodes.reserve(reserve_size);
    }

    Node* alloc()
    {
        nodes.emplace_back();
        return &nodes.back();
    }

    void clear()
    {
        nodes.clear();
    }

private:
    std::vector<Node> nodes;
};

Node *make(int d, NodePool &store)
{
    Node* root = store.alloc();

    if(d>0){
        root->l = make(d-1, store);
        root->r = make(d-1, store);
    }else{
        root->l = root->r = nullptr;
    }

    return root;
}

int main(int argc, char *argv[]) 
{
    const int LINE_SIZE = 50;
    int min_depth = 4;
    int max_depth = std::max(min_depth+2, (argc == 2 ? atoi(argv[1]) : 10));
    int stretch_depth = max_depth+1;

    // Alloc then dealloc stretchdepth tree
    {
        NodePool store((1 << (stretch_depth + 1)) - 1);
        Node* c = make(stretch_depth, store);
        std::cout << "stretch tree of depth " << stretch_depth << "\t "
                  << "check: " << c->check() << std::endl;
    }

    NodePool long_lived_store((1 << (max_depth + 1)) - 1);
    Node* long_lived_tree = make(max_depth, long_lived_store);

    // buffer to store output of each thread
    std::vector<char> outputstr(LINE_SIZE * (max_depth +1));

    #pragma omp parallel for 
    for (int d = min_depth; d <= max_depth; d += 2) 
    {
        int iterations = 1 << (max_depth - d + min_depth);
        int c = 0;

        // Reserve the needed number of nodes in advance
        NodePool store((1 << (d + 1)) - 1);

        for (int i = 1; i <= iterations; ++i) 
        {
            Node *a = make(d, store);
            c += a->check();
            store.clear();
        }

        sprintf(outputstr.data() + LINE_SIZE * d, "%d\t trees of depth %d\t check: %d\n",
           iterations, d, c);
    }

    // print all results
    for (int d = min_depth; d <= max_depth; d += 2) 
        printf("%s", outputstr.data() + (d * LINE_SIZE));

    std::cout << "long lived tree of depth " << max_depth << "\t "
              << "check: " << (long_lived_tree->check()) << "\n";

    return 0;
}
