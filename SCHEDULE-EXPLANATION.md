The cron expression `0 20 * * *` is composed of five fields:

- **Minute:** `0` — the job runs when the minute is 0 (at the beginning of the hour).
- **Hour:** `20` — the job runs at the 20th hour of the day, which is 8:00 PM UTC.
- **Day of Month:** `*` — the job runs every day of the month.
- **Month:** `*` — the job runs every month.
- **Day of Week:** `*` — the job runs every day of the week.

So, this cron expression means that the job is scheduled to run once a day at 8:00 PM UTC.
