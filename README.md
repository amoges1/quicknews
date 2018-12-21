# QuickNews

A Python application that web scrapes BI Tech articles and generates cards of bit-sized information.

1. Articles are stored as objects, containing:
    - title: The title of the article
    - bullets: The bullet summaries of the article
    - url: The url of the article for more information

2. Beauitful Soup is utilized to scrap news information from websites, particularly identifying:
    - title as <h1 class="post-headline">
    - bullets as <ul class="summary-list">

The default url for scraping the Tech section of BI website is: http://www.businessinsider.com/sai

The program loops through all the headlines/articles of the Tech page. Each headline/article contains a url to their respective article, from which the title and bullet summaries are extracted. With Bootstrap 4 and Jinja2, the articles are aggregated as cards on a single viewable page automatically opened.