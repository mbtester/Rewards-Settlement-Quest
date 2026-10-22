# Release-readiness checklist

- [x] Regression tests fail on the faulty build (evidence/before-fix.txt)
- [x] All tests pass on the fixed build (evidence/after-fix.txt)
- [x] Mutation check: removing the idempotency key turns regression tests red (evidence/mutation-check.txt)
- [x] Boundary and timezone cases covered (TC-02, 03, 04a, 04b)
- [x] Duplicate input covered (TC-05)
- [x] Retry and partial-failure cases covered (TC-06 to TC-09, 11, 12)
- [x] Defect report written (docs/defect-report.md)
- [ ] Cross-window duplicate task ID (TC-14): NOT closed, depends on unverified assumption A9
- [ ] Concurrent runs: NOT tested (in-memory ledger)
- [ ] Datastore unique constraint: NOT verified (no real datastore)
- [ ] Failure injection in staging: NOT done
- [ ] Late-arriving tasks, suspended accounts, credit-value changes: NOT covered (A6 to A8)

## Decision
The faulty build is a no-go. QST-001 is critical, and the 5 regression tests fail on it. The corrected build is a conditional go, in this fictional scope only.

Basis: on the corrected build 14 tests pass and 1 is an expected failure (TC-14, a known gap). The 5 regression tests that fail on the faulty build pass here. When I removed the payout key as a mutation check, those tests failed again, so they would catch the bug if it came back (evidence/mutation-check.txt).

I would not call it ready for a real system. It becomes a go when: (1) a unique constraint on the payout key exists in the real datastore, (2) concurrent runs are tested against it, and (3) failure injection has been run in staging. TC-14 is an accepted risk for now: it only matters if upstream can send the same task ID twice, and I could not verify that. Someone who owns the upstream system should confirm it, or a payout record per task ID should be added.

## Handoff
1. Unzip or clone and follow the README setup.
2. Run both commands from the README and compare with the files in `evidence/`.
3. Next steps: a payout record per task ID with a unique constraint, a concurrency test against a real database, and a contract test for the real notifier.
