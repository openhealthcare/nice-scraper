#!/usr/bin/env python
import collections
import re
import requests
import time
from lxml.html import fromstring
from urlparse import urljoin

title_rx = re.compile('(.*)\((.*)\)')

content = collections.defaultdict(list)

def process_page(url, data):
    print url
    time.sleep(0.5)
    html = requests.get(url).content
    page = fromstring(html)
    try:
        href = page.cssselect('.track-event')[0]
    except:
        print "No download found on ", url
        import sys; sys.exit(0)
    link = urljoin('http://www.nice.org.uk', href.get('href'))

    crumbs = page.cssselect('#guidance-breadcrumb li')
    cat = crumbs[-2].text_content().strip()

    data['url'] = link
    content[cat].append(data)

html = requests.get("http://www.nice.org.uk/guidance/published?type=Guidelines").content
page = fromstring(html)
rows = page.cssselect(".rowlink tr")
for row in rows:
    title = row[0][0].text_content()
    title, code = title_rx.match(title).groups()
    if not code.strip().startswith('CG'):
        continue

    href = urljoin('http://www.nice.org.uk', row[0][0].get('href'))
    date = row[1].text_content()
    data = {
        'code': code,
        'title': title,
        'date': date
    }
    process_page(href, data)

print content




"""
<guidelines><provider name="NICE"><category name="Blood and immune system"><guideline category="Blood and immune system" code="CG114" subcategory=""><url>
          http://www.nice.org.uk/nicemedia/live/13329/52853/52853.pdf
        </url><title>
          Anaemia management in people with chronic kidney disease
        </title></guideline>
"""