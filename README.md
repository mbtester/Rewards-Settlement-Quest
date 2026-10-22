# Rewards settlement: duplicate-payout regression (Quest project)

Synthetic fixture for the MUST Quest. It is not a live system and uses no real data.
The service code was written with AI help; see `directive.md` appendix for what I checked and changed.

## Setup (Python 3.10+)
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
pytest --impl=faulty -v     # expected: regression tests fail (QST-001)
pytest --impl=fixed -v      # expected: all pass, TC-14 shows as xfailed (known gap)
```
Note: on the first commit (`red-faulty`) `settlement.py` does not exist yet, so use `--impl=faulty` there.

## Layout
- `src/rewards/`: the small service under test (`settlement_faulty.py` = bug, `settlement.py` = fix, `common.py` = shared logic)
- `tests/`: automated checks (`--impl` switches which version is tested)
- `docs/`: rules, test cases, defect report, release readiness
- `evidence/`: saved test output (before fix, after fix, mutation check)
- `intent.md`, `directive.md`: the Quest submission documents
