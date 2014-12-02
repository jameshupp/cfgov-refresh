import sys
import json
import os.path
import requests
import dateutil.parser


def posts_at_url(url):
    
    current_page = 1
    max_page = sys.maxint

    while current_page <= max_page:
        url = os.path.expandvars(url)
        resp = requests.get(url, params={'page':current_page, 'count': '-1'})
        results = json.loads(resp.content) 
        current_page += 1
        max_page = results['pages']
        for p in results['posts']:
            yield p


def documents(name, url, **kwargs):

    for post in posts_at_url(url):
        yield process_initiative(post)


def process_initiative(item):

    del item['comments']
    item['_id'] = item['slug']

    if item['custom_fields'].get('related_office'):
        item['related_office'] = \
            item['custom_fields']['related_office'][0]

    return item