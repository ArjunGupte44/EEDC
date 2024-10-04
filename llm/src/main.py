import sys
import os
from dotenv import load_dotenv
from regression_test import regression_test
from new_llm_optimize import llm_optimize, handle_compilation_error, handle_logic_error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from energy.src.measure_energy import get_evaluator_feedback
from energy.src.benchmark import Benchmark
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')


def master_script():
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
        compilation_errors, output_errors, success = 0, 0, 0

        # Run llm optimization until successful regression test and energy reduced by 5%
        while True:
            regression_test_result = regression_test(f"llm/llm_input_files/input_code/{filename}", f"llm/benchmarks_out/{filename.split(".")[0]}/optimized_{filename}", filename.split(".")[0])
            
            # Compilation error in unoptimized file, exit script
            if regression_test_result == -2:
                print("Error in unoptimized file, exiting script")
                return

            # Compilation error in optimized file, re-prompt
            if regression_test_result == -1:
                if compilation_errors == 3:
                    print("Could not compile optimized file after 3 attempts, will re-optimize from original file")
                    llm_optimize(filename)
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
                    llm_optimize(filename)
                    output_errors = 0
                    continue
                handle_logic_error(filename, False)
                output_errors += 1
            
            # Success
            if regression_test_result == 1:
                print("Regression test successful")
                print(f"{iter}: passing code to measure energy and get evaluator feedback")
                get_evaluator_feedback("", "", "", "", "", "")

                # Not final logic, should be to re-prompt with code with best performance. Should probably stop if it cannot optimize within X amount of tries.
                # Stop if energy is not reduced by 5%
                if success == 3:
                    print("Energy was not reduced by 5% after 3 attempts, will re-optimize from original file")
                    llm_optimize(filename)
                    success = 0

if __name__ == "__main__":
    master_script()