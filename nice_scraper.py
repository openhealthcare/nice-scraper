#!/usr/bin/env python
import collections
import re
import copy
import requests
import time
from lxml.html import fromstring
from urlparse import urljoin
from picklecache import cache
import pickle_warehouse.serializers

title_rx = re.compile('(.*)\((.*)\)')

content = collections.defaultdict(list)


@cache('~/.http')
def get(url):
    return requests.get(url).content

def process_page(href, data):
    html = get(href)
    page = fromstring(html)
    try:
        href = page.cssselect('.track-event')[0]
    except:
        return

    link = urljoin('http://www.nice.org.uk', href.get('href'))

    crumbs = page.cssselect('#guidance-breadcrumb li')
    cat = crumbs[-2].text_content().strip()

    data['url'] = link.encode('utf-8')
    data['category'] = cat.decode('latin1').encode('utf-8')
    content[cat].append(data)

def process():
    html = get("http://www.nice.org.uk/guidance/published?type=Guidelines")
    page = fromstring(html)
    rows = page.cssselect(".rowlink tr")
    for row in rows:
        title = row[0][0].text_content().encode('utf-8')
        title, code = title_rx.match(title).groups()
        if not code.strip().startswith('CG'):
            continue

        href = urljoin('http://www.nice.org.uk', row[0][0].get('href'))
        date = row[1].text_content()
        data = {
            'code': code.strip(),
            'title': title.strip().decode('utf-8'),
            'date': date.strip(),
        }
        process_page(href, data)

process()
keys = sorted(content.keys())
print u'<?xml version="1.0" encoding="utf-8"?>'
print u'<guidelines>'
print u'<provider name="NICE">'
for key in keys:
    print u'<category name="%s">' % key
    for g in content[key]:
        print (u'''   <guideline category="%s" code="%s" subcategory="">
                <url>%s</url>
                <title>%s</title>
            </guideline>''' % (g['category'], g['code'], g['url'], g['title'])).encode('utf-8')

    print u'</category>'
print u'</provider>'
print u'</guidelines>'
