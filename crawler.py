import requests
from bs4 import BeautifulSoup

from collections import deque
from time import sleep
from urllib.parse import urljoin, urldefrag, urlsplit


def get_content(search_url):
    
    max_content_size = 5 * 1024 * 1024
    
    try:
        with requests.get(search_url, timeout=15, stream=True) as response:
              
            if not response.ok:
                print("HTTP unreachable: ", search_url)
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
            
            return BeautifulSoup(bytes(content), "html.parser")
            
    except requests.exceptions.Timeout as error:
        print("Request timed out", search_url, error)
    except requests.exceptions.RequestException as error:
        print("Request failed", search_url, error)
    
    return None

def crawler(search_url, search_title, queue, visited, final):

    soup = get_content(search_url)
    
    if soup is None:
        return None
        
    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True)
        address = urljoin(search_url, link["href"])
        
        if address not in visited:
            queue.append(address)
            visited.add(address)
        if search_title in text and address not in visited:
            final.add(address)



search_url = input("Home Page: ").strip()
search_title = input("Search for: ").strip()

visited = set()
final = set()
queue = deque([search_url])


while len(queue) > 0:
    crawler(queue.popleft(), search_title, queue, visited, final)
    

for link in final:
    print(link, "\n")
