from pydantic import BaseModel
from openai import OpenAI
from regression_test import regression_test
from dotenv import load_dotenv
import os

load_dotenv()
openai_key = os.getenv('API_KEY')

prompt = f"""You are tasked with optimizing the following code for energy efficiency, specifically focusing on time and space complexity. Analyze the code and provide an explicit step-by-step explanation of how sections of the code can be optimized. Explicitly consider multiple optimization paths (e.g., different algorithms, data structures). After evaluating the pros and cons of each, choose the most efficient strategy and update the code accordingly. After walking through the analysis, implement the necessary changes directly into the code. Some aspects of the code to consider for optimization include:

                Reduction of nested loops
                Efficient data structure selection
                Dynamic programming or memorization opportunities
                Utilization of specialized algorithms
                Code simplicity and readability

                Example of optimization: 
                Example of Python code to be optimized:
                ```
                # Define a list of numbers
                numbers = [1, 2, 3, 4, 5]

                # Nested loops to calculate the sum of all pairwise products
                total_sum = 0
                for i in numbers:
                    for j in numbers:
                        total_sum += i * j

                print("Total sum of pairwise products:", total_sum)
                ```

                Example of updated Python Code after Optimization:
                ```
                import numpy as np
                from scipy import sparse

                # Define a list of numbers
                numbers = [1, 2, 3, 4, 5]

                # Calculate the pairwise products using the Kronecker product
                pairwise_products = sparse.kron(numbers, numbers)

                # Sum up all the elements in the matrix
                total_sum = np.sum(pairwise_products)

                print("Total sum of pairwise products:", total_sum)
                ```

                Here is the actual code to be optimized: 
                """

def llm_optimize(filename):
    source_path = "llm/llm_input_files/input_code/" + filename
    with open(source_path, "r") as file:
        code_content = file.read()

    class Strategy(BaseModel):
        Pros: str
        Cons: str

    class OptimizationReasoning(BaseModel):
        analysis: str
        strategies: list[Strategy] 
        selected_strategy: str
        final_code: str

    #checking for evaluator feedback
    # Get the current directory of the script
    current_dir = os.path.dirname(__file__)
    # Construct the absolute path to evaluator_feedback.txt
    feedback_file_path = os.path.abspath(os.path.join(current_dir, "../../energy/src/evaluator_feedback.txt"))

    if os.path.isfile(feedback_file_path):
        with open(feedback_file_path, 'r') as file:
            evaluator_feedback = file.read()
            print("got evaluator feedback")
        # print("File content:", content)
    else:
        evaluator_feedback = ""
        print("Evaluator haven't gave feedback")

    # add code content to prompt
    optimize_prompt = prompt + f" {code_content}" + f"{evaluator_feedback}"

    client = OpenAI(api_key=openai_key)  

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
            {
                "role": "user",
                "content": optimize_prompt
            }
        ],
        response_format=OptimizationReasoning
    )

    if completion.choices[0].message.parsed.final_code == "":
        print("Error in llm completion")
        return
    
    final_code = completion.choices[0].message.parsed.final_code

    destination_path = "llm/llm_output_files/"
    with open(destination_path+"optimized_"+filename, "w") as file:
        file.write(final_code)

    # Success code
    return 0

def handle_compilation_error(filename):
    with open("llm/llm_output_files/optimized_"+filename, "r") as file:
        optimized_code = file.read()

    with open("llm/src/output_logs/regression_test_log.txt", "r") as file:
        error_message = file.read()
                      
        class ErrorReasoning(BaseModel):
            analysis: str
            final_code: str
        
        compilation_error_prompt = f"""You were tasked with the task outlined in the following prompt: {prompt}. You returned the following optimized code: {optimized_code}. However, the code failed to compile with the following error message: {error_message}. Analyze the error message and explicitly identify the issue in the code that caused the compilation error. Then, consider if there's a need to use a different optimization strategy to compile successfully or if there are code changes which can fix this implementation strategy. Finally, update the code accordingly and ensure it compiles successfully. Ensure that the optimized code is both efficient and error-free and return it. """   
        
        client = OpenAI(api_key=openai_key)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
                {
                    "role": "user",
                    "content": compilation_error_prompt
                }
            ],
            response_format=ErrorReasoning
        )

        final_code = completion.choices[0].message.parsed.final_code

        destination_path = "llm/llm_output_files/"
        with open(destination_path+"optimized_"+filename, "w") as file:
            file.write(final_code)

def handle_logic_error(filename, use_output_differences):
    with open("llm/llm_output_files/optimized_"+filename, "r") as file:
        optimized_code = file.read()

    with open("llm/src/output_logs/regression_test_log.txt", "r") as file:
        output_differences = file.read()
    
    class ErrorReasoning(BaseModel):
        analysis: str
        final_code: str
        
    if not use_output_differences:
        logic_error_prompt = f"""You were tasked with the task outlined in the following prompt: {prompt}. You returned the following optimized code: {optimized_code}. However, the code failed to produce the same outputs as the original source code. Analyze the source code and the optimized code and explicitly identify the potential reasons that caused the logic error. Then, consider if there's a need to use a different optimization strategy to match the outputs or if there are code changes which can fix this implementation strategy. Finally, update the code accordingly and ensure it will match the source code's outputs for any input. Ensure that the optimized code is both efficient and error-free and return it. """   
    else:
        logic_error_prompt = f"""You were tasked with the task outlined in the following prompt: {prompt}. You returned the following optimized code: {optimized_code}. However, the code failed to produce the same outputs as the original source code. Here are the output differences : {output_differences}. Analyze the source code and the optimized code and explicitly identify the potential reasons that caused the logic error. Then, consider if there's a need to use a different optimization strategy to match the outputs or if there are code changes which can fix this implementation strategy. Finally, update the code accordingly and ensure it will match the source code's outputs for any input. Ensure that the optimized code is both efficient and error-free and return it. """

    client = OpenAI(api_key=openai_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
            {
                "role": "user",
                "content": logic_error_prompt
            }
        ],
        response_format=ErrorReasoning
    )

    final_code = completion.choices[0].message.parsed.final_code

    destination_path = "llm/llm_output_files/"
    with open(destination_path+"optimized_"+filename, "w") as file:
        file.write(final_code)