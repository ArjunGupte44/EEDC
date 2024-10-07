import subprocess
import os
import pickle
from dotenv import load_dotenv
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')


#define raletive path to RAPL
rapl_main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../RAPL/main'))
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

class Benchmark():
    def __init__(self, benchmark_language, benchmark_name, filename, benchmark_data):
        self.benchmark_language = benchmark_language
        self.benchmark_name = benchmark_name
        self.benchmark_data = benchmark_data

    def run(self, optim_iter):
        # First clear the contents of the energy data log file
        print(f"Benchmark.run: clearing content in {self.benchmark_language}.csv")
        log_file_path = f"{USER_PREFIX}/EEDC/energy/src/{self.benchmark_language}.csv"
        if os.path.exists(log_file_path):
            file = open(log_file_path, "w+")
            file.close()

        #run make measure using make file
        #change current directory to benchmarks/folder to run make file
        os.chdir(f"{USER_PREFIX}/EEDC/llm/benchmarks_out/{self.benchmark_name}")
        current_dir = os.getcwd()
        print(f"Current directory: {current_dir}")

        #for testing purpose
        if optim_iter == 0: 
            try: 
                subprocess.run(["make", "measure"], check=True)
                print("Benchmark.run: make measure successfully\n")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Benchmark.run: make measure failed: {e}\n")
            return False
        
        #measure the optimize code energy 
        try: 
            subprocess.run(["make", "measure_optimized"], check=True)
            print("Benchmark.run: make measure successfully\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Benchmark.run: make measure failed: {e}\n")
        return False

        #Return path to results file
        results_file = f"{self.benchmark_language}.csv"
        return results_file


    def process_results(self, results_file, optim_iter, source_code_path) -> float:
        energy_data_file = open(f"{USER_PREFIX}/EEDC/energy/src/{self.benchmark_language}.csv", "r")
        benchmark_data = []
        for line in energy_data_file:
            parts = line.split(';')
            benchmark_name = parts[0].strip()
            energy_data = [vals.strip() for vals in parts[1].split(',')]
            
            #Remove empty strings for CPU, GPU, DRAM and convert remaining numbers to floats
            energy_data = [float(num) for num in energy_data if num]
            benchmark_data.append((benchmark_name, *energy_data))

        #Find average energy usage and average runtime
        avg_energy = 0
        avg_runtime = 0
        for data in benchmark_data:
            avg_energy += data[1]
            avg_runtime += data[2]
        avg_energy /= len(benchmark_data)
        avg_runtime /= len(benchmark_data)

        #Append results to benchmark data dict
        source_code_file = open(source_code_path, "r")
        source_code = source_code_file.read()
        self.benchmark_data[optim_iter] = (source_code, round(avg_energy, 3), round(avg_runtime, 3))
        # print(f"This is the iteration {optim_iter} of benchmark data: {self.benchmark_data[optim_iter]}")

        #Update PKL file with latest version of benchmark data dict
        with open(f"{USER_PREFIX}/EEDC/energy/{self.benchmark_language}/benchmark_data.pkl", "wb") as benchmark_data_pkl_file:
            pickle.dump(self.benchmark_data, benchmark_data_pkl_file)

        #Close all files
        energy_data_file.close()
        source_code_file.close()
        benchmark_data_pkl_file.close()