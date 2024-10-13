#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <apr_pools.h>
#include <omp.h>
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

    void clear()
    {
        apr_pool_clear(pool);
    }

private:
    apr_pool_t* pool;
};

Node* make_tree(int depth, NodePool &store)
{
    Node* root = store.alloc();

    if(depth > 0){
        root->l = make_tree(depth - 1, store);
        root->r = make_tree(depth - 1, store);
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

    // Stretch depth tree for allocation
    {
        NodePool store;
        Node *stretch_tree = make_tree(stretch_depth, store);
        std::cout << "stretch tree of depth " << stretch_depth << "\t "
                  << "check: " << stretch_tree->check() << std::endl;
    }

    NodePool long_lived_pool;
    Node *long_lived_tree = make_tree(max_depth, long_lived_pool);

    // Buffer to store output of each thread
    char *output_buffer = (char*)malloc(LINE_SIZE * (max_depth + 1) * sizeof(char));

    #pragma omp parallel for
    for (int d = min_depth; d <= max_depth; d += 2) 
    {
        int iterations = 1 << (max_depth - d + min_depth);
        int check_result = 0;
        
        // Ensure each thread has its memory pool
        NodePool local_store;

        for (int i = 1; i <= iterations; ++i) 
        {
            Node *tree = make_tree(d, local_store);
            check_result += tree->check();
            local_store.clear();
        }

        // Each thread separately handles its own buffer section
        snprintf(output_buffer + LINE_SIZE * d, LINE_SIZE, "%d\t trees of depth %d\t check: %d\n", iterations, d, check_result);
    }

    // Print all results
    for (int d = min_depth; d <= max_depth; d += 2) 
        printf("%s", output_buffer + (d * LINE_SIZE));
    free(output_buffer);

    std::cout << "long lived tree of depth " << max_depth << "\t "
              << "check: " << (long_lived_tree->check()) << "\n";

    return 0;
}