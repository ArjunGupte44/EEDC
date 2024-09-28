from pydantic import BaseModel
from openai import OpenAI
import json
import os

def evaluator_llm(benchmark_info):

    #extract original
    original_source_code = benchmark_info["original"]["source_code"]
    original_avg_energy = benchmark_info["original"]["avg_energy"]
    original_avg_runtime = benchmark_info["original"]["avg_runtime"]

    lowest_soruce_code = benchmark_info["lowest_avg_energy"]["source_code"]
    lowest_avg_energy = benchmark_info["lowest_avg_energy"]["avg_energy"]
    lowest_avg_runtime = benchmark_info["lowest_avg_energy"]["avg_runtime"]

    current_source_code = benchmark_info["current"]["source_code"]  
    current_avg_energy = benchmark_info["current"]["avg_energy"]
    current_avg_runtime = benchmark_info["current"]["avg_runtime"]

    prompt = f"""
    You are a code optimization expert. Evaluate the following current code snippet in terms of time and space complexity, readability, and performance. Please provide a detailed analysis of the code's efficiency and suggest further optimizations using the best energy code and original code as reference. Your response should include:

    1. An analysis of how the code currently works.
    2. Any inefficiencies or bottlenecks in terms of time, space, or readability.
    3. Step-by-step suggestions for improving the code, including alternative algorithms, data structures, or any other performance enhancement strategies.
    4. Examples of how the code can be changed or rewritten to achieve better performance in terms of energy usage.

    Here is the original code snippet:
    ```
    {original_source_code}
    ```
    Average energy usage: {original_avg_energy}
    Average run time: {original_avg_runtime}

    Here is the best code snippets(the lowest energy usage):
    ```
    {lowest_soruce_code}
    ```
    Average energy usage: {lowest_avg_energy}
    Average run time: {lowest_avg_runtime}

    Here is the current code snippiets that you are tasked to optimize:
    ```
    {current_source_code}
    ```
    Average energy usage: {current_avg_energy}
    Average run time: {current_avg_runtime}

    Please respond in natural language (English) with actionable suggestions for improving the code's performance in terms of energy usage.
    """


    client = OpenAI(api_key=)
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Think through the code optimizations strategies possible step by step"},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the answer from the response
    optimization_advice = response.choices[0].message.content

    #write to file
    with open("optimization_advise.txt", "w") as file:
        file.write(optimization_advice)
    
    return optimization_advice