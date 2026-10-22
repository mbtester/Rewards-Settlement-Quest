"""CORRECTED reference implementation."""
from .common import NotificationError, settlement_window, qualifying_credits


class SettlementService:
    def __init__(self, ledger, notifier):
        self.ledger, self.notifier = ledger, notifier

    def run(self, tasks, run_at):
        start, end = settlement_window(run_at)
        result = {"paid": {}, "notified": [], "notify_failed": []}
        for user_id, credits in qualifying_credits(tasks, start, end).items():
            key = f"{user_id}|{start.isoformat()}"              # FIX 1: one payout per user per window
            if self.ledger.credit(user_id, credits, key=key):
                result["paid"][user_id] = credits
            if key in self.ledger.notified:
                continue                                         # already told this user
            try:                                                 # FIX 2: contain notification failure
                self.notifier.send(user_id, credits)
            except NotificationError:
                result["notify_failed"].append(user_id)
            else:
                self.ledger.notified.add(key)
                result["notified"].append(user_id)
        return result
