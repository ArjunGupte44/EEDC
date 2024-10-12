#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <apr_pools.h>
#include <omp.h>

const size_t    LINE_SIZE = 64;

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
    
    int check() const 
    {
        if (l) {
            return l->check() + 1 + r->check();
        }
        else return 1;
    }
};

class NodePool
{
public:
    NodePool() 
    {
        apr_pool_create_unmanaged(&pool);
    }

    ~NodePool() 
    {
        apr_pool_destroy(pool);
    }

    Node* alloc()
    {
        return (Node *)apr_palloc(pool, sizeof(Node));
    }

    void clear() // Removed the threshold and apr_pool_num_bytes_alloc function
    {
        apr_pool_clear(pool);
    }

private:
    apr_pool_t* pool;
};

Node *make(int d, NodePool &store)
{
    Node* root = store.alloc();

    if(d > 0) {
        root->l = make(d - 1, store);
        root->r = make(d - 1, store);
    } else {
        root->l = root->r = nullptr;
    }

    return root;
}

int main(int argc, char *argv[]) 
{
    Apr apr;
    int min_depth = 4;
    int max_depth = std::max(min_depth + 2, (argc == 2 ? atoi(argv[1]) : 10));
    int stretch_depth = max_depth + 1;

    // Allocate then deallocate a stretch depth tree
    {
        NodePool store;
        Node *c = make(stretch_depth, store);
        std::cout << "stretch tree of depth " << stretch_depth << "\t "
                  << "check: " << c->check() << std::endl;
    }

    NodePool long_lived_store;
    Node *long_lived_tree = make(max_depth, long_lived_store);

    // Buffer to store output of each thread
    char *outputstr = (char*)malloc(LINE_SIZE * (max_depth + 1) * sizeof(char));

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

        sprintf(outputstr + LINE_SIZE * d, "%d\t trees of depth %d\t check: %d\n",
           iterations, d, c);
    }

    // Print all results
    for (int d = min_depth; d <= max_depth; d += 2) 
        printf("%s", outputstr + (d * LINE_SIZE));
    free(outputstr);

    std::cout << "long lived tree of depth " << max_depth << "\t "
              << "check: " << (long_lived_tree->check()) << "\n";

    return 0;
}