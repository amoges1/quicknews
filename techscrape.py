from bs4 import BeautifulSoup
import requests
import jinja2
import webbrowser

class Article:
    """Article contains title and bullets."""
    def __init__(self, title, bullets, url):
        self.title = title
        self.bullets = bullets
        self.url = url

def extract_article(url):

    # get website page
    res = requests.get(url)

    # parse website html
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.find('h1', {'class':'post-headline'})
    bullets = soup.find('ul', {'class':'summary-list'})

    # Not all articles have bullets
    if title and bullets:
        return title.getText(), bullets
    return title.getText(), "Click to learn more"


def scrape_tech_insider(url='http://www.businessinsider.com/sai'):
    # print("Now loading today's articles...")
    
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, 'html.parser')

    # Parse Tech BI page for all articles' urls
    article_links = soup.find_all('a', { 'class':'title'})
    article_urls = [ a['href'] for a in article_links]

    news = []
    for url in article_urls:
        title, bullets = extract_article(url)
        # print(bullets)
        if title and bullets:
            article = Article(title, bullets, url)
            news.append(article)

    # for articles in news:
    #     print(articles.title)

    # Jinja2 setup
    env = jinja2.Environment()
    env.loader = jinja2.FileSystemLoader(r'templates')

    # Pass article objects to news container
    template = env.get_template('news.html')
    completed_page = template.render(news = news)

    # copy news container to new file
    wfh = open('article.html', 'w')
    wfh.write(completed_page)
    wfh.close()

    # open new file filled with articles
    webbrowser.open('article.html')

scrape_tech_insider()
