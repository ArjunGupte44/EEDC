import openai 

def chat_with_gpt(api_key, prompt):
    openai.api_key = api_key

    model_engine = "text-davinci-002"  # You can use other engines like "text-ada" for GPT-3
    max_tokens = 100

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens
    )

    message = response.choices[0].text.strip()
    return message

if __name__ == "__main__":
    api_key = "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"
    prompt = "Translate the following English text to French: 'Hello, World!'"
    
    response = chat_with_gpt(api_key, prompt)
    print(f"GPT says: {response}")
