import webbrowser

def search_youtube(query):
    """Open YouTube and search for the given query."""
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    print(f"Searching YouTube for: {query}")
    exit()


