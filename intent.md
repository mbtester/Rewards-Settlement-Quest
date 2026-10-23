# intent.md: Why this problem?

## Why this problem
I picked the duplicate payout on retry because it is the failure where a small mistake costs real money and nobody sees it happen. A user simply has more credits than they should, and it only shows up in reconciliation. Retries and idempotency are also a familiar weak spot in payment-style systems, so I wanted to test it properly rather than pick an easy one.

## Failures I considered
| # | Failure | Impact (1-5) | Likelihood (1-5) | Effort (1-5) | Score |
|---|---|---|---|---|---|
| F1 | Retry after notification failure pays the user twice | 5 | 3 | 3 | 24 |
| F2 | Window computed in local/server time instead of UTC | 4 | 3 | 3 | 21 |
| F3 | Notification failure rolls back or blocks the payout | 4 | 3 | 3 | 21 |
| F4 | Duplicate task IDs from client retries counted twice | 3 | 4 | 2 | 21 |
| F5 | Boundary: task at Monday 00:00 UTC paid twice or never | 4 | 2 | 2 | 20 |

Score = Impact x 3 + Likelihood x 2 + (6 - Effort), so low effort scores higher. The numbers are my own judgment, not measured data. I weighted impact the most because a wrong payout is hard to undo.

## Why F1 ranked first
It has the highest impact (money, silent, hard to claw back) and it repeats: every notification outage can trigger it. It is also testable in a small fixture, which fits a 6 to 8 hour effort. It touches three of the brief's rules at once (retry, partial failure, notification after payout), so one fix and one set of tests cover a lot. F2 and F5 are still in the suite as test cases (TC-02, 03, 04a, 04b), and F4 is TC-05, so the other failures were not dropped, only not chosen as the main one.

## Uncertainty
This is a fictional service. I have no incident history and I am not claiming any. The likelihood scores are my estimate. The fixture shows that the failure can happen if the code is written this way. It does not show how often it would happen in a real system.

## Affected users
The people receiving rewards (they get overpaid), support staff who handle disputes and clawbacks, and finance, who reconcile the ledger.

## Evidence
What I have: a reproducible fixture where the faulty version pays 20 instead of 10 and the fixed version pays 10, with saved test output for both. 
What I do not have: any real incident data, real users or a real notification provider. Everything here is synthetic.

## Intended value
A regression check that fails if anyone reintroduces the bug, and a short list of release checks a team could adopt for any money-moving job.

## Non-goals
Live systems, load or concurrency testing, UI, real notification providers, and account-state or admin-setting rules.
