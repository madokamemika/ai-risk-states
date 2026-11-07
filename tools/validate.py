import json
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from tools.corpus import ROOT, STATE_NAMES, files

KINDS = ('person', 'state', 'joint')


def validators():
    schemas = {path.name: json.loads(path.read_text()) for path in (ROOT / 'schema').glob('*.json')}
    registry = Registry().with_resources((name, Resource.from_contents(s)) for name, s in schemas.items())
    return {kind: Draft202012Validator(schemas[f'{kind}.schema.json'], registry=registry) for kind in KINDS}


def load(kind, validator, errors):
    key = 'code' if kind == 'state' else 'id'
    docs = {}
    for path in files(kind):
        name = path.relative_to(ROOT)
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f'{name}: not valid JSON ({e})')
            continue
        for e in validator.iter_errors(doc):
            errors.append(f'{name}: {"/".join(map(str, e.path)) or "(root)"}: {e.message}')
        if doc.get(key) != path.stem:
            errors.append(f'{name}: file name must be {doc.get(key)}.json')
        docs[doc.get(key)] = doc
    return docs


def dangling(people, states, joints):
    for code in sorted(STATE_NAMES.keys() - states.keys()):
        yield f'states/{code}.json: missing'
    for joint in joints.values():
        for pid in joint.get('people', []):
            if pid not in people:
                yield f'joint/{joint["id"]}.json: unknown person {pid}'
    for state in states.values():
        for item in state.get('items', []):
            for pid in item.get('people', []):
                if pid not in people:
                    yield f'states/{state["code"]}.json: unknown person {pid}'
    for person in people.values():
        for statement in person.get('statements', []):
            if statement.get('joint') and statement['joint'] not in joints:
                yield f'people/{person["id"]}.json: unknown joint {statement["joint"]}'


def main():
    errors = []
    checks = validators()
    people, states, joints = (load(kind, checks[kind], errors) for kind in KINDS)
    errors.extend(dangling(people, states, joints))
    if errors:
        print('\n'.join(errors))
        print(f'\n{len(errors)} problem(s)')
        sys.exit(1)
    print(f'ok: {len(people)} people, {len(states)} states, {len(joints)} joint items')


if __name__ == '__main__':
    main()
