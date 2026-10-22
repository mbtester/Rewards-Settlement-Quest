"""FAULTY reference: reproduces QST-001 (duplicate payout on retry)."""
from .common import settlement_window, qualifying_credits


class SettlementService:
    def __init__(self, ledger, notifier):
        self.ledger, self.notifier = ledger, notifier

    def run(self, tasks, run_at):
        start, end = settlement_window(run_at)
        result = {"paid": {}, "notified": [], "notify_failed": []}
        for user_id, credits in qualifying_credits(tasks, start, end).items():
            self.ledger.credit(user_id, credits)        # BUG 1: no idempotency key
            result["paid"][user_id] = credits
            self.notifier.send(user_id, credits)        # BUG 2: failure escapes and aborts the run
            result["notified"].append(user_id)
        return result
