from datetime import datetime, date, time, timezone, timedelta
import pytest
from services.scheduler_service import calculate_next_run

def test_calculate_next_run_once():
    # Base datetime: 2026-07-10 12:00:00 UTC (Friday, day of week = 4)
    base_dt = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Once target: 2026-07-12 at 18:30
    specific_date = date(2026, 7, 12)
    next_run = calculate_next_run(
        frequency="once",
        scheduled_time_str="18:30",
        specific_date=specific_date,
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    assert next_run == datetime(2026, 7, 12, 18, 30, 0, tzinfo=timezone.utc)


def test_calculate_next_run_daily_future_today():
    # Base datetime: 2026-07-10 12:00:00 UTC
    base_dt = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Daily target: 18:00 (which is in the future today)
    next_run = calculate_next_run(
        frequency="daily",
        scheduled_time_str="18:00",
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    assert next_run == datetime(2026, 7, 10, 18, 0, 0, tzinfo=timezone.utc)


def test_calculate_next_run_daily_past_today():
    # Base datetime: 2026-07-10 20:00:00 UTC
    base_dt = datetime(2026, 7, 10, 20, 0, 0, tzinfo=timezone.utc)
    
    # Daily target: 18:00 (which is in the past today, so should run tomorrow)
    next_run = calculate_next_run(
        frequency="daily",
        scheduled_time_str="18:00",
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    assert next_run == datetime(2026, 7, 11, 18, 0, 0, tzinfo=timezone.utc)


def test_calculate_next_run_weekly_future():
    # Base datetime: 2026-07-10 12:00:00 UTC (Friday)
    base_dt = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Weekly target: Sunday (6) at 10:00
    next_run = calculate_next_run(
        frequency="weekly",
        scheduled_time_str="10:00",
        day_of_week=6,
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    # Friday + 2 days = Sunday (July 12)
    assert next_run == datetime(2026, 7, 12, 10, 0, 0, tzinfo=timezone.utc)


def test_calculate_next_run_weekly_past_today():
    # Base datetime: 2026-07-10 12:00:00 UTC (Friday, day 4)
    base_dt = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Weekly target: Friday (4) at 10:00 (which is past today's time 12:00)
    next_run = calculate_next_run(
        frequency="weekly",
        scheduled_time_str="10:00",
        day_of_week=4,
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    # Should schedule for next Friday (July 17)
    assert next_run == datetime(2026, 7, 17, 10, 0, 0, tzinfo=timezone.utc)


def test_calculate_next_run_monthly_future():
    # Base datetime: 2026-07-10 12:00:00 UTC
    base_dt = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Monthly target: Day 15 at 08:00
    next_run = calculate_next_run(
        frequency="monthly",
        scheduled_time_str="08:00",
        day_of_month=15,
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    assert next_run == datetime(2026, 7, 15, 8, 0, 0, tzinfo=timezone.utc)


def test_calculate_next_run_monthly_past():
    # Base datetime: 2026-07-10 12:00:00 UTC
    base_dt = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Monthly target: Day 5 at 08:00 (past for this month, so next month Aug 5)
    next_run = calculate_next_run(
        frequency="monthly",
        scheduled_time_str="08:00",
        day_of_month=5,
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    assert next_run == datetime(2026, 8, 5, 8, 0, 0, tzinfo=timezone.utc)


def test_calculate_next_run_monthly_boundary_cap():
    # Base datetime: 2026-01-10 12:00:00 UTC
    base_dt = datetime(2026, 1, 10, 12, 0, 0, tzinfo=timezone.utc)
    
    # Monthly target: Day 31 at 18:00
    # Next month is February, which has 28 days in 2026. Day 31 should cap to Feb 28.
    next_run = calculate_next_run(
        frequency="monthly",
        scheduled_time_str="18:00",
        day_of_month=31,
        base_dt=base_dt,
        tz=timezone.utc
    )
    
    assert next_run == datetime(2026, 1, 31, 18, 0, 0, tzinfo=timezone.utc)
    
    # If base is Jan 31 19:00 (past Jan 31 18:00), should target next month (February) capped to 28
    base_dt_past = datetime(2026, 1, 31, 19, 0, 0, tzinfo=timezone.utc)
    next_run_feb = calculate_next_run(
        frequency="monthly",
        scheduled_time_str="18:00",
        day_of_month=31,
        base_dt=base_dt_past,
        tz=timezone.utc
    )
    assert next_run_feb == datetime(2026, 2, 28, 18, 0, 0, tzinfo=timezone.utc)
