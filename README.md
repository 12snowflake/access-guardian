# finspark-26
# Access Guardian — Setup

A prototype that auto-revokes vendor/contractor access when their contract
ends, and flags any attempt to use the account afterward.

## 1. Requirements
- Python 3.10+ (check with `python3 --version`)
- No external database needed — it uses a local SQLite file

## 2. Set up a virtual environment (recommended)
This keeps the project's packages separate from anything else on your machine.

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Create and seed the database
```bash
python seed.py
```
This creates `access_guardian.db` in this same folder and loads 4 sample
accounts (some expired, some active).

## 5. Run the access check
```bash
python checker.py
```
This revokes any account whose contract has ended, logs it to the audit
trail, and simulates a suspicious access attempt.

## 6. View the results
Either:
```bash
python dashboard.py        # prints tables to the terminal
```
or:
```bash
python app.py               # starts a local web dashboard
```
then open **http://127.0.0.1:5000** in a browser.

## Notes
- Re-running `seed.py` wipes and reloads the sample accounts — useful for
  demos, but don't run it if you want to keep real data.
- The database file lives next to these scripts regardless of which folder
  you run the commands from.
- Please copy-paste the video link from slides in a new tab to run the video.
