from pydantic import BaseModel
from openai import OpenAI
import json
import os
from regression_test import regression_test

def master_script():
    # Loop through all the input code files in the directory
    for filename in os.listdir("llm/llm_input_files/input_code"):

        if filename == "binarytrees.gpp-9.c++":

            comperrors = 0
            logicerrors = 0
            optimizations = 0

            print(filename)

            source_path = "llm/llm_input_files/input_code/" + filename

            with open(source_path, "r") as file:
                code_content = file.read()
            print(code_content)

            class Strategy(BaseModel):
                Pros: str
                Cons: str

            class OptimizationReasoning(BaseModel):
                analysis: str
                strategies: list[Strategy] 
                selected_strategy: str
                final_code: str

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
                    
                {code_content}

                """

            client = OpenAI(api_key="openai_key")  

            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=OptimizationReasoning
            )

            print(completion.choices[0].message.parsed)

            final_code = completion.choices[0].message.parsed.final_code



            destination_path = "llm/llm_output_files/"
            with open(destination_path+"optimized_"+filename, "w") as file:
                file.write(final_code)

            optimizations += 1
            success = regression_test("llm/llm_input_files/input_code/"+filename, destination_path+"optimized_"+filename)
            print(f"Optimization attempt {optimizations} with success {success}")

            while success != 1 and optimizations < 6:
                if success == 0:
                    print(f"Optimization attempt {optimizations} with success {success}")
                    logicerrors += 1
                    success, optimizations = handle_logic_error(prompt, optimizations, filename)
                        
                elif success == -1:
                    print(f"Optimization attempt {optimizations} with success {success}")
                    success, optimizations = handle_compilation_error(prompt, optimizations, filename)

            if success == 1:
                print(f"Optimization attempt {optimizations} with success {success}")
            else:
                print("Optimization failed.")
            

def handle_compilation_error(prompt, optimizations, filename):
    success = -1
    comperrors = 0
    while success == -1 and comperrors < 3:
        comperrors += 1
        with open("output_log.txt", "r") as file:            #dummy file to be replaced with actual compilation error file
            error_message = file.read()
        print(error_message)

        with open("llm/llm_output_files/optimized_"+filename, "r") as file:
            optimized_code = file.read()
        
        class ErrorReasoning(BaseModel):
            analysis: str
            final_code: str
        
        new_prompt = f"""You were tasked with the task outlined in the following prompt: {prompt}. You returned the following optimized code: {optimized_code}. However, the code failed to compile with the following error message: {error_message}. Analyze the error message and explicitly identify the issue in the code that caused the compilation error. Then, consider if there's a need to use a different optimization strategy to compile successfully or if there are code changes which can fix this implementation strategy. Finally, update the code accordingly and ensure it compiles successfully. Ensure that the optimized code is both efficient and error-free and return it. """   
        client = OpenAI(api_key="openai_key")
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
                {
                    "role": "user",
                    "content": new_prompt
                }
            ],
            response_format=ErrorReasoning
        )

        print(completion.choices[0].message.parsed)

        final_code = completion.choices[0].message.parsed.final_code

        destination_path = "llm/llm_output_files/"
        with open(destination_path+"optimized_"+filename, "w") as file:
            file.write(final_code)

        optimizations += 1
        success = regression_test("llm/llm_input_files/input_code/"+filename, destination_path+"optimized_"+filename)

    return success, optimizations
       

def handle_logic_error(prompt, optimizations, filename):

    logicerrors = 0
    success = 0
    while success == 0 and logicerrors < 3:
        logicerrors += 1

        with open("llm/llm_output_files/optimized_"+filename, "r") as file:
            optimized_code = file.read()
        
        class ErrorReasoning(BaseModel):
            analysis: str
            final_code: str
        
        if logicerrors > 2:             #if logic errors persist, we do the same thing but give it information about the cases its failing
            with open("output_log.txt", "r") as file:            
                error_message = file.read()
            print(error_message)
            new_prompt = f"""You were tasked with the task outlined in the following prompt: {prompt}. You returned the following optimized code: {optimized_code}. However, the code failed to produce the same outputs as the original source code. Here are the output differences : {error_message}. Analyze the source code and the optimized code and explicitly identify the potential reasons that caused the logic error. Then, consider if there's a need to use a different optimization strategy to match the outputs or if there are code changes which can fix this implementation strategy. Finally, update the code accordingly and ensure it will match the source code's outputs for any input. Ensure that the optimized code is both efficient and error-free and return it. """
        else:
            new_prompt = f"""You were tasked with the task outlined in the following prompt: {prompt}. You returned the following optimized code: {optimized_code}. However, the code failed to produce the same outputs as the original source code. Analyze the source code and the optimized code and explicitly identify the potential reasons that caused the logic error. Then, consider if there's a need to use a different optimization strategy to match the outputs or if there are code changes which can fix this implementation strategy. Finally, update the code accordingly and ensure it will match the source code's outputs for any input. Ensure that the optimized code is both efficient and error-free and return it. """   

        client = OpenAI(api_key="openai_key")
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
                {
                    "role": "user",
                    "content": new_prompt
                }
            ],
            response_format=ErrorReasoning
        )

        print(completion.choices[0].message.parsed)

        final_code = completion.choices[0].message.parsed.final_code

        destination_path = "llm/llm_output_files/"
        with open(destination_path+"optimized_"+filename, "w") as file:
            file.write(final_code)

        optimizations += 1
        success = regression_test("llm/llm_input_files/input_code/"+filename, destination_path+"optimized_"+filename)

    return success, optimizations
    


if __name__ == "__main__":
    master_script()
