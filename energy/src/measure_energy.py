from benchmark import Benchmark
import pickle

USER_PREFIX = "/home/arjun/VIP_PTM/"

language = "C++"
name = "binary-trees"
original_code_path = f"{USER_PREFIX}EEDC/energy/src/binarytrees.gpp-9.c++"
optimized_code_path = f"{USER_PREFIX}EEDC/energy/src/binarytrees.gpp-9.c++"
executable = "./binarytrees.gpp-9.gpp_run"
args = "21"

bmark = Benchmark(language, name)

for optim_iter in range(2):
    results_file = bmark.run(executable, args)
    bmark.process_results(results_file, optim_iter, original_code_path if optim_iter == 0 else optimized_code_path)


#Verify pickle file has the benchmark data dict stored correctly (source code, avg energy, avg runtime)
with open(f"{USER_PREFIX}EEDC/energy/{language}/benchmark_data.pkl", "rb") as file:
    contents = pickle.load(file)

#Uncomment the line below to see the benchmark data dict printed out
# print(contents)