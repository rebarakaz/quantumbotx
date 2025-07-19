# core/ai/ollama_client.py

import ollama

def ask_ollama(prompt, model="llama3"):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"
