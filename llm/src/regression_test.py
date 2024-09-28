import subprocess

# Includes for apr
APR_INCLUDE_PATH = "/usr/include/apr-1.0"
APR_LIB = "apr-1"

TREE_DEPTHS_TO_TEST = [6, 10, 15]    # 6 is the minimum depth

TEST_OUTPUT_FILE = "llm/src/output_logs/regression_test_log.txt"
UNOPTIMIZED_OUTPUT = "llm/src/output_logs/unoptimized_output.txt"
OPTIMIZED_OUTPUT = "llm/src/output_logs/optimized_output.txt"

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
        output_log.write(f"Compilation error for {source_file}:\n{error_message}\n\n")
        return False

def run_program(exec_path, output_file, depth):
    with open(output_file, 'w+') as f:
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

# Only for binarytrees
def regression_test(UNOPTIMIZED_FILE, OPTIMIZED_FILE):
    output_different = False

    UNOPTIMIZED_EXEC = UNOPTIMIZED_FILE.split(".")[0]
    OPTIMIZED_EXEC = OPTIMIZED_FILE.split(".")[0]

    # have to rewrite TES
    with open(TEST_OUTPUT_FILE, 'w+') as output_log:
        if not compile_program(UNOPTIMIZED_FILE, UNOPTIMIZED_EXEC, output_log):
            # Return code when unoptimized file does not compile
            return -2
        if not compile_program(OPTIMIZED_FILE, OPTIMIZED_EXEC, output_log):
            # Return code when optimized file does not compile
            return -1

        for depth in TREE_DEPTHS_TO_TEST:
            output_log.write(f"Testing with depth {depth} \t")
            run_program(UNOPTIMIZED_EXEC, UNOPTIMIZED_OUTPUT, str(depth))
            run_program(OPTIMIZED_EXEC, OPTIMIZED_OUTPUT, str(depth))
            if not compare_outputs(UNOPTIMIZED_OUTPUT, OPTIMIZED_OUTPUT, output_log):
                output_different = True
        if output_different:
            return 0
        else:
            output_log.write("Regression test successful. Outputs are the same.\n\n")
            return 1

if __name__ == "__main__":
    regression_test("binarytrees.cpp", "optimized_binarytrees.cpp")