import sys
import os
from regression_test import regression_test
from new_llm_optimize import llm_optimize, handle_compilation_error, handle_logic_error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from energy.src.measure_energy import get_evaluator_feedback
from energy.src.benchmark import Benchmark

def master_script(iter=0):
    for filename in os.listdir("llm/llm_input_files/input_code"):
        
        # Temporary to only run on binarytrees
        if filename != "binarytrees.gpp-9.c++":
            continue

        print(f"Optimizing {filename}, longest step")
        if llm_optimize(filename) != 0:
            print("Error in optimization, exiting script")
            return
        
        print(f"Running regression test on {filename}")
        regression_test_result = -3
        compilation_errors, output_errors = 0, 0
        while regression_test_result != 1:
            regression_test_result = regression_test("llm/llm_input_files/input_code/"+filename, "llm/llm_output_files/optimized_"+filename)
            
            # Compilation error in unoptimized file, exit script
            if regression_test_result == -2:
                print("Error in unoptimized file, exiting script")
                return

            # Compilation error in optimized file, re-prompt
            if regression_test_result == -1:
                if compilation_errors == 3:
                    print("Could not compile optimized file after 3 attempts, will re-optimize from original file")
                    # Be careful with recursion here
                    master_script()
                    return
                print("Error in optimized file, re-optimizing")
                handle_compilation_error(filename)
                compilation_errors += 1

            # Output difference in optimized file, re-prompt
            if regression_test_result == 0:
                if output_errors == 3:
                    print("Output differences after 3 attempts, will provide output differences to llm")
                    handle_logic_error(filename, True)
                elif output_errors > 3:
                    print("Still output differences after providing output differences to llm, will re-optimize from original file")
                    # Be careful with recursion here
                    master_script()
                    return
                print("Output difference in optimized file, re-optimizing")
                handle_logic_error(filename, False)
                output_errors += 1
            
            # Success
            if regression_test_result == 1:
                print("Regression test successful")
                print(f"{iter}: passing code to measure energy and get evaluator feedback")
                get_evaluator_feedback("", "", "", "", "", "")

                #call master_script() for evaluator feedback
                #what's the stoping condition
                if iter >= 2:
                    return
                master_script(iter+1)

if __name__ == "__main__":
    master_script()