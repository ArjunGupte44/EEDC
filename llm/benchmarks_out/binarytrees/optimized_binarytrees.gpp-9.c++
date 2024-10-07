#include <iostream>
#include <vector>
#include <thread>
#include <mutex>
#include <cstring> // for memset

const size_t LINE_SIZE = 64;

struct Node 
{
    Node *l, *r;
    int check() const 
    {
        if (l) return l->check() + 1 + r->check();
        else return 1;
    }
};

class OptimizedNodePool 
{
public:
    Node* alloc()
    {
        nodes.emplace_back(Node());
        return &nodes.back();
    }
    void clear() { nodes.clear(); }
private:
    std::vector<Node> nodes;
};

Node* make(int d, OptimizedNodePool &store)
{
    Node* root = store.alloc();
    if(d>0)
    {
        root->l=make(d-1, store);
        root->r=make(d-1, store);
    }
    else
    {
        root->l=root->r=0;
    }
    return root;
}

void worker(int d, int iterations, std::vector<std::string> &outputstrs, int min_depth, std::mutex &mtx)
{
    int c = 0;
    for (int i = 1; i <= iterations; ++i) 
    {
        OptimizedNodePool store;
        Node *a = make(d, store);
        c += a->check();
        store.clear();
    }
    char buffer[LINE_SIZE];
    snprintf(buffer, LINE_SIZE, "%d\t trees of depth %d\t check: %d\n", iterations, d, c);
    std::lock_guard<std::mutex> lock(mtx);
    outputstrs[(d-min_depth)/2] = buffer;
}

int main(int argc, char *argv[]) 
{
    int min_depth = 4;
    int max_depth = std::max(min_depth+2, (argc == 2 ? atoi(argv[1]) : 10));
    int stretch_depth = max_depth+1;

    { // Inner block scope to automatically call destructors
        OptimizedNodePool store;
        Node *c = make(stretch_depth, store);
        std::cout << "stretch tree of depth " << stretch_depth << "\t check: " << c->check() << std::endl;
    }

    OptimizedNodePool long_lived_store;
    Node *long_lived_tree = make(max_depth, long_lived_store);

    std::vector<std::string> outputstrs(max_depth/2 + 1);
    std::vector<std::thread> threads;
    std::mutex mtx;

    for (int d = min_depth; d <= max_depth; d += 2) 
    {
        int iterations = 1 << (max_depth - d + min_depth);
        threads.emplace_back(worker, d, iterations, std::ref(outputstrs), min_depth, std::ref(mtx));
    }

    for(auto& thread : threads) {
        thread.join();
    }

    for (const auto& result : outputstrs) {
        printf("%s", result.c_str());
    }

    std::cout << "long lived tree of depth " << max_depth << "\t check: " << (long_lived_tree->check()) << "\n";

    return 0;
}