import re
from tokenizer import computeWordFrequencies, tokenize
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from collections import defaultdict, Counter
import urllib.robotparser


ACCEPTED_DOMAINS = [re.compile(r'.*[\W]ics\.uci\.edu\/.*'), re.compile(r'.*[\W]cs\.uci\.edu\/.*'),
                    re.compile(r'.*[\W]informatics\.uci\.edu\/.*'), re.compile(r'.*[\W]stat\.uci\.edu\/.*'),
                    re.compile(r'.*today\.uci\.edu\/department\/information_computer_sciences\/*')]

DISCOVERED_LINKS = set()

DISCOVERED_SUBDOMAINS = defaultdict(int)

TOKEN_DICT = dict() 

MAX_WORD_PAGE = ""

MAX_WORD_COUNT = 0

TRAVERSED_COUNT = 0

ROBOTS_TXT = dict()

def writeDataToFiles():
    subdomain_file = open('Logs/Subdomains.log', "w")
    token_file = open('Logs/TokenCount.log', "w")
    max_word_file = open('Logs/MaxWordPage.log', "w")

    sortedSubdomains = sorted(((domain, count) for domain, count in DISCOVERED_SUBDOMAINS.items()), key = (lambda k: (-k[1],k[0])))

    for subdomain, count in sortedSubdomains:
        subdomain_file.write(f'{subdomain} -> {count}\n')

    sortedTokens = sorted(((token, count) for token, count in TOKEN_DICT.items()), key = (lambda k: (-k[1],k[0])))

    for token, count in sortedTokens[:50]:
        token_file.write(f'{token} -> {count}\n')

    max_word_file.write(f'{MAX_WORD_PAGE} -> {MAX_WORD_COUNT}')

    subdomain_file.close()
    token_file.close()
    max_word_file.close()


def updateMaxWordPage(resp):
    global MAX_WORD_COUNT
    global MAX_WORD_PAGE

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    content = soup.get_text()
    tokens = tokenize(content)


    wordCount = len(tokens)

    if wordCount > MAX_WORD_COUNT:
        MAX_WORD_COUNT = wordCount
        MAX_WORD_PAGE = resp.url

def updateTokenDict(resp):
    if resp.status < 200 or resp.status > 399:
        return

    global TOKEN_DICT
    content = resp.raw_response.content
    soup = BeautifulSoup(content, 'html.parser')
    texts = soup.get_text()

    new_dict = computeWordFrequencies(texts)
    TOKEN_DICT = dict(Counter(TOKEN_DICT) + Counter(new_dict))

    updateMaxWordPage(resp)



def scraper(url, resp):
    global DISCOVERED_LINKS
    global TRAVERSED_COUNT

    updateTokenDict(resp)

    # DEBUG/TESTING
    #if (TRAVERSED_COUNT >= 20):
    #    writeDataToFiles()

    links = extract_next_links(url, resp)
    links = [link for link in links if is_valid(link)]

    links_file = open('Logs/DiscoveredLinks.log', "a")
    for link in links:
        url_netloc = urlparse(link).netloc
        if re.search(r'.+[\W]ics\.uci\.edu.*', url_netloc):
            DISCOVERED_SUBDOMAINS[url_netloc] += 1
            #print(f'{url_netloc} -> {DISCOVERED_SUBDOMAINS[url_netloc]}')
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
        
        # First character checks
        if re.match(r'^#.*$', link):                        # Get rid of scroll-to tags
            continue

        if re.search(r'[\d\d\d\d]{2,}-\d\d(?:-\d\d)?', link):                          # ignores calendar/event formats in urls
            continue                                        # i.e : yyyy-mm-dd or yy-mm-dd or mm-dd


        parsed_link = urlparse(link)

        if re.match(r'^\/[^\/].+$', link):                  # First character is / (relative path)
            link = f'{url_scheme}://{url_netloc}{link}'     # Add the scheme and netloc to the beginning link
        elif re.match(r'^\/\/.+$', link):
            link = f'{url_scheme}:{link}'                   # First characters are //  (use same scheme)
                                                            # Add scheme to the beginning of link


        
        link = link.split('?')[0]
        link = link.split('#')[0]

        if link in DISCOVERED_LINKS:
            continue

        for pattern in ACCEPTED_DOMAINS:
            match = re.search(pattern, link)
                
            if match:
                if not ROBOTS_TXT.get(url_netloc):                  #domain is not matched before
                    robotParser = urllib.robotparser.RobotFileParser()   # parse robots.txt and save it in dictionary
                    robotParser.set_url(f'{url_scheme}://{url_netloc}/robots.txt')
                    robotParser.read()
                    ROBOTS_TXT[url_netloc] = robotParser
                    # print(robotParser.site_maps())
                if ROBOTS_TXT[url_netloc].can_fetch('*', link):    # is the link allowed
                    # TO DO: 
                    # figure out number of tokens in each web page
                    # determine if the page has low information value
                    # or if the pages just have no information
                    # 
                    filtered_links.add(link)
                else:
                    disallowLinks_file = open('Logs/DisallowLinks.log', "a")
                    disallowLinks_file.write(link + '\n')
                    disallowLinks_file.close()
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            # added .diff extensions here
            + r"|diff)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
