import datetime
import json
import re
import urllib.request
from collections import Counter

from tools.corpus import ROOT, load, read, write

ARCHIVE = 'https://goveronica.com/data/'
STATE = re.compile(r'^us-[a-z]{2}$')
FRONTIER = re.compile(
    r'frontier|catastrophic|foundation model|critical risk|superintelligen|kill switch|large developer'
    r'|advanced (ai|artificial)|safety and security protocol|artificial intelligence safety|ai safety',
    re.I,
)
REJECTED = ROOT / 'queue/rejected.json'


def archive(name):
    request = urllib.request.Request(ARCHIVE + name, headers={'User-Agent': 'ai-risk-states/1.0'})
    return json.load(urllib.request.urlopen(request, timeout=60))


def code(entry):
    return entry['jurisdiction'][3:].upper()


def tally(entries):
    return dict(sorted(Counter(code(e) for e in entries).items()))


def state_only(sections):
    return [s for s in sections if STATE.match(s['jurisdiction'])]


def is_frontier(bill):
    return FRONTIER.search(bill['title'] + ' ' + bill.get('summary', ''))


def candidates(frontier):
    cited = {item['source'] for state in load('state') for item in state.get('items', [])}
    rejected = set(read(REJECTED)) if REJECTED.exists() else set()
    today = datetime.date.today().isoformat()
    fresh = [b for b in frontier if b['source'] not in cited | rejected]
    queue = [{'state': code(b), 'date': b['date'], 'title': b['title'], 'status': b['status'],
              'summary': b.get('summary', ''), 'source': b['source'], 'found': today} for b in fresh]
    return sorted(queue, key=lambda q: q['date'], reverse=True)


def main():
    bills, laws = archive('legal-bills.json'), archive('legal-index.json')
    state_bills = state_only(bills['sections'])
    frontier = [b for b in state_bills if is_frontier(b)]
    write(ROOT / 'inputs/bill-counts.json', {
        'asof': bills['generated'][:10],
        'bills': tally(state_bills),
        'frontier_bills': tally(frontier),
        'laws': tally(state_only(laws['sections'])),
    })
    queue = candidates(frontier)
    write(ROOT / 'queue/bills.json', queue)
    print(f'{len(state_bills)} state AI bills, {len(frontier)} frontier-risk, {len(queue)} new candidates')


if __name__ == '__main__':
    main()
