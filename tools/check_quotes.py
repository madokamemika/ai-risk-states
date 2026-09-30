import html
import pathlib
import re
import sys
import urllib.request

from tools.corpus import files, read

TYPOGRAPHY = str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '…': '...', ' ': ' '})
MARKUP = re.compile(r'<script.*?</script>|<style.*?</style>|<[^>]+>', re.S)
USER_AGENT = 'Mozilla/5.0 (ai-risk-states quote check)'


def normalise(text):
    text = html.unescape(text).translate(TYPOGRAPHY).lower()
    text = re.sub(r"[^a-z0-9' ]+", ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def fetch(url, cache={}):
    if url not in cache:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            body = urllib.request.urlopen(request, timeout=30).read()
            # A PDF's text is compressed, so it cannot be searched: report it unverified, not missing.
            cache[url] = None if body.startswith(b'%PDF') else normalise(MARKUP.sub(' ', body.decode('utf-8', 'ignore')))
        except Exception:
            cache[url] = None
    return cache[url]


def targets(args):
    chosen = [pathlib.Path(a) for a in args if a.endswith('.json')]
    return [p for p in chosen if p.exists() and p.parent.name == 'people'] if chosen else files('person')


def main():
    found, unreachable, missing = 0, [], []
    for path in targets(sys.argv[1:]):
        person = read(path)
        for statement in person['statements']:
            if statement['kind'] != 'quote':
                continue
            page = fetch(statement['source'])
            if page is None:
                unreachable.append(f'{person["id"]}: {statement["source"]}')
            elif normalise(statement['text']) in page:
                found += 1
            else:
                missing.append(f'{person["id"]}: "{statement["text"][:70]}" not found at {statement["source"]}')
    print(f'{found} quotes found verbatim, {len(unreachable)} sources unreachable, {len(missing)} not found')
    for line in unreachable:
        print('  unverified', line)
    for line in missing:
        print('  NOT FOUND', line)
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
