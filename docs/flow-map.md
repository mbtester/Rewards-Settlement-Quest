# Flow map

```mermaid
flowchart TD
    A[Scheduler: Tue 09:00 UTC] --> B[Compute window: prev Mon 00:00Z to this Mon 00:00Z]
    B --> C[Load tasks]
    C --> D[Keep completed tasks with start <= completed_at < end]
    D --> E[Dedupe by task_id]
    E --> F[Total 10 x tasks per user]
    F --> G[Payout: ledger.credit with key user+window]
    G --> H[Notify user]
    H --> I[Record notified]
    H -. provider error .-> J[Fixed: record notify_failed, keep payout]
    H -. provider error .-> K[Faulty: job crashes, scheduler retries, double payout]
```

## Risk points
1. Window computation (timezone and boundary): TC-02, TC-03, TC-04a/b, TC-13
2. Counting (duplicates, non-qualifying): TC-05, TC-10, TC-14
3. Payout (retry, idempotency): TC-06, TC-07, TC-09
4. Notification (partial failure): TC-08, TC-11, TC-12
