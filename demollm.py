import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Who is Virat Kohli?"}
    ],
    temperature=0.7,
    max_tokens=300
)

print("--- RESPONSE ---")
print(response.choices[0].message.content)

print("\n--- USAGE STATS ---")
print(f"Input tokens: {response.usage.prompt_tokens}")
print(f"Output tokens: {response.usage.completion_tokens}")