# Qwen-Worker WORKFLOW

This document describes the step‑by‑step process that the Qwen‑Worker agent follows each execution cycle.

## 1. Startup & Environment Check
1. Verify that the Qwen 8B model binary is reachable (`which qwen` or configured path).
2. Load configuration from `config.yaml` (if present) – contains API endpoints, keys, and schedule intervals.
3. Initialize a logger that writes to `agents/qwen-worker/qwen.log`.

## 2. Heartbeat Check (every 5 minutes)
1. Record current ISO‑8601 timestamp.
2. Write a heartbeat line to `heartbeat.log`:
   ```
   [timestamp] HEARTBEAT OK
   ```
3. If the write fails, trigger escalation (see Escalation Protocol).

## 3. Daily Log Update (once per day at 00:00 local time)
1. Append a line to `daily.log`:
   ```
   [timestamp] DAILY STATUS – OK
   ```
2. Include a short summary of yesterday’s API pulls (number of records, any anomalies).

## 4. API Data Pull
For each configured API (list in `config.yaml` under `apis:`):
1. Send HTTP GET request with appropriate headers/auth.
2. On success (200):
   - Save raw JSON to `data/<api_name>/<date>.json`.
   - Optionally truncate to the most recent 100 records and store a cleaned version in `data/<api_name>/latest.json`.
3. On failure:
   - Retry up to 2 times with exponential back‑off (2 s, 4 s).
   - If still failing, write an entry to `escalations.log` and create `escalate.trigger`.

## 5. File Read/Write Operations
- Any required file reads (e.g., reading last heartbeat) use the built‑in read utility.
- Writes are atomic: write to a temporary file then rename to final target.

## 6. Status Reporting to Khem
1. Compile a short status report:
   - Heartbeat status (last timestamp)
   - Daily log entry count for today
   - API pull results (success/failed count)
2. Write the report to `status/report.txt`.
3. If `escalate.trigger` exists, prepend an **ESCALATION** header.
4. Exit with code 0 on success, non‑zero on unrecoverable error.

## 7. Cleanup & Sleep
- Remove any temporary files in `tmp/`.
- Sleep until next scheduled event (handled by the main scheduler or cron).

---
*Workflow designed for autonomous, low‑impact operation on a local Qwen 8B instance.*