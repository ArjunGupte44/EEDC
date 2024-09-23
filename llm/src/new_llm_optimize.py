from pydantic import BaseModel
from openai import OpenAI
import json
import os

for filename in os.listdir("llm/llm_input_files/input_code"):
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

    client = OpenAI(api_key="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")  

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

    # Extract the final code from the completion response
    final_code = completion.choices[0].message.parsed.final_code



    destination_path = "llm/llm_output_files/"
    with open(destination_path+"optimized_"+filename, "w") as file:
        file.write(final_code)