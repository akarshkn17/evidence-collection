from urllib.parse import quote_plus


def issue_search_url(base_url: str, jql: str) -> str:
    return f"{base_url.rstrip('/')}/issues/?jql={quote_plus(jql)}"
