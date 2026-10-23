# directive.md: Final working directive

## Objective
Make sure a retry or a notification failure can never cause a second payout in the synthetic rewards settlement flow, and prove it with an automated regression that fails on the faulty build and passes on the fixed one.

## Scope
In: window, boundary and timezone logic, duplicate input, retry and partial failure for the fictional rewards service.
Out: live systems, concurrency, a real datastore, and account-state or admin-setting rules.

## Requirements
1. Rules R1 to R6 and assumptions A1 to A9 as written in `docs/business-rules.md`.
2. At least 8 test cases covering happy path, cut-off boundary, timezone conversion, duplicate input, retry and partial failure. The project has 15 tests (`docs/test-cases.md`).
3. The regression group fails on the faulty build and passes on the fixed build.
4. One defect report with reproduction steps, expected vs actual, severity rationale, root cause, evidence, a proposed fix and the release checks that would block it.
5. A release-readiness checklist with a decision and handoff steps.

## Completion criteria
- [x] before-fix, after-fix and mutation-check outputs saved in `evidence/`
- [x] defect report and checklist complete
- [ ] Loom under 5 minutes
- [x] every link opened and checked for reviewer access

---

## Appendix: Results and handoff

### Artifact links
- Repository: https://github.com/mbtester/Rewards-Settlement-Quest
- Test cases: docs/test-cases.md
- Defect report: docs/defect-report.md
- Release checklist: docs/release-readiness.md
- Evidence: evidence/before-fix.txt, evidence/after-fix.txt, evidence/mutation-check.txt
- Commits/tags: [red-faulty](https://github.com/mbtester/Rewards-Settlement-Quest/commit/71dbcef8e2439d2e613dcdbfa50135fca5b1db45) and [green-fixed](https://github.com/mbtester/Rewards-Settlement-Quest/commit/3120f23c959e120058876c9a11e91932a8e40472)

### How to view and reproduce
Follow README.md. Run `pytest --impl=faulty -v` and `pytest --impl=fixed -v`. The first should show the regression tests failing, the second everything passing.

### Actual results
Faulty: 9 passed, 5 failed, 1 xfailed. Fixed: 14 passed, 1 xfailed. Mutation check (key removed): 2 regression tests failed.

### AI contribution and corrections
- AI produced: the starter project (service, fixtures, first set of tests), the draft test-case table, and first drafts of the documents including this one.
- What I reviewed and checked: 
    1. read the faulty and fixed code line by line
    2. checked on a calendar that 20 Oct 2026 is a Tuesday and the window is 12 to 19 Oct 
    3. checked that 05:30 IST is 00:00 UTC
    4. ran the mutation check
    5. ran the tests myself on my machine
- What I changed or rejected: My first TC-14 used a task that fell outside the second window, so it passed without testing anything. I changed it so the same task ID arrives with a week 2 timestamp and marked it xfail(strict).
- What I wrote or decided myself: the choice of Failure, the test cases, the scores, the severity, the release decision, the TC-14 reasoning, the business rules

### Limitations
- TC-14 and assumption A9: if upstream can send the same task ID twice across weeks, the fix does not stop a second payout. Not verified either way.
- The ledger is in memory, so concurrent runs and database transactions are not tested.
- Late-arriving tasks, suspended accounts and credit-value changes are not covered.
- Everything is synthetic; nothing was tested against a live system.

### Actual effort
6 hours 12 minutes (in progress)
