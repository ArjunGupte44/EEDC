import subprocess
import os

BINARY_TREES_SOURCE = "binarytrees.cpp"
OPTIMIZED_BINARY_TREES_SOURCE = "optimized_binarytrees.cpp"

BINARY_TREES_EXEC = "./binarytrees"
OPTIMIZED_BINARY_TREES_EXEC = "./optimized_binarytrees"

BINARY_TREES_OUTPUT = "output_binarytrees.txt"
OPTIMIZED_BINARY_TREES_OUTPUT = "output_optimized_binarytrees.txt"

APR_INCLUDE_PATH = "/Library/Developer/CommandLineTools/SDKs/MacOSX14.0.sdk/usr/include/apr-1"
APR_LIB = "apr-1"

TREE_DEPTHS_TO_TEST = [6, 10, 15]    # 6 is the minimum depth

TEST_OUTPUT_FILE = "output_log.txt"  

def compile_program(source_file, output_exec):
    print(f"Compiling {source_file}")
    try:
        result = subprocess.run(
            ["g++", "-o", output_exec, source_file, f"-I{APR_INCLUDE_PATH}", f"-l{APR_LIB}"],
            stderr=subprocess.PIPE,
            check=True 
        )
        print(f"Compiled {source_file} successfully.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Compilation error for {source_file}:")
        print(e.stderr.decode(), "\n") 
        return False

def run_program(exec_path, output_file, depth):
    with open(output_file, 'w') as f:
        result = subprocess.run([exec_path, depth], stdout=f, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Runtime error on {exec_path} with error message: {result.stderr.decode()}")
            return False
    return True

def compare_outputs(file1, file2):
    with open(TEST_OUTPUT_FILE, 'a') as output_log:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            file1_content = f1.readlines()
            file2_content = f2.readlines()

            if file1_content == file2_content:
                output_log.write("Outputs are the same.\n")
                return True
            else:
                output_log.write("Outputs are different.\n")
                output_log.write(f"binarytrees output:\n{file1_content}\n")
                output_log.write(f"optimized_binarytrees output:\n{file2_content}\n")
                return False

def regression_test():
    with open(TEST_OUTPUT_FILE, 'w') as output_log:
        output_log.write("Starting regression tests.\n\n")

        if not compile_program(BINARY_TREES_SOURCE, BINARY_TREES_EXEC):
            return
        if not compile_program(OPTIMIZED_BINARY_TREES_SOURCE, OPTIMIZED_BINARY_TREES_EXEC):
            return

    single_fail = False
    for depth in TREE_DEPTHS_TO_TEST:
        with open(TEST_OUTPUT_FILE, 'a') as output_log:
            output_log.write(f"Testing with depth {depth}\n")
        
        if not run_program(BINARY_TREES_EXEC, BINARY_TREES_OUTPUT, str(depth)):
            return
        if not run_program(OPTIMIZED_BINARY_TREES_EXEC, OPTIMIZED_BINARY_TREES_OUTPUT, str(depth + 1)):
            return

        if compare_outputs(BINARY_TREES_OUTPUT, OPTIMIZED_BINARY_TREES_OUTPUT):
            with open(TEST_OUTPUT_FILE, 'a') as output_log:
                output_log.write("Regression test successful. Outputs are the same.\n\n")
        else:
            single_fail = True
            with open(TEST_OUTPUT_FILE, 'a') as output_log:
                output_log.write("Regression test failed. Outputs are different.\n\n")
        
    if single_fail:
        with open(TEST_OUTPUT_FILE, 'a') as output_log:
            output_log.write("Analyze the output differences above and identify why the output for optimized_binarytrees.cpp is different. Investigate issues such as memory management, algorithmic discrepancies, or optimizations that could affect the results. Make the changes in optimized_binarytrees.cpp and ensure the outputs match.\n")

if __name__ == "__main__":
    # new_llm_optimize()
    # for x in llm_input_files:
    regression_test()
    # while regression_test == False:
    #    tell llm that the output is different, up to 3 times
    #    then if it still fails, use output_log.txt to feed into new_llm_optimize() function



