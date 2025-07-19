# core/utils/ai.py

import subprocess

def get_ollama_prediction(prompt, model="llama3"):
    """
    Kirim prompt ke Ollama model lokal dan ambil prediksi (BUY/SELL)
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=30
        )
        response = result.stdout.strip().lower()
        if "buy" in response:
            return "BUY"
        elif "sell" in response:
            return "SELL"
        else:
            return None
    except Exception as e:
        print(f"[AI Error] {e}")
        return None
