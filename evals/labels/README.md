# Human labels — how far to trust the judge

Two maps from the 2026-11-25 runs (one per skill version), each with the judge's classification of
every proposal in `labels.md`. Fill the right-hand columns where you disagree, then:

    python3 evals/judge.py labels=evals/labels

reports **Judge vs human**: the share of proposals you left in the judge's cell, and whether you
agree on M1.

**Fill the answer keys for `codetriage` and `subscription-payments` first** (evals/answer-keys/):
these sheets make you read a map of those repositories, and a key written after reading a map is
graded against it.
