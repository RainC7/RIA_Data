from bs4 import BeautifulSoup

def parse_wiki_search_results(html_content: str) -> list:
    """
    Parses the HTML content of a RIA Wiki search results page
    and extracts relevant information for each search result.

    Args:
        html_content: The HTML content of the search results page.

    Returns:
        A list of dictionaries, where each dictionary represents a search result
        with 'title', 'url', and 'snippet' keys.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []

    search_results_ul = soup.find('ul', class_='mw-search-results')
    if not search_results_ul:
        return results

    for li in search_results_ul.find_all('li', class_='mw-search-result'):
        title_tag = li.find('div', class_='mw-search-result-heading').find('a')
        snippet_tag = li.find('div', class_='searchresult')

        title = title_tag.get_text(strip=True) if title_tag else 'N/A'
        url = "https://wiki.ria.red" + title_tag['href'] if title_tag and 'href' in title_tag.attrs else 'N/A'
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else 'N/A'

        results.append({
            'title': title,
            'url': url,
            'snippet': snippet
        })
    return results
