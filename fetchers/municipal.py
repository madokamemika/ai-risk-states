"""Weekly municipal-AI candidate fetcher (no LLMs).

Cities and counties are acting on AI — superintelligence bans like Bloomington's
Ordinance 2026-29, AI moratoria, data-center siting freezes — and none of that
reaches the state-bill archive the other fetcher reads. There is no unified API
for municipal ordinances, so this reads NEWS instead: it queries NewsAPI across a
broad keyword set (not just "superintelligence ban", which would only catch
Bloomington clones), keeps the results that pair a municipal locus with an AI or
compute hook, and writes de-duplicated candidates to queue/municipal.json for a
human to review per REVIEW.md. Nothing it writes is published.

Key: NEWSAPI_KEY in the environment (a free newsapi.org key, set as a repo secret
for the weekly workflow). Without it the fetcher skips and leaves the queue
untouched — the same way the LegiScan stage degrades — so it never wipes data.
To swap NewsAPI for Google Programmable Search, only fetch() changes; the query
set, the relevance filter and the queue shape stay.
"""
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request

from tools.corpus import ROOT, load, read, write

QUEUE = ROOT / 'queue/municipal.json'
REJECTED = ROOT / 'queue/rejected.json'
ENDPOINT = 'https://newsapi.org/v2/everything'

# Broad on purpose: each query pairs a municipal/local hook with an AI or compute
# hook so the result set stays about local AI action rather than AI news at large.
QUERIES = [
    '"superintelligence ban" OR "ban artificial superintelligence" OR "AGI moratorium"',
    '"AI moratorium" AND (city OR county OR council OR ordinance)',
    '("AI ordinance" OR "artificial intelligence ordinance") AND (city OR county OR council)',
    '"data center moratorium" OR "data center ban" OR "data center zoning" OR "data center freeze"',
    '("facial recognition ban" OR "predictive policing" OR "surveillance ordinance") AND ordinance',
    '("city council" OR "county board" OR "board of supervisors" OR "common council") AND ("artificial intelligence" OR superintelligence OR "data center")',
]

# A candidate must read as a LOCAL body doing something about AI/compute.
MUNICIPAL = re.compile(
    r'\b(city council|common council|town council|county (board|commission|supervisors)'
    r'|board of supervisors|aldermen|selectmen|city of|county of|municipal|ordinance|mayor)\b', re.I)
AI = re.compile(
    r'\b(artificial intelligence|superintelligen|\bAGI\b|data ?center|algorithm|facial recognition'
    r'|predictive policing)\b|\bAI\b', re.I)


def fetch(query, days=30, pages=1):
    """Return NewsAPI articles for a query. The key is sent as a header so a proxy
    can inject it from a dummy value in testing; in CI it is the real secret."""
    key = os.environ['NEWSAPI_KEY']
    frm = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    out = []
    for page in range(1, pages + 1):
        params = urllib.parse.urlencode({
            'q': query, 'language': 'en', 'sortBy': 'publishedAt',
            'from': frm, 'pageSize': 50, 'page': page,
        })
        request = urllib.request.Request(
            f'{ENDPOINT}?{params}',
            headers={'User-Agent': 'ai-risk-states/1.0', 'X-Api-Key': key})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        if data.get('status') != 'ok':
            raise RuntimeError(f"NewsAPI error: {data.get('code')} {data.get('message')}")
        out.extend(data.get('articles', []))
        if len(data.get('articles', [])) < 50:
            break
    return out


def cited_sources():
    sources = set()
    for state in load('state'):
        for item in state.get('items', []):
            sources.add(item['source'])
    for person in load('person'):
        for statement in person.get('statements', []):
            sources.add(statement['source'])
    for item in load('joint'):
        if item.get('source'):
            sources.add(item['source'])
    return sources


def relevant(article):
    text = f"{article.get('title') or ''} {article.get('description') or ''}"
    return bool(MUNICIPAL.search(text) and AI.search(text))


def main():
    if not os.environ.get('NEWSAPI_KEY'):
        print('[municipal] NEWSAPI_KEY not set; skipping (queue left unchanged)')
        return
    existing = read(QUEUE) if QUEUE.exists() else []
    seen = {c['source'] for c in existing} | cited_sources()
    seen |= set(read(REJECTED)) if REJECTED.exists() else set()
    found = datetime.date.today().isoformat()
    queue, added = list(existing), 0
    for query in QUERIES:
        try:
            articles = fetch(query)
        except Exception as error:
            print(f'[municipal] query failed ({query[:40]}…): {error}')
            continue
        for article in articles:
            url = article.get('url')
            if not url or url in seen or not relevant(article):
                continue
            seen.add(url)
            queue.append({
                'date': (article.get('publishedAt') or '')[:10],
                'title': article.get('title') or '',
                'summary': article.get('description') or '',
                'source': url,
                'outlet': (article.get('source') or {}).get('name') or '',
                'found': found,
            })
            added += 1
        time.sleep(1)
    queue.sort(key=lambda candidate: candidate.get('date', ''), reverse=True)
    write(QUEUE, queue)
    print(f'[municipal] {added} new candidates; {len(queue)} in queue/municipal.json')


if __name__ == '__main__':
    main()
