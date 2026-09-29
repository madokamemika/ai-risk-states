import datetime
import json
import urllib.parse
import urllib.request

from tools.corpus import ROOT, STATE_NAMES, load, write

USER_AGENT = 'ai-risk-states/1.0 (https://github.com/madokamemika/ai-risk-states)'

GOVERNORS = '''
SELECT ?stateLabel ?govLabel ?start WHERE {
  ?state wdt:P31 wd:Q35657; p:P6 ?st. ?st ps:P6 ?gov.
  FILTER NOT EXISTS { ?st pq:P582 ?end }
  OPTIONAL { ?st pq:P580 ?start }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}'''

SENATORS = '''
SELECT DISTINCT ?pLabel WHERE {
  ?p p:P39 ?st. ?st ps:P39 wd:Q4416090.
  FILTER NOT EXISTS { ?st pq:P582 ?end }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}'''


def sparql(query):
    url = 'https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': query, 'format': 'json'})
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    return json.load(urllib.request.urlopen(request, timeout=120))['results']['bindings']


def latest_governors():
    latest = {}
    for row in sparql(GOVERNORS):
        state, start = row['stateLabel']['value'], row.get('start', {}).get('value', '')
        if state not in latest or start > latest[state][1]:
            latest[state] = (row['govLabel']['value'], start)
    return {state: name for state, (name, _) in latest.items()}


def sitting_senators():
    return {row['pLabel']['value'] for row in sparql(SENATORS)}


def last_name(name):
    return name.split()[-1].lower()


def same_senator(filed, sitting):
    return last_name(filed) == last_name(sitting) and filed.split()[0][:3] == sitting.split()[0][:3]


def flags(governors, senators):
    for person in load('person'):
        state = STATE_NAMES.get(person['state'] or '')
        if person['office_type'] == 'governor' and state:
            now = governors.get(state)
            if now and last_name(now) != last_name(person['name']):
                yield {'id': person['id'], 'filed_as': person['office'], 'wikidata_says': f'{state} governor is now {now}'}
        if person['office_type'] == 'us_senator' and not any(same_senator(person['name'], s) for s in senators):
            yield {'id': person['id'], 'filed_as': person['office'], 'wikidata_says': 'no open US Senate seat found'}


def main():
    governors, senators = latest_governors(), sitting_senators()
    found = list(flags(governors, senators))
    write(ROOT / 'queue/offices.json', {'checked': datetime.date.today().isoformat(), 'flags': found})
    print(f'{len(governors)} governors, {len(senators)} sitting senators; {len(found)} flag(s)')
    for flag in found:
        print(' ', flag['id'], '-', flag['wikidata_says'])


if __name__ == '__main__':
    main()
