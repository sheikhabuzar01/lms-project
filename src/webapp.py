from flask import Flask, request, jsonify, render_template, session
import storage
from book import Book
from member import Member
from library import Library
from issue_return import issue_book, return_book
from auth_system import AuthSystem

DB_PATH = "library_db.json"

app = Flask(__name__, static_folder="static", template_folder="templates")
# WARNING: change this in production — use env var or config
app.secret_key = "dev-secret-change-me"

# Load application state
library, auth = storage.load_state(DB_PATH)
if not getattr(auth, "users", {}):
    auth.register_user("admin", "admin")


def book_to_dict(book: Book) -> dict:
    return book.to_dict()


def member_to_dict(m: Member) -> dict:
    return m.to_dict()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/books')
def books_page():
    return render_template('books.html')


@app.route('/members')
def members_page():
    return render_template('members.html')


@app.route('/issue')
def issue_page():
    return render_template('issue.html')


@app.route('/search')
def search_page():
    return render_template('search.html')


@app.route('/auth')
def auth_page():
    return render_template('auth.html')


@app.route('/loans')
def loans_page():
    return render_template('loans.html')


def _is_logged_in() -> bool:
    return bool(session.get("user"))


@app.route("/api/me")
def api_me():
    return jsonify({"user": session.get("user")})


@app.route("/api/books", methods=["GET", "POST"])
def api_books():
    if request.method == "GET":
        return jsonify([book_to_dict(b) for b in library.list_books()])
    # protect admin action
    if not _is_logged_in():
        return jsonify({"ok": False, "msg": "Authentication required"}), 401
    data = request.get_json() or {}
    # server-side validation
    errors = {}
    isbn = (data.get('isbn') or '').strip()
    title = (data.get('title') or '').strip()
    author = (data.get('author') or '').strip()
    copies_raw = data.get('copies', 0)
    if not isbn:
        errors['isbn'] = 'ISBN is required.'
    if not title:
        errors['title'] = 'Title is required.'
    if copies_raw is None:
        copies_raw = 0
    try:
        copies = int(copies_raw)
        if copies < 0:
            errors['copies'] = 'Copies must be >= 0.'
    except Exception:
        errors['copies'] = 'Copies must be a number.'

    if errors:
        return jsonify({'ok': False, 'errors': errors}), 400

    book = Book(isbn, title, author, copies)
    library.add_book(book)
    storage.save_state(DB_PATH, library, auth)
    return jsonify({"ok": True, "msg": "Book added"})


@app.route('/api/books/<isbn>', methods=['DELETE', 'PUT'])
def api_book_modify(isbn: str):
    if not _is_logged_in():
        return jsonify({"ok": False, "msg": "Authentication required"}), 401

    if request.method == 'DELETE':
        removed = library.remove_book(isbn)
        if removed:
            storage.save_state(DB_PATH, library, auth)
            return jsonify({"ok": True, "msg": "Book removed"})
        return jsonify({"ok": False, "msg": "Book not found"}), 404

    # PUT -> update
    data = request.get_json() or {}
    book = library.get_book(isbn)
    if book is None:
        return jsonify({"ok": False, "msg": "Book not found"}), 404
    # update allowed fields
    title = data.get('title')
    author = data.get('author')
    copies = data.get('copies')
    if title is not None:
        book.title = title
    if author is not None:
        book.author = author
    if copies is not None:
        try:
            c = int(copies)
            if c < 0:
                return jsonify({"ok": False, 'errors': {'copies': 'Copies must be >= 0'}}), 400
            book.copies = c
        except Exception:
            return jsonify({"ok": False, 'errors': {'copies': 'Invalid number'}}), 400
    storage.save_state(DB_PATH, library, auth)
    return jsonify({"ok": True, "msg": "Book updated"})


@app.route("/api/members", methods=["GET", "POST"])
def api_members():
    if request.method == "GET":
        return jsonify([member_to_dict(m) for m in library.list_members()])
    # allow member registration without login, but could be protected
    data = request.get_json() or {}
    errors = {}
    member_id = (data.get('member_id') or '').strip()
    name = (data.get('name') or '').strip()
    if not member_id:
        errors['member_id'] = 'Member ID is required.'
    if not name:
        errors['name'] = 'Name is required.'
    if errors:
        return jsonify({'ok': False, 'errors': errors}), 400
    m = Member(member_id, name)
    library.add_member(m)
    storage.save_state(DB_PATH, library, auth)
    return jsonify({"ok": True, "msg": "Member added"})


@app.route('/api/members/<member_id>', methods=['DELETE', 'PUT'])
def api_member_modify(member_id: str):
    if not _is_logged_in():
        return jsonify({"ok": False, "msg": "Authentication required"}), 401

    member = library.get_member(member_id)
    if member is None:
        return jsonify({"ok": False, "msg": "Member not found"}), 404

    if request.method == 'DELETE':
        # prevent deletion if member has borrowed books
        if member.borrowed_books:
            return jsonify({"ok": False, "msg": "Member has borrowed books"}), 400
        try:
            del library.members[member_id]
            storage.save_state(DB_PATH, library, auth)
            return jsonify({"ok": True, "msg": "Member removed"})
        except KeyError:
            return jsonify({"ok": False, "msg": "Member not found"}), 404

    # PUT -> update name
    data = request.get_json() or {}
    name = data.get('name')
    if name is not None:
        name = (name or '').strip()
        if not name:
            return jsonify({'ok': False, 'errors': {'name': 'Name is required.'}}), 400
        member.name = name
        storage.save_state(DB_PATH, library, auth)
        return jsonify({"ok": True, "msg": "Member updated"})
    return jsonify({"ok": False, "msg": "Nothing to update"}), 400


@app.route("/api/issue", methods=["POST"])
def api_issue():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    isbn = data.get("isbn")
    if not member_id or not isbn:
        return jsonify({"ok": False, "msg": "member_id and isbn required"}), 400
    member = library.get_member(member_id)
    if member is None:
        return jsonify({"ok": False, "msg": "Member not found"}), 404
    ok, msg = issue_book(library, isbn, member)
    storage.save_state(DB_PATH, library, auth)
    return jsonify({"ok": ok, "msg": msg})


@app.route('/api/loans', methods=['GET'])
def api_loans():
    # return list of loans
    loans = []
    for lid, loan in library.loans.items():
        loans.append({
            'loan_id': loan.loan_id,
            'member_id': loan.member_id,
            'isbn': loan.isbn,
            'issue_date': loan.issue_date.isoformat(),
            'due_date': loan.due_date.isoformat(),
            'returned': bool(loan.returned),
        })
    return jsonify(loans)


@app.route('/api/loans/<loan_id>', methods=['PUT'])
def api_loan_update(loan_id: str):
    if not _is_logged_in():
        return jsonify({"ok": False, "msg": "Authentication required"}), 401
    loan = library.loans.get(loan_id)
    if not loan:
        return jsonify({"ok": False, "msg": "Loan not found"}), 404
    data = request.get_json() or {}
    due_date = data.get('due_date')
    returned = data.get('returned')
    if due_date is not None:
        try:
            from datetime import datetime
            loan.due_date = datetime.fromisoformat(due_date).date()
        except Exception:
            return jsonify({"ok": False, "errors": {'due_date': 'Invalid date format, expected YYYY-MM-DD'}}), 400
    if returned is not None:
        loan.returned = bool(returned)
    storage.save_state(DB_PATH, library, auth)
    return jsonify({"ok": True, "msg": "Loan updated"})


@app.route("/api/return", methods=["POST"])
def api_return():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    isbn = data.get("isbn")
    if not member_id or not isbn:
        return jsonify({"ok": False, "msg": "member_id and isbn required"}), 400
    member = library.get_member(member_id)
    if member is None:
        return jsonify({"ok": False, "msg": "Member not found"}), 404
    ok, msg = return_book(library, isbn, member)
    storage.save_state(DB_PATH, library, auth)
    return jsonify({"ok": ok, "msg": msg})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    u = data.get("username")
    p = data.get("password")
    if not u or not p:
        return jsonify({"ok": False, "msg": "username/password required"}), 400
    ok = auth.authenticate(u, p)
    if ok:
        session["user"] = u
    return jsonify({"ok": ok})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"ok": True})


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    u = data.get("username")
    p = data.get("password")
    if not u or not p:
        return jsonify({"ok": False, "msg": "username/password required"}), 400
    ok = auth.register_user(u, p)
    if ok:
        session["user"] = u
    return jsonify({"ok": ok})


@app.route("/api/save", methods=["POST"])
def api_save():
    try:
        storage.save_state(DB_PATH, library, auth)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)