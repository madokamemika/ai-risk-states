import datetime
import sys

from tools.corpus import ROOT, load, read, write

DIST = ROOT / 'dist/ai-risk-states.json'


def assemble():
    people = load('person')
    counts = read(ROOT / 'inputs/bill-counts.json')
    return {
        'generated': datetime.date.today().isoformat(),
        'bill_counts_asof': counts['asof'],
        'bill_counts': counts['bills'],
        'people': sorted(people, key=lambda p: p['name'].split()[-1]),
        'states': load('state'),
        'joint': sorted(load('joint'), key=lambda j: j['date']),
    }


def main():
    corpus = assemble()
    if '--check' in sys.argv:
        print('build ok')
        return
    write(DIST, corpus, indent=1)
    statements = sum(len(p['statements']) for p in corpus['people'])
    print(f'wrote {DIST.relative_to(ROOT)}: {len(corpus["people"])} people, {statements} statements')


if __name__ == '__main__':
    main()
