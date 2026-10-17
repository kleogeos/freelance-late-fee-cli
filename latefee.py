#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timezone

STAGES = [
    (0, 0, "not_due", "Invoice not yet overdue."),
    (1, 7, "friendly", "Friendly reminder — assume an oversight."),
    (8, 21, "firm", "Firm follow-up — ask for a specific payment date."),
    (22, 45, "notice", "Notice of late fee — restate amount owed including the fee."),
    (46, None, "final", "Final notice — state next step (pause work / collections)."),
]


def _parse_date(s, label):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        print(f"Invalid {label} date '{s}', expected YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)


def stage_for(days_overdue):
    for lo, hi, key, desc in STAGES:
        if hi is None:
            if days_overdue >= lo:
                return key, desc
        elif lo <= days_overdue <= hi:
            return key, desc
    return "not_due", STAGES[0][3]


def cmd_compute(args):
    due = _parse_date(args.due_date, "--due-date")
    today = _parse_date(args.today, "--today") if args.today else datetime.now(timezone.utc).date()
    if today < due:
        print(f"Not yet due: due {due.isoformat()}, today {today.isoformat()}.", file=sys.stderr)
        sys.exit(1)

    raw_overdue = (today - due).days
    days_overdue = max(0, raw_overdue - args.grace_days)
    if days_overdue <= 0:
        fee = 0.0
    else:
        fee = round(args.amount * (args.rate / 100.0) * (days_overdue / 30.0), 2)
    total = round(args.amount + fee, 2)
    stage_key, stage_desc = stage_for(days_overdue)

    if args.json:
        import json
        print(json.dumps({
            "invoice_amount": round(args.amount, 2),
            "due_date": due.isoformat(),
            "today": today.isoformat(),
            "days_overdue": days_overdue,
            "late_fee_rate_pct_per_month": args.rate,
            "grace_days": args.grace_days,
            "late_fee": fee,
            "total_due": total,
            "stage": stage_key,
        }))
        return

    print(f"Invoice amount:   {args.amount:.2f}")
    print(f"Due date:         {due.isoformat()}")
    print(f"Today:             {today.isoformat()}")
    print(f"Days overdue:      {days_overdue} (after {args.grace_days}-day grace period)")
    print(f"Late fee ({args.rate:g}%/mo): {fee:.2f}")
    print(f"Total due:         {total:.2f}")
    print(f"Stage:             {stage_key} — {stage_desc}")
    if stage_key != "not_due":
        print()
        print("Need the actual email copy for this stage? The free Starter Kit excerpt has all 4:")
        print("https://gist.github.com/kleogeos/845669cc43509b012a0ac2aecac00d0a")


def cmd_stages(args):
    print(f"{'days overdue':>14}  {'stage':<10}  description")
    for lo, hi, key, desc in STAGES:
        rng = f"{lo}+" if hi is None else f"{lo}-{hi}"
        print(f"{rng:>14}  {key:<10}  {desc}")


def main():
    p = argparse.ArgumentParser(prog="latefee", description="Compute a late fee owed on an overdue freelance invoice and which reminder stage to send.")
    sub = p.add_subparsers(dest="command", required=True)

    pc = sub.add_parser("compute", help="Compute late fee + total due for an overdue invoice")
    pc.add_argument("amount", type=float, help="original invoice amount")
    pc.add_argument("--due-date", required=True, help="invoice due date, YYYY-MM-DD")
    pc.add_argument("--today", help="override today's date, YYYY-MM-DD (default: today)")
    pc.add_argument("--rate", type=float, default=1.5, help="late fee rate, percent per month (default 1.5)")
    pc.add_argument("--grace-days", type=int, default=0, help="grace period before fee accrues (default 0)")
    pc.add_argument("--json", action="store_true", help="output JSON instead of plain text")
    pc.set_defaults(func=cmd_compute)

    ps = sub.add_parser("stages", help="List the reminder stages and their day thresholds")
    ps.set_defaults(func=cmd_stages)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
