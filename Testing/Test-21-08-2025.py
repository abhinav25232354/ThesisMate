import requests

def search_crossref(query, rows=100, max_results=500):
    url = "https://api.crossref.org/works"
    cursor = "*"
    results = []
    
    while len(results) < max_results:
        params = {
            "query": query,
            "rows": rows,
            "cursor": cursor,
            "cursor": cursor,
            "mailto": "your_email@example.com"  # optional but recommended
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            break
        
        data = response.json()
        items = data.get("message", {}).get("items", [])
        if not items:
            break
        
        for item in items:
            title = item.get("title", ["No Title"])[0]
            url = item.get("URL", "No URL")
            date_parts = item.get("issued", {}).get("date-parts", [[]])[0]
            year = date_parts[0] if date_parts else "Unknown"
            authors = []
            for author in item.get("author", []):
                name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                authors.append(name)
            
            results.append({
                "title": title,
                "url": url,
                "year": year,
                "authors": authors if authors else ["Unknown"]
            })
            
            if len(results) >= max_results:
                break
        
        # Update cursor for next page
        cursor = data.get("message", {}).get("next-cursor", None)
        if not cursor:
            break
    
    return results

if __name__ == "__main__":
    topic = input("Enter research topic: ")
    papers = search_crossref(topic, rows=100, max_results=500)  # change max_results up to 100000 if needed
    print(f"\n✅ Total research items fetched: {len(papers)}\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   URL: {paper['url']}")
        print(f"   Year: {paper['year']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print()
