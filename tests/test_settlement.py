from datetime import datetime, timedelta, timezone
import pytest

from rewards.common import Ledger, NotificationError, Task, run_with_retry

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))
RUN_AT = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)      # Tuesday
START = datetime(2026, 10, 12, 0, 0, tzinfo=UTC)       # Monday, included
END = datetime(2026, 10, 19, 0, 0, tzinfo=UTC)         # Monday, excluded


def done(task_id, user, when):
    return Task(task_id, user, "completed", when)


class FlakyNotifier:
    def __init__(self, fail_for=(), fail_times=1):
        self.remaining = {u: fail_times for u in fail_for}
        self.sent = []

    def send(self, user_id, credits):
        if self.remaining.get(user_id, 0) > 0:
            self.remaining[user_id] -= 1
            raise NotificationError("provider timeout")
        self.sent.append(user_id)


class BrokenLedger(Ledger):
    def credit(self, *a, **k):
        raise RuntimeError("ledger unavailable")


def make(impl, notifier=None, ledger=None):
    ledger = ledger or Ledger()
    notifier = notifier or FlakyNotifier()
    return impl.SettlementService(ledger, notifier), ledger, notifier


# ---- core rules: should pass on faulty AND fixed (shows the suite is precise) ----

def test_tc01_happy_path(impl):
    svc, ledger, n = make(impl)
    svc.run([done("t1", "u1", START + timedelta(days=1)),
             done("t2", "u1", START + timedelta(days=2)),
             done("t3", "u1", START + timedelta(days=3))], RUN_AT)
    assert ledger.balance("u1") == 30
    assert n.sent == ["u1"]


def test_tc02_lower_boundary_is_included(impl):
    svc, ledger, _ = make(impl)
    svc.run([done("t1", "u1", START)], RUN_AT)
    assert ledger.balance("u1") == 10


def test_tc03_upper_boundary_excluded_then_paid_next_week(impl):
    svc, ledger, _ = make(impl)
    tasks = [done("t1", "u1", END)]
    svc.run(tasks, RUN_AT)
    assert ledger.balance("u1") == 0                     # not this week
    svc.run(tasks, RUN_AT + timedelta(days=7))
    assert ledger.balance("u1") == 10                    # exactly once, next week


def test_tc04a_ist_timestamp_inside_window_is_paid(impl):
    svc, ledger, _ = make(impl)
    # 2026-10-19 05:00 IST == 2026-10-18 23:30 UTC -> inside
    svc.run([done("t1", "u1", datetime(2026, 10, 19, 5, 0, tzinfo=IST))], RUN_AT)
    assert ledger.balance("u1") == 10


def test_tc04b_ist_timestamp_on_utc_boundary_is_excluded(impl):
    svc, ledger, _ = make(impl)
    # 2026-10-19 05:30 IST == 2026-10-19 00:00 UTC -> excluded
    svc.run([done("t1", "u1", datetime(2026, 10, 19, 5, 30, tzinfo=IST))], RUN_AT)
    assert ledger.balance("u1") == 0


def test_tc05_duplicate_task_id_counted_once(impl):
    svc, ledger, _ = make(impl)
    t = done("t1", "u1", START + timedelta(days=1))
    svc.run([t, t, t], RUN_AT)
    assert ledger.balance("u1") == 10


def test_tc09_payout_failure_means_no_notification(impl):
    svc, _, n = make(impl, ledger=BrokenLedger())
    with pytest.raises(RuntimeError):
        svc.run([done("t1", "u1", START + timedelta(days=1))], RUN_AT)
    assert n.sent == []


def test_tc10_non_completed_tasks_earn_nothing(impl):
    svc, ledger, n = make(impl)
    svc.run([Task("t1", "u1", "pending", None),
             Task("t2", "u1", "cancelled", START + timedelta(days=1))], RUN_AT)
    assert ledger.balance("u1") == 0
    assert n.sent == []


def test_tc13_naive_timestamp_is_rejected(impl):
    svc, ledger, _ = make(impl)
    with pytest.raises(ValueError):
        svc.run([done("t1", "u1", datetime(2026, 10, 14, 12, 0))], RUN_AT)
    assert ledger.balance("u1") == 0


# ---- QST-001 regression: retry / partial failure must never double-pay ----

@pytest.mark.regression
def test_tc06_retry_after_notification_failure_pays_once(impl):
    svc, ledger, n = make(impl, notifier=FlakyNotifier(fail_for=["u1"], fail_times=1))
    run_with_retry(svc, [done("t1", "u1", START + timedelta(days=1))], RUN_AT)
    assert ledger.balance("u1") == 10


@pytest.mark.regression
def test_tc07_rerunning_a_finished_settlement_pays_nothing_new(impl):
    svc, ledger, n = make(impl)
    tasks = [done("t1", "u1", START + timedelta(days=1))]
    svc.run(tasks, RUN_AT)
    svc.run(tasks, RUN_AT)
    assert ledger.balance("u1") == 10
    assert n.sent == ["u1"]                              # and no second notification


@pytest.mark.regression
def test_tc08_notification_failure_does_not_reverse_or_crash(impl):
    svc, ledger, _ = make(impl, notifier=FlakyNotifier(fail_for=["u1"], fail_times=99))
    result = svc.run([done("t1", "u1", START + timedelta(days=1))], RUN_AT)
    assert ledger.balance("u1") == 10
    assert result["notify_failed"] == ["u1"]


@pytest.mark.regression
def test_tc11_retry_delivers_missing_notification_without_repaying(impl):
    svc, ledger, n = make(impl, notifier=FlakyNotifier(fail_for=["u1"], fail_times=1))
    tasks = [done("t1", "u1", START + timedelta(days=1))]
    svc.run(tasks, RUN_AT)                               # payout ok, notify fails
    svc.run(tasks, RUN_AT)                               # retry
    assert ledger.balance("u1") == 10
    assert n.sent == ["u1"]


@pytest.mark.regression
def test_tc12_one_users_notify_failure_does_not_block_others(impl):
    svc, ledger, n = make(impl, notifier=FlakyNotifier(fail_for=["u1"], fail_times=99))
    svc.run([done("t1", "u1", START + timedelta(days=1)),
             done("t2", "u2", START + timedelta(days=1))], RUN_AT)
    assert ledger.balance("u2") == 10
    assert n.sent == ["u2"]

@pytest.mark.xfail(strict=True, reason="known gap: payout key is user+window, not task_id")
def test_tc14_same_task_id_reappearing_in_next_window(impl):
    svc, ledger, _ = make(impl)
    svc.run([done("t1", "u1", START + timedelta(days=1))], RUN_AT)        # week 1
    assert ledger.balance("u1") == 10
    # same task_id re-delivered with a timestamp inside week 2
    svc.run([done("t1", "u1", END + timedelta(days=1))],
            RUN_AT + timedelta(days=7))
    assert ledger.balance("u1") == 10                                      # R3: count each task ID once