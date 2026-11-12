import requests
from bs4 import BeautifulSoup

from collections import deque
from time import sleep
from urllib.parse import urljoin, urldefrag, urlsplit


def get_content(search_url, valid_domain):
    
    max_content_size = 5 * 1024 * 1024
    
    try:
        with requests.get(search_url, timeout=15, stream=True) as response:
              
            if not response.ok:
                print("HTTP unreachable: ", search_url)
                return None
            
            if urlsplit(response.url).hostname != valid_domain:
                print("Redirected to external domain: ", response.url)
                return None
            
            content_type = response.headers.get("Content-Type", "").lower()
            media_type = content_type.split(";")[0].strip()
            
            if(media_type not in ("text/html", "application/xhtml+xml")):
                print("Not HTML")
                return None
            
            content = bytearray()
            
            for chunk in response.iter_content(chunk_size=8192):
                if(len(content) + len(chunk) > max_content_size):
                    print("Too much data", search_url)
                    return None
                content.extend(chunk)
            
            return BeautifulSoup(bytes(content), "html.parser"), response.url
            
    except requests.exceptions.Timeout as error:
        print("Request timed out", search_url, error)
    except requests.exceptions.RequestException as error:
        print("Request failed", search_url, error)
    
    return None

def crawler(queued_url, search_title, queue, discovered, final, domain, max_depth):

    search_url, url_depth = queued_url

    print("Currently searching: ", search_url, " on depth: ", url_depth ,"\n")

    content = get_content(search_url, domain)
    
    if content is None:
        return None
    
    soup, url = content
    
    if search_title.casefold() in soup.text.casefold():
        final.add(url)
        
    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True)
        address = urldefrag(urljoin(url, link["href"]))[0]
        parts = urlsplit(address)
        
        if parts.scheme not in ("http", "https"):
            continue
            
        
        
        if search_title.casefold() in text.casefold():
            final.add(address)
        
        if parts.hostname != domain:
            continue
        
        if address not in discovered:
            if url_depth + 1 <= max_depth:
                queue.append((address, url_depth + 1))
            discovered.add(address)



search_url = input("Home Page: ").strip()
search_title = input("Search for: ").strip()
max_depth = int(input("Max depth: ").strip())


discovered = {search_url}
final = set()
queue = deque([(search_url, 0)])
domain = urlsplit(search_url).hostname

while queue:
    crawler(queue.popleft(), search_title, queue, discovered, final, domain, max_depth)
    sleep(0.1)
    
    
print("Links found: ")

for link in final:
    print(link, "\n")
