import sys
import os
import pickle
import json
from dotenv import load_dotenv
from regression_test import regression_test
from new_llm_optimize import llm_optimize, handle_compilation_error, handle_logic_error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from energy.src.measure_energy import get_evaluator_feedback
from energy.src.benchmark import Benchmark
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')


def master_script(optim_iter):
    for filename in os.listdir(f"{USER_PREFIX}/EEDC/llm/llm_input_files/input_code"):
        
        # Temporary to only run on binarytrees
        if filename != "binarytrees.gpp-9.c++":
            continue
        # if filename != "chameneosredux.gpp-5.c++":
        #     continue
        # if filename != "fannkuchredux.gpp-5.c++":
        #     continue
        # if filename != "knucleotide.gpp-3.c++":
        #     continue

            
        print(f"Optimizing {filename}, longest step")
        if llm_optimize(filename, optim_iter) != 0:
            print("Error in optimization, exiting script")
            return
        
        print(f"Running regression test on {filename}")
        regression_test_result = -3
        compilation_errors, output_errors, success = 0, 0, 0

        # Run llm optimization until successful regression test
        while True:
            regression_test_result = regression_test(f"llm/llm_input_files/input_code/{filename}", f"llm/benchmarks_out/{filename.split('.')[0]}/optimized_{filename}", filename.split('.')[0])
            
            # Compilation error in unoptimized file, exit script
            if regression_test_result == -2:
                print("Error in unoptimized file, exiting script")
                return

            # Compilation error in optimized file, re-prompt
            if regression_test_result == -1:
                if compilation_errors == 3:
                    print("Could not compile optimized file after 3 attempts, will re-optimize from original file")
                    llm_optimize(filename, optim_iter)
                    compilation_errors = 0
                    continue
                print("Error in optimized file, re-optimizing")
                handle_compilation_error(filename)
                compilation_errors += 1

            # Output difference in optimized file, re-prompt
            if regression_test_result == 0:
                print("Output difference in optimized file, calling handle_logic_error")
                if output_errors == 3:
                    print("Output differences after 3 attempts, will provide output differences to llm")
                    handle_logic_error(filename, True)
                elif output_errors > 3:
                    print("Still output differences after providing output differences to llm, will re-optimize from original file")
                    llm_optimize(filename, optim_iter)
                    output_errors = 0
                    continue
                handle_logic_error(filename, False)
                output_errors += 1
            
            # Success
            if regression_test_result == 1:
                success += 1
                print("Regression test successful")
                break
        
        
        print(f"{optim_iter}: passing code to measure energy and get evaluator feedback")
        get_evaluator_feedback(filename, optim_iter)
        print("got evaluator feedback")
        return


if __name__ == "__main__":

    #run for 5 iterations
    for optim_iter in range(0, 5):
        print(f"Optimized iteration {optim_iter}")
        master_script(optim_iter)

    #write result
    print("EEDC Optimization Complete, writing results to file.....")

    with open(f"{USER_PREFIX}/EEDC/energy/c++/benchmark_data.pkl", "rb") as file:
        contents = pickle.load(file)
    
    dict_str = json.dumps(contents, indent=4)
    with open("result_file.txt", "w+") as file:
        file.write(str(dict_str))