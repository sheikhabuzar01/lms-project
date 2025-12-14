# Library Management System (Python)

A modular Python library management system with both a desktop GUI and a responsive web frontend.

Brief overview
--------------
- Core modules: `book.py`, `member.py`, `library.py`, `issue_return.py`, `search.py`
- Persistence: `storage.py` (JSON file `library_db.json`)
- Auth helpers: `auth_system.py`
- Desktop GUI: `gui.py` (tkinter)
- Web UI + API: `webapp.py` (Flask) with templates in `templates/` and assets in `static/`
- Tests: `test_library.py` (unittest)

Quick start
-----------
1. Create and activate a venv (recommended):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1  # PowerShell
# or: .\\.venv\\Scripts\\activate  # cmd.exe
```

2. Install dependencies (Flask for webapp):

```powershell
pip install -r requirements.txt 2>nul || pip install flask
```

Run the desktop GUI:

```powershell
python gui.py
```

Run the web application:

```powershell
set FLASK_APP=webapp.py
flask run
# then open http://127.0.0.1:5000
```

Alternatively you can start the Flask app directly with Python:

```powershell
python webapp.py
```

Run tests:

```powershell
python -m unittest test_library.py
```

Notes
-----
- `library_db.json` stores the app data; back it up before large experiments.
- The web API returns JSON and may include a top-level `errors` object for field-level validation messages.
- Frontend helpers in `static/common.js` include `api()`, `showToast()`, `showFieldError()` and `clearFieldError()`.

Contributing
------------
- Add focused unit tests for new behavior.
- Follow existing frontend patterns when adding pages (`templates/` + `static/` files).

License
-------
Provided as-is for educational/demo purposes.
# Expanded Library Management System (Python)

This repository contains a **modular, object-oriented Library Management System** implemented in Python, aligned with the provided collaboration plan (Book, Member, Library, Issue/Return, Search, Auth, Main Interface, Unit Tests).

## 📁 Project Structure

```
library-management-system/
  book.py
  member.py
  library.py
  issue_return.py
  search.py
  auth_system.py
  storage.py                # (expanded) JSON persistence for full state
  library_management_system.py
  test_library.py
  library_db.json           # auto-generated after first run
  .github/PULL_REQUEST_TEMPLATE.md
```

## ✅ Features (Expanded)

- Add / remove / list books
- Add / list members
- Issue & return books (creates **Loan IDs**)
- Search by title / author / ISBN / category
- Basic authentication with roles: **librarian** and **member**
- JSON persistence (`library_db.json`) so data survives between runs
- Unit tests (unittest)

## ▶️ How to Run

### Run the app
```bash
python library_management_system.py
```

### Run tests
```bash
python -m unittest test_library.py
```
