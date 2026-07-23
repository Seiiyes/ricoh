## 2026-06-19 - [⚡ Bolt / Performance Optimization]
**Learning:** In the counters API endpoints (`get_user_counters_latest` and `get_latest_counters_with_printer`), individual `db.query(User)` calls were inside loops, causing N+1 query bottlenecks for large payloads.
**Action:** Replaced loop queries with a single batched query using `.in_()` and an O(1) dictionary lookup, significantly reducing the DB load while maintaining the same logical behavior.
