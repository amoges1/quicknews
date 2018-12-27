from bs4 import BeautifulSoup
import requests
import jinja2
import sqlite3
import dateutil.parser
import webbrowser


class Article:
    """Article contains title and bullets."""
    def __init__(self, title, bullets, url, date):
        self.title = title
        self.bullets = bullets
        self.url = url
        self.date = date

    def getValues(self):
        return self.title, self.bullets, self.url, self.date

#
# Extract only Date and Time ISO to readable format 
#
def convertISO(timestamp):
    isoDate = timestamp.split("+")[0]
    dateTime = " ".join(isoDate.split("T"))
    return dateTime

#
# Extract an article's title, bullet summary, published date and url   
#
def extract_article(url):

    # get website page
    res = requests.get(url)
    
    # parse website html
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.find('h1', {'class':'post-headline'})
    strTitle = title.getText(strip=True).replace("'", "''")
    summary = soup.find('ul', {'class':'summary-list'})
   
    timestamp = soup.find('div', {'class': 'byline-timestamp'})["data-timestamp"]
    date = convertISO(timestamp)
    

    # Not all articles have bullets
    if title and summary:

         # convert summary into lists, remove end whitespace
        summary = summary.getText().split(".")[:-1]

        # remove whitespaces in each bullet
        bullets = [ bullet.strip() for bullet in summary]

        # escape apostrophes by replacement
        strBullets = ".".join(bullets).replace("'", "''")
        return strTitle, strBullets, date
    return strTitle, "Click above to learn more", date

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
# Import archived articles in SQLite3 DB, Table NEWS 
#
def import_archive(conn):
    news = []

    c = conn.cursor()
    c.execute("SELECT * FROM NEWS ORDER BY ROWID DESC")

    for row in c:
        title, bullets, url, date = row[0], row[1], row[2], row[3]
        article = Article(title, bullets, url, date)
        news.append(article)

    return news

#
# Remove articles when DB limit of 32 is reached
# 
def remove_archives(conn):
    c = conn.cursor()
    count = c.execute("SELECT COUNT(TITLE) FROM NEWS").fetchone()[0]
    
    # remove old articles
    if(count < 32):
        c.execute("""DELETE FROM NEWS WHERE ROWID > 1 """)
        conn.commit()

#
# Driver function to retrieve articles from BI Tech page
#     
def scrape_tech_insider(url='http://www.businessinsider.com/sai'):
    # connect to Archive database
    conn = sqlite3.connect('static/archive.db')
    
    # remove old articles
    remove_archives(conn)
    
    # setup webscrape
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, 'html.parser')

    # Parse Tech BI page for all articles' urls
    article_links = soup.find_all('a', { 'class':'title'})
    article_urls = [ a['href'] for a in article_links]

    # insert articles into archive
    for url in article_urls:
        title, bullets, date = extract_article(url)
        if title and bullets:
            article = Article(title, bullets, url, date)
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
