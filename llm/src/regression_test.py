import subprocess
import os

APR_INCLUDE_PATH = "/Library/Developer/CommandLineTools/SDKs/MacOSX14.0.sdk/usr/include/apr-1"
APR_LIB = "apr-1"

TREE_DEPTHS_TO_TEST = [6, 10, 15]    # 6 is the minimum depth

TEST_OUTPUT_FILE = "output_log.txt"  

def compile_program(source_file, output_exec, output_log):
    print(f"Compiling {source_file}")
    try:
        subprocess.run(
            ["g++", "-o", output_exec, source_file, f"-I{APR_INCLUDE_PATH}", f"-l{APR_LIB}"],
            stderr=subprocess.PIPE,
            check=True 
        )
        print(f"Compiled {source_file} successfully.\n")
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode()
        # print(f"Compilation error for {source_file}:")
        print(error_message, "\n")
        output_log.write(f"Compilation error for {source_file}:\n{error_message}\n\n")
        return False

def run_program(exec_path, output_file, depth):
    with open(output_file, 'w') as f:
        result = subprocess.run([exec_path, depth], stdout=f, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Runtime error on {exec_path} with error message: {result.stderr.decode()}")
            return False
    return True

def compare_outputs(file1, file2, output_log):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        file1_content = f1.readlines()
        file2_content = f2.readlines()
        if file1_content == file2_content:
            output_log.write("Outputs are the same.\n")
            return True
        else:
            output_log.write("Outputs are different.\n")
            output_log.write(f"binarytrees output:\n{file1_content}\n")
            output_log.write(f"optimized_binarytrees output:\n{file2_content}\n\n")
            return False

def regression_test(UNOPTIMIZED_FILE, OPTIMIZED_FILE):
    did_compile = True
    output_different = False

    UNOPTIMIZED_EXEC = "./" + UNOPTIMIZED_FILE.split(".")[0]
    OPTIMIZED_EXEC = "./" + OPTIMIZED_FILE.split(".")[0]
    UNOPTIMIZED_OUTPUT = "output_" + UNOPTIMIZED_FILE.split(".")[0] + ".txt"
    OPTIMIZED_OUTPUT = "output_" + OPTIMIZED_FILE.split(".")[0] + ".txt"

    with open(TEST_OUTPUT_FILE, 'w') as output_log:
        # output_log.write("Starting regression tests.\n\n")

        if not compile_program(UNOPTIMIZED_FILE, UNOPTIMIZED_OUTPUT, output_log):
            did_compile = False
        if not compile_program(OPTIMIZED_FILE, OPTIMIZED_OUTPUT, output_log):
            did_compile = False

        if not did_compile:
            # output_log.write("Compilation failed.\n")
            return -1

        for depth in TREE_DEPTHS_TO_TEST:
            output_log.write(f"Testing with depth {depth} \t")
            run_program(UNOPTIMIZED_EXEC, UNOPTIMIZED_OUTPUT, str(depth))
            run_program(OPTIMIZED_EXEC, OPTIMIZED_OUTPUT, str(depth))
            if not compare_outputs(UNOPTIMIZED_OUTPUT, OPTIMIZED_OUTPUT, output_log):
                output_different = True
        if output_different:
            # output_log.write("Analyze the output differences above and identify why the output for optimized_binarytrees.cpp is different. Investigate issues such as memory management, algorithmic discrepancies, or optimizations that could affect the results. Make the changes in optimized_binarytrees.cpp and ensure the outputs match.\n")
            return 0
        else:
            output_log.write("Regression test successful. Outputs are the same.\n\n")
            return 1
            

if __name__ == "__main__":
    # new_llm_optimize()
    # for x in llm_input_files:
    regression_test("binarytrees.cpp", "optimized_binarytrees.cpp")
    # while regression_test == False:
    #    tell llm that the output is different, up to 3 times
    #    then if it still fails, use output_log.txt to feed into new_llm_optimize() function



