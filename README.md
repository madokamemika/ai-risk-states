# AI risk, state by state

What each US state, and the people who govern it, have said or done about
frontier-AI risk, and what each of them can do about it. This is the corpus
behind [goveronica.com/ai-risk-states.html](https://goveronica.com/ai-risk-states.html);
the page fetches `dist/ai-risk-states.json` from this repository on load.

## What is in it

| Folder | One file per | Holds |
|---|---|---|
| `people/` | policymaker | office, party, committees, and every statement: a verbatim quote, an urging or an action, each with its source |
| `states/` | state and DC | what the state has done on AI risk, and a brief: its own push, compute and data centers, pushback, universities, its members of Congress |
| `joint/` | bill, letter, order or lawsuit | who shares it, for linking people |
| `queue/` | nothing published | candidates found by the fetchers, waiting for review |
| `dist/` | built output | the single file the page reads |

Every statement and every brief section cites a source. A statement filed as a
`quote` must appear word for word at its source; CI checks that on every pull
request.

Entries marked `"review": {"status": "unreviewed"}` came from a research pass in
September 2026 and have not yet been reviewed. Treat them accordingly, and see
below to help.

## Four fields to get right

- **`kind`** on a statement: `quote` is the speaker's exact words, found verbatim
  at the source; `urging` and `action` are paraphrase.
- **`arena`** on a statement: `federal` if aimed at Congress, federal law, federal
  agencies or preemption; `state` if aimed at the speaker's own state.
- **`xrisk`** on a state: `acted` for a law, executive order or enforcement action
  aimed at frontier risk; `direct` for letters, statements or pending bills on it;
  `adjacent` for AI safety short of catastrophic risk; `none` for nothing on record.
- **`left_office`** on a person: the date they left the office named in `office`.
  Their record stays, since what they said and did while in office is still on
  the record, but the page stops listing the powers of an office they no longer hold.

## How things get in

1. **Fetchers** (`fetchers/`, weekly, no LLMs) read public data and write only to
   `queue/` and `inputs/`: state AI bills from the
   [AI Law Archive](https://goveronica.com/legal-reader.html) (LegiScan and govinfo),
   and office changes from Wikidata.
2. They open a pull request of candidates.
3. A reviewer follows [REVIEW.md](REVIEW.md): accepted candidates become corpus
   entries; rejected ones go to `queue/rejected.json` so they are not proposed again.
4. On merge, `tools/build.py` rebuilds `dist/` and the page picks it up.

You can also open a pull request by hand: add or correct a file in `people/`,
`states/` or `joint/`, and run `python3 -m tools.validate` and
`python3 -m tools.check_quotes <files>` first. With no files, the quote check
reads every quote in the corpus. A source it cannot fetch is reported as
unverified rather than failed, and a reviewer confirms those words by hand.

## Counts, not a score

The page never combines anything into a single number. The map is coloured by
the most each state has done on frontier-AI risk (`xrisk` in `states/*.json`:
acted, spoke, AI safety only, nothing on record), and each state shows four
raw counts:

- **Public statements:** quotes and urgings on record from its officials.
- **State actions:** laws, bills, lawsuits, executive orders and vetoes filed for
  the state, plus actions its officials took at home.
- **Federal-facing actions:** actions its officials aimed at Washington, and the
  letters and bills to Congress they signed.
- **AI bills this session:** every AI bill introduced in its legislature.

## Licence

The corpus text we wrote is MIT (see [LICENSE](LICENSE)). Quotes are short
excerpts of their speakers' words, attributed and linked. Portraits keep the
licence recorded beside each one. Bill data is provided by LegiScan.
