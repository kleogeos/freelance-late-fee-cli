# freelance-late-fee-cli

![Test CLI](https://github.com/kleogeos/freelance-late-fee-cli/actions/workflows/test.yml/badge.svg)

Compute the late fee owed on an overdue freelance invoice, and which reminder stage to send (friendly → firm → notice → final). No dependencies, no sign-up — just stdlib Python.

```bash
python3 latefee.py compute 1000 --due-date 2026-09-01 --today 2026-10-17
```

```
Invoice amount:   1000.00
Due date:         2026-09-01
Today:             2026-10-17
Days overdue:      46 (after 0-day grace period)
Late fee (1.5%/mo): 23.00
Total due:         1023.00
Stage:             final — Final notice — state next step (pause work / collections).
```

### Install (optional)

```bash
pip install git+https://github.com/kleogeos/freelance-late-fee-cli
freelance-latefee compute 1000 --due-date 2026-09-01
```

### Commands

| Command | What it does |
|---|---|
| `compute AMOUNT --due-date YYYY-MM-DD [--today DATE] [--rate PCT] [--grace-days N] [--json]` | Late fee + total due + which reminder stage applies |
| `stages` | List the 4 reminder stages and their day-overdue thresholds |

`--rate` is the late fee rate in percent **per month**, prorated by days overdue (default 1.5%/mo — a common contract clause). `--grace-days` is a grace period before the fee starts accruing (default 0).

### Why this instead of doing it by hand

The math is easy to get wrong when you're annoyed at a late-paying client (prorating a monthly rate by days, remembering which threshold means "send the firm one, not the final one"). This just answers both questions in one command, deterministically, so the number in your reminder email is exactly right.

Pairs with:
- [late-fee-calculator](https://kleogeos.github.io/freelancer-tools/late-fee-calculator.html) — same math, browser version, no install
- [freelance-late-fee-js](https://github.com/kleogeos/freelance-late-fee-js) — same math, `npx` instead of `pip`, no install
- [4 late-payment email templates](https://gist.github.com/kleogeos/845669cc43509b012a0ac2aecac00d0a) — free excerpt from the [Freelancer Starter Kit](https://kleogeos.github.io/freelancer-tools/kit.html?src=cli-latefee) (full kit also has proposal, contract, and intake templates)

### Development

```bash
python3 test_latefee.py -v
```

## License

MIT
