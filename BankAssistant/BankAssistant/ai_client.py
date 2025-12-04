from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(prompt: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=300,
        )
        message = response.output[0].content[0].text
        return message
    except Exception as e:
        return f"[OpenAI error] {e}"