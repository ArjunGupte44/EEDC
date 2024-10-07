import subprocess
import os
from dotenv import load_dotenv
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')

TEST_OUTPUT_FILE = f"{USER_PREFIX}/EEDC/llm/src/output_logs/regression_test_log.txt"
UNOPTIMIZED_OUTPUT = f"{USER_PREFIX}/EEDC/llm/src/output_logs/unoptimized_output.txt"
OPTIMIZED_OUTPUT = f"{USER_PREFIX}/EEDC/llm/src/output_logs/optimized_output.txt"

def compile_program(source_file, output_exec, output_log):
    print(f"\nregression_test(compile_program): Compiling {source_file}\n")
    try: 
        # Run make compile
        # Redirect stdout and stderr to the regression_test_log file
        subprocess.run(
                ["make", "compile"], 
                check=True,
                stdout=output_log, 
                stderr=output_log  # Redirect stderr to the same file as stdout
        )
        print("regression_test: Makefile compile successfully.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"regression_test: Makefile compile failed: {e}\n")
        return False

def compile_optimized_program(optimized_source_file, optimized_output_exec, output_log):
    print(f"\nregression_test(compile_program): Compiling {optimized_source_file}\n")
    try: 
        # Run make compile
        # Redirect stdout and stderr to the regression_test_log file
        subprocess.run(
                ["make", "compile_optimized"],
                check=True,
                stdout=output_log, 
                stderr=output_log  # Redirect stderr to the same file as stdout
        )
        print("regression_test: Makefile compile successfully.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"regression_test: Makefile compile failed: {e}\n")
        return False

def run_program(exec_path, output_file):
    # This run original
    print(f"\nregression_test(run_program): Running original {exec_path}\n")
    
    # Run the make command and capture the output in a variable
    result = subprocess.run(["make", "run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Check for errors
    if result.returncode != 0:
        print(f"Runtime error on {exec_path} with error message: {result.stderr}")
        return False

    # Filter out the unwanted lines
    filtered_output = "\n".join(
        line for line in result.stdout.splitlines()
        if not (line.startswith("make[") or line.startswith("./"))
    )
    
    # Write the filtered output to the file
    with open(output_file, 'w+') as f:
        f.write(filtered_output)
    
    return True

def run_program_optimized(exec_path, output_file):

    # This run optimized
    print(f"\nregression_test(run_program): Running optimized {exec_path}\n")
    
    # Run the make command and capture the output in a variable
    result = subprocess.run(["make", "run_optimized"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Check for errors
    if result.returncode != 0:
        print(f"Runtime error on {exec_path} with error message: {result.stderr}")
        return False

    # Filter out the unwanted lines
    filtered_output = "\n".join(
        line for line in result.stdout.splitlines()
        if not (line.startswith("make[") or line.startswith("./"))
    )
    
    # Write the filtered output to the file
    with open(output_file, 'w+') as f:
        f.write(filtered_output)
    
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
def regression_test(unoptimized_file_path, optimized_file_path, folder_name):
    output_different = False
    print(f"\nregression_test unoptimized_file_path: {unoptimized_file_path}")
    print(f"regression_test optimized_file_path: {optimized_file_path}\n")

    unoptimized_file_exec = unoptimized_file_path.split(".")[0]
    optimized_file_exec = optimized_file_path.split(".")[0]

    #change current directory to benchmarks/folder to run make file
    os.chdir(f"{USER_PREFIX}/EEDC/llm/benchmarks_out/{folder_name}")    
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")


    # compile program
    with open(TEST_OUTPUT_FILE, 'w+') as output_log:

        #compile program
        if not compile_program(unoptimized_file_path, unoptimized_file_exec, output_log):
            # Return code when unoptimized file does not compile
            return -2
        if not compile_optimized_program(optimized_file_path, optimized_file_exec, output_log):
            # Return code when optimized file does not compile
            return -1

        #run program
        run_program(unoptimized_file_exec, UNOPTIMIZED_OUTPUT)
        run_program_optimized(optimized_file_exec, OPTIMIZED_OUTPUT)
        if not compare_outputs(UNOPTIMIZED_OUTPUT, OPTIMIZED_OUTPUT, output_log):
            output_different = True
        if output_different:
            return 0
        else:
            output_log.write("Regression test successful. Outputs are the same.\n\n")
            return 1

if __name__ == "__main__":

    #input to regresstion thest should be path to optimized and original code
    regression_test("/home/jimmy/VIP_PTM/EEDC/llm/benchmarks_out/chameneosredux/chameneosredux.gpp-5.c++", "/home/jimmy/VIP_PTM/EEDC/llm/benchmarks_out/chameneosredux/optimized_chameneosredux.gpp-5.c++", "chameneosredux")