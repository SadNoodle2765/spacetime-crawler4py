import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

ACCEPTED_DOMAINS = [re.compile(r'.*[\W]ics\.uci\.edu\/.*'), re.compile(r'.*[\W]cs\.uci\.edu\/.*'),
                    re.compile(r'.*[\W]infomatics\.uci\.edu\/.*'), re.compile(r'.*[\W]stats\.uci\.edu\/.*'),
                    re.compile(r'.*today\.uci\.edu\/department\/information_computer_sciences\/*')]

DISCOVERED_LINKS = set()

TRAVERSED_COUNT = 0

def scraper(url, resp):
    global DISCOVERED_LINKS
    global TRAVERSED_COUNT
    links = extract_next_links(url, resp)
    links = [link for link in links if is_valid(link)]

    links_file = open('Logs/DiscoveredLinks.log', "a")
    for link in links:
        links_file.write(link + '\n')

    links_file.close()

    DISCOVERED_LINKS |= set(links)
    #print(test)
    TRAVERSED_COUNT += 1

    for link in links:
        print(link)

    print('Discovered Link Count: ' + str(len(DISCOVERED_LINKS)))
    print('Number of Links Traversed: ' + str(TRAVERSED_COUNT))

    return links

def extract_next_links(url, resp): 
    url_scheme = urlparse(url).scheme       # Getting scheme and netloc to append
    url_netloc = urlparse(url).netloc       # in front of relative path links

    if resp.status < 200 or resp.status > 399:
        return list()

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    filtered_links = set()

    for link in links: 

        parsed_link = urlparse(link)
        # First character checks
        if re.match(r'^#.*$', link):                        # Get rid of scroll-to tags
            continue
        elif re.match(r'^\/[^\/].+$', link):                  # First character is / (relative path)
            link = f'{url_scheme}://{url_netloc}{link}'     # Add the scheme and netloc to the beginning link
        elif re.match(r'^\/\/.+$', link):
            link = f'{url_scheme}:{link}'                   # First characters are //  (use same scheme)
                                                            # Add scheme to the beginning of link

        
        link = link.split('?')[0]
        link = link.split('#')[0]

        if link in DISCOVERED_LINKS:
            continue

        for pattern in ACCEPTED_DOMAINS:
            match = re.match(pattern, link)
            if match:
                filtered_links.add(link)
                break
        #filtered_links.append(link)

    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return list(filtered_links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|pdf|pptx|docx|jpg|"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
