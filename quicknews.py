from bs4 import BeautifulSoup
import requests
import jinja2
import sqlite3
import dateutil.parser
import webbrowser
import mysql.connector

business_insider_url="https://www.businessinsider.com"
tech_url='https://www.businessinsider.com/sai'
fin_url='https://www.businessinsider.com/clusterstock'
stra_url='https://www.businessinsider.com/warroom'
pol_url='https://www.businessinsider.com/politics'
mark_url='https://markets.businessinsider.com/'

tech_tag='Technology'
fin_tag='Finance'
stra_tag='Strategy'
pol_tag='Politics'

class Article:
    '''Article contains title, bullets, date, url, tag'''
    def __init__(self, title, bullets, date, url, tag):
        self.title = title
        self.bullets = bullets
        self.date = date
        self.url = url
        self.tag = tag

    def getValues(self):
        return self.title, self.bullets, self.date, self.url, self.tag

def getInfo(soup, url):
    '''Return title, date, summary dependent on section. BI Market follows diff page format'''
    # starts with markets.business
    if url.startswith(mark_url):
        # strip beg/end whitespaces, escape apostrophes, hyphens w/ html code (for sql/viewing) of title
        title = soup.find('h1', {'class':'article-title'}).getText(strip=True).replace("'", "&#39;").replace("’", "&#39;").replace("—", "&#8208;")
        date = soup.find('span', {'class':'news-post-quotetime'}).getText()
        # find <li> bullet points
        summary = soup.find('div', {'class':'news-content'}).find_all("li")

        return title, date, summary
    else:
        print(url)
        if soup.find('h1', {'class':'post-headline'}) is None:
            title = soup.find('title').getText(strip=True).replace("'", "&#39;").replace("’", "&#39;").replace("—", "&#8208;")
            return title, "0", "Click above to learn more"
        
        title = soup.find('h1', {'class':'post-headline'}).getText(strip=True).replace("'", "&#39;").replace("’", "&#39;").replace("—", "&#8208;")

        # find timestamp in ISO 8601 format e.g. 2019-01-04T23:58:22+0000; remove timezone
        date = soup.find('div', {'class': 'byline-timestamp'})["data-timestamp"].split("+")[0]
        summary = soup.find('ul', {'class':'summary-list'})
        return title, date, summary


def extract_article(url):
    '''Extract an article's title, bullet summary, url, and published date'''
    # get website page
    res = requests.get(url)
    
    # parse website html
    soup = BeautifulSoup(res.text, 'html.parser')
    title, date, summary = getInfo(soup, url)
   
    # Not all articles have a summary
    try:
        bullets = [ bullet.getText().strip() for bullet in summary]
        # escape apostrophes, hyphens w/ html code (for sql/viewing), join w/ * to insert in sql (no [])
        strBullets = "*".join(bullets).replace("'", "&#39;").replace("’", "&#39;").replace("—", "&#8208;")
        return title, strBullets, date
    except:
        return title, "Click above to learn more", date

def import_archive(conn):
    '''Import archived articles from sql database, table NEWS, DESC Order'''
    c = conn.cursor()
    c.execute("SELECT * FROM NEWS ORDER BY DATE DESC")

    news = []
    # Export news from sql archive db in chronological order
    for row in c:
        title, bullets, dateISO, url, tag = row[0], row[1], row[2], row[3], row[4]
        if dateISO is "0":
            article = Article(title, bullets, dateISO, url, tag) #was date?
        else:
            date = dateutil.parser.parse(dateISO) # convert ISO into datetime object
            article = Article(title, bullets, date, url, tag)
        news.append(article)

    return news

def archive_insert(conn, article):
    '''Insert web scraped articles into SQLite3 DB, Table News for archive'''
    c = conn.cursor()
    strTitle, strBullets, date, url, tag = article.getValues()
    
    # insert new article 
    sql_query = """INSERT OR IGNORE INTO NEWS (TITLE, SUMMARY, DATE, URL, TAG) VALUES \
                    ('{}', '{}', '{}', '{}', '{}')""".format(strTitle, strBullets, date, url, tag)
    c.execute(sql_query)
    conn.commit()

def remove_archives(conn):
    '''Remove old articles from sql database'''
    c = conn.cursor()
    c.execute("""DELETE FROM NEWS""")
    conn.commit()
    
def check_table(conn):
    '''Create news table in sql database if none exists'''
    c = conn.cursor()
    sql_query = """CREATE TABLE IF NOT EXISTS NEWS (TITLE TEXT, SUMMARY TEXT, DATE TEXT, URL TEXT, TAG TEXT, UNIQUE(TITLE)) """
    c.execute(sql_query)

def scrape_section(conn, prefix_url, tag):
    '''Extract articles from BI <tag> page'''
    # setup webscrape
    res = requests.get(prefix_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Find <a> headlines on BI Section Page
    article_headlines =  soup.find_all('a', { 'class':'tout-title-link'}) 
    
    # Extract urls of respective <a> headlines
    article_urls = [ a['href'] for a in article_headlines]
  
    # insert articles into sql archive db
    for url in article_urls:
        if "https" not in url:
            url = business_insider_url + url
        title, bullets, date = extract_article(url)
        article = Article(title, bullets, date, url, tag)
        archive_insert(conn, article)

def display_content(news):
    '''Load articles using news template'''
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

def scrape_tech_insider():
    '''Driver function to retrieve articles from BI Tech/Finance/Strategy/Politics page'''
    # create/connect to Archive database
    conn = sqlite3.connect('static/archive.db')
    
    # create table if none exists
    check_table(conn)

    # remove old articles
    remove_archives(conn)
    print("Begin scraping Business Insider")
    print("===============================")
    
    print("Retrieving Technology articles...")
    scrape_section(conn, tech_url, tech_tag)
    print("Retrieving Finance articles...")
    scrape_section(conn, fin_url, fin_tag)
    print("Retrieving Strategy articles...")
    scrape_section(conn, stra_url, stra_tag)
    print("Retrieving Politics articles...")
    scrape_section(conn, pol_url, pol_tag)
    
    # import archived articles
    news = import_archive(conn)
    conn.close()

    # open browser w/ news
    display_content(news)


if __name__ == "__main__":
    scrape_tech_insider()
