"""Shared pieces of the fictional rewards-settlement service (synthetic, assessment rules only).

Business rules:
  R1  Run Tuesday 09:00 UTC. Window = [previous Monday 00:00 UTC, this Monday 00:00 UTC).
      Lower bound included, upper bound excluded.
  R2  Each qualifying (status == "completed") task earns 10 test credits.
  R3  A task_id is counted once.
  R4  A retry must never create a second payout for the same user + window.
  R5  Notify only after a successful payout.
  R6  A notification failure must never reverse or block a payout.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
CREDITS_PER_TASK = 10


class NotificationError(Exception):
    """Raised by a notifier when delivery fails (provider timeout, 5xx, ...)."""


@dataclass(frozen=True)
class Task:
    task_id: str
    user_id: str
    status: str                      # "completed" | "pending" | "cancelled"
    completed_at: datetime | None = None


class Ledger:
    """In-memory stand-in for the payout ledger.

    credit(key=None)  -> append-only, no duplicate protection (what the faulty code uses)
    credit(key="...") -> idempotent: a second call with the same key is a no-op
    """

    def __init__(self):
        self.entries = []            # (key, user_id, credits)
        self._keys = set()
        self.notified = set()        # payout keys whose notification was delivered

    def credit(self, user_id, credits, key=None):
        if key is not None and key in self._keys:
            return False
        if key is not None:
            self._keys.add(key)
        self.entries.append((key, user_id, credits))
        return True

    def balance(self, user_id):
        return sum(c for _, u, c in self.entries if u == user_id)


def settlement_window(run_at):
    """Return (start, end) in UTC: start inclusive, end exclusive."""
    if run_at.tzinfo is None:
        raise ValueError("run_at must be timezone-aware")
    run_utc = run_at.astimezone(UTC)
    this_monday = (run_utc - timedelta(days=run_utc.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return this_monday - timedelta(days=7), this_monday


def qualifying_credits(tasks, start, end):
    """Credits per user for completed tasks inside [start, end), each task_id counted once."""
    seen, totals = set(), {}
    for t in tasks:
        if t.status != "completed" or t.completed_at is None:
            continue
        if t.completed_at.tzinfo is None:
            raise ValueError(f"naive timestamp on task {t.task_id}")
        ts = t.completed_at.astimezone(UTC)
        if not (start <= ts < end) or t.task_id in seen:
            continue
        seen.add(t.task_id)
        totals[t.user_id] = totals.get(t.user_id, 0) + CREDITS_PER_TASK
    return totals


def run_with_retry(service, tasks, run_at, attempts=3):
    """Scheduler behaviour: if the job raises, run the whole job again."""
    last = None
    for _ in range(attempts):
        try:
            return service.run(tasks, run_at)
        except Exception as exc:     # mirrors a generic scheduler retry
            last = exc
    raise last
