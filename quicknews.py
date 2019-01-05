from bs4 import BeautifulSoup
import requests
import jinja2
import sqlite3
import dateutil.parser
import webbrowser


class Article:
    """Article contains title and bullets."""
    def __init__(self, title, bullets, date, url):
        self.title = title
        self.bullets = bullets
        self.date = date
        self.url = url

    def getValues(self):
        return self.title, self.bullets, self.date, self.url

#
# Extract an article's title, bullet summary, url, and published date   
#
def extract_article(url):

    # get website page
    res = requests.get(url)
    
    # parse website html
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.find('h1', {'class':'post-headline'})
    # strip beg/end whitespaces, escape apostrophes, hyphens w/ html code (for sql/viewing)
    strTitle = title.getText(strip=True).replace("'", "&#39;").replace("’", "&#39;").replace("—", "&#8208;")

    # find <li> bullet points
    summary = soup.find('ul', {'class':'summary-list'})
    
    # find timestamp in ISO 8601 format e.g. 2019-01-04T23:58:22+0000
    timestamp = soup.find('div', {'class': 'byline-timestamp'})["data-timestamp"]

    # remove timezone
    date = timestamp.split("+")[0] 
    
    # Not all articles have bullets
    if title and summary:

        # convert summary into lists, switch quotes." to ". and remove last-index whitespace
        listSummary = summary.getText().replace(".\"", "\".").split(".")[:-1]
        # remove/cleanse whitespaces in each bullet
        bullets = [ bullet.strip() for bullet in listSummary]
        # escape apostrophes, hyphens w/ html code (for sql/viewing)
        strBullets = ".".join(bullets).replace("'", "&#39;").replace("’", "&#39;").replace("—", "&#8208;")
        
        return strTitle, strBullets, date

    # No summary, add simple text for return
    return strTitle, "Click above to learn more", date

#
# Import archived articles from sql database, table NEWS, DESC Order
#
def import_archive(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM NEWS ORDER BY DATE DESC")

    news = []
    # Export news from sql archive db in chronological order
    for row in c:
        title, bullets, dateISO, url = row[0], row[1], row[2], row[3]
        date = dateutil.parser.parse(dateISO) # convert ISO into datetime object
        article = Article(title, bullets, date, url)
        news.append(article)

    return news

#
# Insert web scraped articles into SQLite3 DB, Table News for archive
#
def archive_insert(conn, article):
    c = conn.cursor()
    strTitle, strBullets, date, url = article.getValues()
    
    # insert new article 
    sql_query = """INSERT OR IGNORE INTO NEWS (TITLE, SUMMARY, DATE, URL) VALUES ('{}', '{}', '{}', '{}')""".format(strTitle, strBullets, date, url)
    c.execute(sql_query)
    conn.commit()

#
# Remove old articles from sql database
# 
def remove_archives(conn):
    c = conn.cursor()
    c.execute("""DELETE FROM NEWS""")
    conn.commit()
       
def check_table(conn):
    c = conn.cursor()
    sql_query = """CREATE TABLE IF NOT EXISTS NEWS (TITLE TEXT, SUMMARY TEXT, DATE TEXT, URL TEXT, UNIQUE(TITLE)) """
    c.execute(sql_query)

#
# Driver function to retrieve articles from BI Tech page
#     
def scrape_tech_insider(url='http://www.businessinsider.com/sai'):
    # create/connect to Archive database
    conn = sqlite3.connect('static/archive.db')
    
    # create table if none exists
    check_table(conn)

    # remove old articles
    remove_archives(conn)
    
    # setup webscrape
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Find <a> headlines on BI Tech Page
    article_headlines = soup.find_all('a', { 'class':'title'})
    # Extract urls of respective <a> headlines
    article_urls = [ a['href'] for a in article_headlines]

    # insert articles into sql archive db
    for url in article_urls:
        title, bullets, date = extract_article(url)
        article = Article(title, bullets, date, url)
        archive_insert(conn, article)
    
    # import archived articles
    news = import_archive(conn)

    conn.close()

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

if __name__ == "__main__":
    scrape_tech_insider()
