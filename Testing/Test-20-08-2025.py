import requests
import time

def search_papers(query, limit=5, retries=5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "paperId,title,authors,year,url,abstract"
    }

    for attempt in range(retries):
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:  # Too many requests
            print("Rate limited. Waiting before retry...")
            time.sleep(15 * (attempt + 1))  # exponential backoff
        else:
            return response.json()

    return {"error": "Failed after retries"}


# Example
data = search_papers("deep learning in healthcare", limit=3)

if "data" in data:
    papers = data["data"]
    print(f"Total Papers Found: {len(papers)}\n")

    for i, paper in enumerate(papers, start=1):
        print(f"Paper {i}:")
        print(f"  PaperID : {paper.get('paperId', 'N/A')}")
        print(f"  URL     : {paper.get('url', 'N/A')}")
        print(f"  Title   : {paper.get('title', 'N/A')}")
        print(f"  Year    : {paper.get('year', 'N/A')}")
        print(f"  Status  : {'Available' if paper else 'Unavailable'}")
        
        authors = [author.get("name", "Unknown") for author in paper.get("authors", [])]
        print(f"  Authors : {', '.join(authors) if authors else 'N/A'}")

        abstract = paper.get("abstract", None)
        print(f"  Abstract: {abstract if abstract else 'N/A'}")
        print("-" * 60)

else:
    print("Error:", data)
