"""
User Activity — Data Source
============================
Currently returns deterministic mock data.

In production, replace this module's implementation with a real
data source (e.g. analytics DB query, Mixpanel API, ClickHouse).
The interface — a function returning UserActivityData — must stay
the same so the generator and report class require zero changes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyStats:
    date: str
    active_users: int
    new_signups: int
    sessions: int
    avg_session_minutes: float


@dataclass(frozen=True)
class UserActivityData:
    period_label: str
    daily: list[DailyStats]
    total_active_users: int
    total_new_signups: int
    total_sessions: int
    avg_session_minutes: float


def fetch_user_activity_data() -> UserActivityData:
    """
    Return user activity data for the last 7 days.

    TODO (production): Replace with a parameterised analytics query.
        SELECT date, COUNT(DISTINCT user_id) AS active_users,
               COUNT(DISTINCT CASE WHEN is_new THEN user_id END) AS new_signups,
               COUNT(*) AS sessions,
               AVG(duration_seconds) / 60.0 AS avg_session_minutes
        FROM   sessions
        WHERE  date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP  BY date
        ORDER  BY date
    """
    daily = [
        DailyStats("2024-06-10", 1_842, 134, 4_201, 8.4),
        DailyStats("2024-06-11", 2_103, 158, 4_890, 9.1),
        DailyStats("2024-06-12", 1_976, 142, 4_512, 8.7),
        DailyStats("2024-06-13", 2_341, 201, 5_230, 9.8),
        DailyStats("2024-06-14", 2_589, 223, 5_901, 10.2),
        DailyStats("2024-06-15", 1_654, 98,  3_780, 7.9),
        DailyStats("2024-06-16", 1_423, 87,  3_210, 7.3),
    ]

    return UserActivityData(
        period_label="June 10 – 16, 2024",
        daily=daily,
        total_active_users=sum(d.active_users for d in daily),
        total_new_signups=sum(d.new_signups for d in daily),
        total_sessions=sum(d.sessions for d in daily),
        avg_session_minutes=round(
            sum(d.avg_session_minutes for d in daily) / len(daily), 1
        ),
    )
