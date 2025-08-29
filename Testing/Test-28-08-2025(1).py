import requests

def askAI(userInput):
    API_KEY = "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"
    API_URL = "https://api.perplexity.ai/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    MODEL_NAME = "sonar-deep-research"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant. Always respond with very long and detailed answers."},
            {"role": "user", "content": userInput + " Don't add markdown syntax bold, italic, underline, bullets, citations and reference markers etc."}
        ],
        "max_tokens": 700,
        "temperature": 0.7,
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    print(data)

    # # Extracting needed fields
    # answer = data["choices"][0]["message"]["content"]
    # citations = data.get("citations", [])
    # search_results = data.get("search_results", [])

    # # Prepare response in structured form
    # result = {
    #     "answer": answer,
    #     "citations": citations,
    #     "search_results": []
    # }

    # # Add detailed search results
    # for res in search_results:
    #     result["search_results"].append({
    #         "title": res.get("title"),
    #         "url": res.get("url"),
    #         "date": res.get("date"),
    #         "last_updated": res.get("last_updated")
    #     })

    # return result


# Example usage:
if __name__ == "__main__":
    query = input("Enter your question: ")
    output = askAI(query)

    # print("\n=== AI Answer ===\n", output["answer"])
    # print("\n=== Citations ===")
    # for c in output["citations"]:
    #     print("-", c)

    # print("\n=== Search Results ===")
    # for s in output["search_results"]:
    #     print(f"Title: {s['title']}")
    #     print(f"URL: {s['url']}")
    #     print(f"Date: {s['date']}")
    #     print(f"Last Updated: {s['last_updated']}")
    #     print()
