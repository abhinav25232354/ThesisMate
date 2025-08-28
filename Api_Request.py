from openai import OpenAI
import requests

def askAI(userInput):
    API_KEY = "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"
    API_URL = "https://api.perplexity.ai/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    MODEL_NAME = "sonar"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant. Always respond with very long and detailed answers."},
            {"role": "user", "content": userInput + "Don't add markdown syntax bold, italic, underline, bullets, citations and reference markers etc."}
        ],
        "max_tokens": 700,
        "temperature": 0.7,
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    # print(data)

    answer = data["choices"][0]["message"]["content"]
    # Format answer as HTML paragraphs for display
    content = "<p>" + answer.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
    citations = data.get("citations", [])
    search_results = data.get("search_results", [])
    return citations, content, search_results

if __name__ == "__main__":
    question = "Explain the theory of relativity in simple terms."
    print(askAI(question))