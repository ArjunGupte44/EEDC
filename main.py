import openai 
import sys

def call(api_key, prompt):
    openai.api_key = api_key
    model_engine = "text-davinci-003"
    max_tokens = 100

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens
    )

    message = response.choices[0].text.strip()
    return message

def main():
    if len(sys.argv) < 2:
        print("API key not provided.")
        return

    api_key = sys.argv[1]
    prompt = ""
    response = call(api_key, prompt)
    print(response)

if __name__ == "__main__":
    main()
