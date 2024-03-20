import ollama
from ollama import Client

generator_instructions_path = "/home/agupte/VIP_PTM_DL/LLM_Energy_Efficiency/prompts/generator_instructions.txt"
input_code_path = "/home/agupte/VIP_PTM_DL/LLM_Energy_Efficiency/prompts/input_code.txt"

instructions_file = open(generator_instructions_path, "r")
instructions = "".join(instructions_file.readlines())

input_code_file = open(input_code_path, "r")
input_code = "".join(input_code_file.readlines())

generator_prompt = instructions + input_code
#print(generator_prompt)


client = Client("http://")
response = ollama.chat(model='codellama', messages=[
  {
    'role': 'user',
    'content': generator_prompt,
  },
])
print(response['message']['content'])
