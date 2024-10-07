from .benchmark import Benchmark
from .evaluator import evaluator_llm
import pickle
import os

def load_benchmark_data(filepath):
    with open(filepath, "rb") as file:
        contents = pickle.load(file)
    return contents

def extract_content(contents):
    # Convert keys to a sorted list to access the first and last elements
    keys = list(contents.keys())

    #print all values
    # for key, (source_code, avg_energy, avg_runtime) in contents.items():
    #     print("key:", key)
    #     print("avg_energy:", avg_energy)
    #     print("avg_runtime:", avg_runtime)
    # print("\n")

    # Extract the first(original) and last(current) elements
    first_key = keys[0]
    last_key = keys[-1]

    first_value = contents[first_key]
    last_value = contents[last_key]


    # Loop through the contents to find the key with the lowest avg_energy
    min_avg_energy = float('inf')
    min_energy_key = None
    for key, (source_code, avg_energy, avg_runtime) in contents.items():
        if avg_energy < min_avg_energy:
            min_avg_energy = avg_energy
            min_energy_key = key

    min_value = contents[min_energy_key]

    # Prepare results in a structured format (dictionary)
    benchmark_info = {
        "original": {
            "source_code": first_value[0],
            "avg_energy": first_value[1],
            "avg_runtime": first_value[2]
        },
        "lowest_avg_energy": {
            "source_code": min_value[0],
            "avg_energy": min_value[1],
            "avg_runtime": min_value[2]
        },
        "current": {
            "source_code": last_value[0],
            "avg_energy": last_value[1],
            "avg_runtime": last_value[2]
        }
    }
    
    return benchmark_info

def print_benchmark_info(benchmark_info):
    """Prints the benchmark information in a structured format."""
    print("Original:")
    # Uncomment to print source code
    # print("Source Code:", benchmark_info["original"]["source_code"])
    print("Average Energy:", benchmark_info["original"]["avg_energy"])
    print("Average Runtime:", benchmark_info["original"]["avg_runtime"])
    print("\n")

    print("Lowest Average Energy:")
    # Uncomment to print source code
    # print("Source Code:", benchmark_info["lowest_avg_energy"]["source_code"])
    print("Average Energy:", benchmark_info["lowest_avg_energy"]["avg_energy"])
    print("Average Runtime:", benchmark_info["lowest_avg_energy"]["avg_runtime"])
    print("\n")

    print("Current:")
    # Uncomment to print source code
    # print("Source Code:", benchmark_info["current"]["source_code"])
    print("Average Energy:", benchmark_info["current"]["avg_energy"])
    print("Average Runtime:", benchmark_info["current"]["avg_runtime"])
    print("\n")


def get_evaluator_feedback(filename):
    # filename = binarytrees.gpp-9.c++
    USER_PREFIX = os.path.join(os.path.dirname(__file__), f"../../")
    language = filename.split(".")[-1]
    name = filename.split(".")[0]
    original_code_path = f"{USER_PREFIX}llm/llm_input_files/input_code/{filename}"
    optimized_code_path = f"{USER_PREFIX}llm/llm_output_files/optimized_{filename}"

    # Assuming regression test created a optimized executable
    executable = f"{USER_PREFIX}llm/output_files/optimized_{filename.split('.')[0]}"

    # Needs to be changed for other benchmarks
    args = "21"
    pkl_path = os.path.join(os.path.dirname(__file__), f"../../energy/{language}/benchmark_data.pkl")

    bmark = Benchmark(language, name)

    #run benchmark
    results_file = bmark.run(executable, args)
    bmark.process_results(results_file, optimized_code_path)

    # Load benchmark data
    contents = load_benchmark_data(pkl_path)
    
    # Find the required benchmark elements
    benchmark_info = extract_content(contents)
    
    # Print the benchmark information
    print_benchmark_info(benchmark_info)

    #run evaluator
    evaluator_feedback = evaluator_llm(benchmark_info)
    # print(evaluator_feedback)
    
    return benchmark_info

if __name__ == "__main__":
    get_evaluator_feedback("", "", "", "", "", "")