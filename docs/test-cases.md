# Test cases

| ID | Category | Input | Expected outcome | Faulty (actual) | Fixed (actual) |
|---|---|---|---|---|---|
| TC-01 | Happy path | 3 completed tasks mid-window, one user | 30 credits, 1 notification | PASSED | PASSED |
| TC-02 | Boundary | completed exactly Mon 12 Oct 00:00Z | paid (lower bound included) | PASSED | PASSED |
| TC-03 | Boundary | completed exactly Mon 19 Oct 00:00Z | not paid this run; paid once next week | PASSED | PASSED |
| TC-04a | Timezone | 19 Oct 05:00 IST (= 18 Oct 23:30Z) | paid | PASSED | PASSED |
| TC-04b | Timezone | 19 Oct 05:30 IST (= 19 Oct 00:00Z) | not paid | PASSED | PASSED |
| TC-05 | Duplicate | same task ID three times | 10 credits | PASSED | PASSED |
| TC-06 | Retry | notification fails once, scheduler retries | balance 10 | FAILED, 20 | PASSED |
| TC-07 | Retry | run finished settlement again | no new credit, no second notification | FAILED | PASSED |
| TC-08 | Partial failure | payout OK, notification always fails | balance 10, no crash, failure recorded | FAILED | PASSED |
| TC-09 | Partial failure | ledger write fails | no notification sent | PASSED | PASSED |
| TC-10 | Negative | pending and cancelled tasks | 0 credits, no notification | PASSED | PASSED |
| TC-11 | Retry | notification fails, then retry | balance 10, notification sent once | FAILED | PASSED |
| TC-12 | Partial failure | user 1 notification fails, user 2 fine | user 2 still paid and notified | FAILED | PASSED |
| TC-13 | Input | naive timestamp | rejected, nothing paid | PASSED | PASSED |
| TC-14 | Known gap (A9) | same task ID reappears with a week-2 timestamp | balance stays 10 (R3) | PASSED | xFAILED, 20 |
