import requests
import json

def analyze_pdf(pdf_url, question):
    """Analyze a PDF with a specific question"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": "Bearer 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"}
    
    payload = {
        "messages": [{
            "content": [
                {"type": "text", "text": question},
                {"type": "file_url", "file_url": {"url": pdf_url}}
            ],
            "role": "user"
        }],
        "model": "sonar-pro"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Usage
result = analyze_pdf(
    "https://www.semanticscholar.org/reader/9c9d7247f8c51ec5a02b0d911d1d7b9e8160495d",
    "What are the main recommendations?"
)

# Extract variables:
citations = result.get("citations", [])
search_results = result.get("search_results", [])
content = result.get("choices", [])[0].get("message", {}).get("content", "")

# Example usage:
print("Citations:", citations)
print("Search Results:", search_results)
print("Content:", content)