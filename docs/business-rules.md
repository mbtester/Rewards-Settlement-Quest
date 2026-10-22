# Business rules and assumptions (synthetic, from the Quest brief)

## Rules
| ID | Rule |
|---|---|
| R1 | Settlement runs Tuesday 09:00 UTC. Window = [previous Monday 00:00 UTC, this Monday 00:00 UTC). Lower bound included, upper bound excluded. |
| R2 | Each qualifying (completed) task earns 10 test credits. |
| R3 | Each task ID is counted once. |
| R4 | A retry never creates a second payout. |
| R5 | A notification is sent only after a successful payout. |
| R6 | A notification failure never reverses or blocks a payout. |

## Assumptions (not given in the brief; untested against any real system)
| ID | Assumption |
|---|---|
| A1 | Only `completed` tasks qualify; `completed_at` decides the window. |
| A2 | Timestamps must carry a timezone. Naive timestamps are rejected. |
| A3 | A manual re-run on any day uses the window of the week containing that day. |
| A4 | One payout is identified by user + window start (the idempotency key). |
| A5 | A retry after a failed notification sends the notification once and does not pay again. |
| A6 | Account changes (suspended/closed account) are out of scope. |
| A7 | Credit value per task is fixed at 10; admin changes mid-week are out of scope. |
| A8 | Task data is frozen between a run and its retry; late-arriving tasks are out of scope. |
| A9 | Upstream emits each task ID once and `completed_at` never changes after completion. TC-14 probes what happens if this is wrong. |
