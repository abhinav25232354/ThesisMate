from semanticscholar import SemanticScholar

sch = SemanticScholar()  # Optionally: SemanticScholar(api_key="YOUR_API_KEY")

results = sch.search_paper("generative ai")
for paper in results:
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join([a.name for a in paper.authors])}")
    print(f"Year: {paper.year}")
    print(f"URL: {paper.url}")
    print("")
