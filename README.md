# QuickNews

A Python/SQLite3 program that web scrapes BI Technology, Finance, Strategy and Politics articles, archives them in a NEWS database, and generates cards of bit-sized information.

1. Articles are stored as objects, containing:
    - title: The title of the article
    - bullets: The bullet summaries of the article
    - url: The url of the article for more information
    - date: The published date of the article
    - tag: The type of article e.g. Tech, Finance

2. Beauitful Soup is utilized to scrap news information from websites, particularly identifying:
    - title as h1 tags with class="post-headline" or class="article-title"
    - bullets as ul tags with class="summary-list" or by indexing
    - date as div tags with class="byline-timestamp" and attribute "data-timestamp" or class="news-post-quotetime"

The urls for scraping the respective sections of BI website are: 
    - Technology: http://www.businessinsider.com/sai
    - Finance: https://www.businessinsider.com/clusterstock
    - Strategy: https://www.businessinsider.com/warroom
    - Politics: https://www.businessinsider.com/politics

The program runs through the headlines of the various sections, retrieving its respective url to its article, from which the title and bullet summaries are extracted. With Bootstrap 4 and Jinja2, the articles are aggregated as cards in chronological order onto a single viewable page automatically opened. 

With Power of Python, running "python quicknews.py" starts the fun...

![image](https://user-images.githubusercontent.com/17581500/89742023-393b6500-da64-11ea-9aac-8a12d2f92c1a.png)

![image](https://user-images.githubusercontent.com/17581500/89742004-0f823e00-da64-11ea-91d0-2717ff5891c5.png)

"This is a personal project made for fun. All Respective icons and service(s) belong to Respective owners."
