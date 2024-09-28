import subprocess
import os
import pickle

#USER_PREFIX = "/home/Arjun/VIP_PTM/"
# USER_PREFIX = "/home/jimmy/VIP_PTM/"


class Benchmark():
    def __init__(self, benchmark_language, benchmark_name):
        self.benchmark_language = benchmark_language
        self.benchmark_name = benchmark_name
        self.benchmark_data = {}

    def run(self, executable, args):
        #First clear the contents of the energy data log file
        log_file_path = f"/EEDC/energy/{self.benchmark_language}.csv"
        if os.path.exists(log_file_path):
            file = open(log_file_path, "w")
            file.close()

        #Load the MSR kernel module
        try:
            result = subprocess.run(
                ["sudo", "modprobe", "msr"],
                stderr=subprocess.PIPE,
                check=True 
            )
            print("Successfully loaded MSR kernel module - ready to begin benchmark.\n")
        except subprocess.CalledProcessError as e:
            print(f"Error while loading MSR kernel module:")
            print(e.stderr.decode(), "\n") 
            return False
        
        #Run the benchmark
        try:
            result = subprocess.run(
                f"sudo ../../RAPL/main \"{executable} {args}\" {self.benchmark_language} {self.benchmark_name}",
                shell=True,
                stderr=subprocess.PIPE,
                check=True
            )
            print("\nFinished running benchmark successfully.")
        except subprocess.CalledProcessError as e:
            print("Benchmark did not run successfully.")
            return False
        
        #Return path to results file
        results_file = f"{self.benchmark_language}.csv"
        return results_file

    def process_results(self, results_file, optim_iter, source_code_path) -> float:
        energy_data_file = open(f"{USER_PREFIX}EEDC/energy/{results_file}", "r")
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
        
        #Update PKL file with latest version of benchmark data dict
        with open(f"{USER_PREFIX}EEDC/energy/{self.benchmark_language}/benchmark_data.pkl", "wb") as benchmark_data_pkl_file:
            pickle.dump(self.benchmark_data, benchmark_data_pkl_file)

        #Close all files
        energy_data_file.close()
        source_code_file.close()
        benchmark_data_pkl_file.close()