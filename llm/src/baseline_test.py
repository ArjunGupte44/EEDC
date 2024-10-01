import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from energy.src.measure_energy import get_evaluator_feedback

def baseline_test():
    for filename in os.listdir("../llm_input_files/input_code"):
        get_evaluator_feedback(filename)
        return

if __name__ == "__main__":
    baseline_test()