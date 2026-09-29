# Reviewing

For anyone reviewing a pull request here, person or model. Go through it in
order; a pull request merges only when every step passes.

## Candidates from the fetchers

For each entry in `queue/bills.json` or `queue/offices.json`:

1. **Open the source.** If it does not load or does not say what the candidate
   says, reject it.
2. **Is it about frontier or catastrophic AI risk, AI safety, or who regulates
   AI?** Chatbot and child-safety bills count as adjacent. Anything else, reject.
3. **Accept** by editing the corpus: add an item to `states/<CODE>.json`, a
   statement to `people/<id>.json`, or correct an office. Remove the candidate
   from the queue.
4. **Reject** by adding its source URL to `queue/rejected.json` and removing it
   from the queue.

## Any change to the corpus

- **Every statement has a source you opened.** No source, no statement.
- **`quote` means the exact words.** `tools/check_quotes.py` must pass for the
  changed files. A source it cannot fetch (paywall, 403) needs a reviewer to
  confirm the words by hand, and to say so in the pull request.
- **Paraphrase is `urging` or `action`,** in neutral words.
- **Arena:** `federal` if aimed at Congress, federal law, federal agencies or
  preemption of state law; `state` if aimed at the speaker's own state's law,
  courts or enforcement.
- **Current office.** Check the person still holds it; office changes are the
  most common error.
- **Neutral voice.** No adjectives that take a side; people on every side of the
  preemption fight belong here.
- **Mark it reviewed:** set `"review": {"status": "reviewed", "by": "<name or model>", "date": "YYYY-MM-DD"}`
  on each file you checked in full.

`python3 -m tools.validate` and the `check` workflow must pass.
