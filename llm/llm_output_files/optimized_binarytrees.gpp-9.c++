#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <apr_pools.h>
#include <vector>

const size_t LINE_SIZE = 64;

class Apr
{
public:
    Apr() 
    {
        apr_initialize();
    }

    ~Apr() 
    {
        apr_terminate();
    }
};

struct Node 
{
    Node *l, *r;
    Node() : l(nullptr), r(nullptr) {}
    int check() const 
    {
        return (l ? l->check() : 0) + 1 + (r ? r->check() : 0);
    }
};

class NodePool
{
public:
    NodePool() 
    {
        apr_pool_create_unmanaged(&pool);
        prealloc(); // Pre-allocate for better locality if depth is known.
    }

    ~NodePool() 
    {
        apr_pool_destroy(pool);
    }

    Node* alloc()
    {
        if(free_nodes.empty()){
            return (Node *)apr_palloc(pool, sizeof(Node));
        }else{
            Node* n = free_nodes.back();
            free_nodes.pop_back();
            return n;
        }
    }

    void clear()
    {
        for(Node* n : used_nodes) {
            free_nodes.push_back(n);
        }
        used_nodes.clear();
    }

private:
    apr_pool_t* pool;
    std::vector<Node*> free_nodes, used_nodes;
    void prealloc() {
        // Allocate, for simplicity demo.
        for(size_t i = 0; i < 1024; ++i) // arbitrary preallocation
            free_nodes.push_back((Node *)apr_palloc(pool, sizeof(Node)));
    }
};

Node *make(int d, NodePool &store)
{
    Node* root = store.alloc();
    if(d>0){
        root->l=make(d-1, store);
        root->r=make(d-1, store);
    }
    return root;
}

int main(int argc, char *argv[]) 
{
    Apr apr;
    int min_depth = 4;
    int max_depth = std::max(min_depth+2, (argc == 2 ? atoi(argv[1]) : 10));
    int stretch_depth = max_depth+1;

    // Alloc then dealloc stretchdepth tree
    {
        NodePool store;
        Node *c = make(stretch_depth, store);
        std::cout << "stretch tree of depth " << stretch_depth << "\t "
                  << "check: " << c->check() << std::endl;
    }

    NodePool long_lived_store;
    Node *long_lived_tree = make(max_depth, long_lived_store);

    std::vector<char> outputstr(LINE_SIZE * (max_depth + 1));

    #pragma omp parallel for 
    for (int d = min_depth; d <= max_depth; d += 2) 
    {
        int iterations = 1 << (max_depth - d + min_depth);
        int c = 0;

        NodePool store;

        for (int i = 1; i <= iterations; ++i) 
        {
            Node *a = make(d, store);
            c += a->check();
            store.clear();
        }

        sprintf(&outputstr[LINE_SIZE * d], "%d\t trees of depth %d\t check: %d\n", iterations, d, c);
    }

    for (int d = min_depth; d <= max_depth; d += 2) 
        printf("%s", &outputstr[d * LINE_SIZE] );

    std::cout << "long lived tree of depth " << max_depth << "\t "
              << "check: " << (long_lived_tree->check()) << "\n";

    return 0;
}