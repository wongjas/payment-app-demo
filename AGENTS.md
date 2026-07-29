# AGENTS.md

## Cursor Cloud specific instructions

This is a simple Python Flask app ("SecurePay - Fake Payment App") with a vanilla HTML/CSS/JS frontend. No database, no Docker, no Node.js required.

### Services

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| Flask dev server | `python3 app.py` | 5000 | Serves both API and static frontend; runs in debug mode with auto-reload |

### Key commands

- **Install deps:** `pip install -r requirements.txt` (also install `flake8` for linting)
- **Lint:** `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` (critical errors only; CI uses `continue-on-error`)
- **Test:** `pytest test_app.py -v --cov=app --cov-report=term-missing`
- **Run:** `python3 app.py` (opens on http://localhost:5000)

### Caveats

- Use `python3` not `python` — the system may not have `python` symlinked.
- Payments are stored in-memory only; restarting the server clears all transactions.
- The app has a 10% random payment failure rate built in for demo purposes.
- The `time.sleep(1)` in `process_payment` adds a 1-second delay per payment (including in tests).
