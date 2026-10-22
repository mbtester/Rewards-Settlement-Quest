# Defect report QST-001

**Title:** Settlement pays a user twice when the job is retried after a notification failure
**Environment:** local synthetic fixture, `src/rewards/settlement_faulty.py`
**Severity:** Critical (S1)

**Severity rationale:** This moves money, and it moves it the wrong way without any error being shown to anyone. The user just sees a higher balance, so nobody notices until reconciliation or a complaint. It also repeats: every time the notification provider has a bad moment, the job crashes, the scheduler retries, and the payout happens again. I rate the impact as high. The likelihood is my estimate only, because this is a fictional service and I have no incident data.

## Steps to reproduce
1. `pytest --impl=faulty -v -k tc06`
2. Manual equivalent: u1 has one completed task inside the window, the notifier fails once for u1, and the scheduler retries the whole job.

## Expected
u1 ends with 10 credits and gets one notification.

## Actual
u1 ends with 20 credits.

## Root cause
Two faults in `SettlementService.run` work together:
1. `ledger.credit(...)` is called without an idempotency key, so running the job again credits again.
2. `notifier.send(...)` is not contained. Its exception leaves `run`, the scheduler sees a failed job and retries it, and fault 1 pays again.

Fixing only one is not enough. A key without containment still lets one user's notification error stop everyone after them (TC-12). Containment without a key still double-pays on any manual re-run (TC-07).

## Evidence
- `evidence/before-fix.txt`
- `evidence/after-fix.txt`
- `evidence/mutation-check.txt`
- `git diff red-faulty green-fixed`

## Proposed fix
Give each payout a key made of user + window start so a repeat is a no-op. Catch `NotificationError`, record it as failed, and on a retry send only the missing notification without paying again.

## Release checks that would block this
1. The regression group (`pytest -m regression`) must be green in CI.
2. A staging failure-injection run: make the notifier fail, then retry the job.
3. A reconciliation check: ledger credits per user per window must equal 10 x qualifying tasks.
4. A unique constraint on the payout key in the real datastore.
5. An alert when any user has more than one payout in a window.
6. A review checklist question for any code that moves money: is this idempotent?
