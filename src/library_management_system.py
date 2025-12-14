"""
Main Application Interface (Group G)

Combines all modules into a simple command-line interface.
"""

from __future__ import annotations

from book import Book
from member import Member
from library import Library
from issue_return import issue_book, return_book
from search import search_by_title, search_by_author, search_by_isbn
from auth_system import AuthSystem
import storage
import shutil
from pathlib import Path
from datetime import datetime


def print_menu() -> None:
    """
    Displays the main menu options.
    """
    print("\n=== Library Management System ===")
    print("1. Add Book")
    print("2. List Books")
    print("3. Register Member")
    print("4. List Members")
    print("5. Issue Book")
    print("6. Return Book")
    print("7. Search Books")
    print("8. Login (Librarian)")
    print("9. List Loans")
    print("10. Remove Book")
    print("11. Save Now")
    print("12. Backup DB")
    print("0. Exit")


def search_menu() -> None:
    """
    Displays search options.
    """
    print("\n--- Search Books ---")
    print("1. By Title")
    print("2. By Author")
    print("3. By ISBN")


def main(no_save: bool = False) -> tuple[Library, AuthSystem]:
    """
    Entry point of the application. Provides a looped menu interface.
    """
    library = Library()

    # Load persisted state (library + auth). Falls back to new instances.
    library, auth = storage.load_state("library_db.json")
    if not isinstance(auth, AuthSystem):
        # backwards compatibility (if storage returned a plain dict)
        auth = AuthSystem.from_dict(getattr(auth, "to_dict", lambda: {"users": {}})())

    # Ensure there is at least one default librarian
    if not auth.users:
        auth.register_user("admin", "admin")

    logged_in = False

    print("Welcome to the Library Management System")
    print("Default librarian account -> username: admin, password: admin")

    def confirm(prompt: str) -> bool:
        resp = input(f"{prompt} (y/N): ").strip().lower()
        return resp in ("y", "yes")

    def save_now() -> None:
        try:
            storage.save_state("library_db.json", library, auth)
            print("State saved to library_db.json")
        except Exception as e:
            print(f"Failed to save state: {e}")

    def create_backup(backup_dir: str = "backups") -> str:
        p = Path(backup_dir)
        p.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = p / f"library_db_{timestamp}.json"
        # Ensure latest state is saved before backup
        storage.save_state("library_db.json", library, auth)
        try:
            shutil.copy2("library_db.json", backup_path)
            return str(backup_path)
        except Exception:
            # If library_db.json does not exist yet, write a fresh one
            storage.save_state(str(backup_path), library, auth)
            return str(backup_path)

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Exiting the system. Goodbye!")
            break

        if choice == "1":
            if not logged_in:
                print("You must be logged in as librarian to add books.")
                continue
            isbn = input("Enter ISBN: ").strip()
            title = input("Enter title: ").strip()
            author = input("Enter author: ").strip()
            try:
                copies = int(input("Enter number of copies: ").strip())
            except ValueError:
                print("Invalid number of copies.")
                continue

            try:
                book = Book(isbn, title, author, copies)
                library.add_book(book)
                print(f"Book '{title}' added successfully.")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            books = library.list_books()
            if not books:
                print("No books in the library.")
            else:
                print("\n--- Books in Library ---")
                for book in books:
                    print(book)
                # show available copies summary
                print(f"Total books: {len(books)}")

        elif choice == "3":
            member_id = input("Enter member ID: ").strip()
            name = input("Enter member name: ").strip()
            member = Member(member_id, name)
            library.add_member(member)
            print(f"Member '{name}' registered successfully.")

        elif choice == "4":
            members = library.list_members()
            if not members:
                print("No members registered.")
            else:
                print("\n--- Registered Members ---")
                for member in members:
                    print(member)
                print(f"Total members: {len(members)}")

        elif choice == "5":
            member_id = input("Enter member ID: ").strip()
            member = library.get_member(member_id)
            if member is None:
                print("Member not found.")
                continue
            isbn = input("Enter ISBN of book to issue: ").strip()
            success, message = issue_book(library, isbn, member)
            print(message)

        elif choice == "6":
            member_id = input("Enter member ID: ").strip()
            member = library.get_member(member_id)
            if member is None:
                print("Member not found.")
                continue
            isbn = input("Enter ISBN of book to return: ").strip()
            success, message = return_book(library, isbn, member)
            print(message)

        elif choice == "9":
            # List loans
            if not library.loans:
                print("No loans recorded.")
            else:
                print("\n--- Loans ---")
                for lid, loan in library.loans.items():
                    status = "Returned" if loan.returned else "Active"
                    print(f"Loan {lid}: Member {loan.member_id} -> ISBN {loan.isbn} | Due: {loan.due_date.isoformat()} | {status}")

        elif choice == "10":
            if not logged_in:
                print("You must be logged in as librarian to remove books.")
                continue
            isbn = input("Enter ISBN of book to remove: ").strip()
            if not isbn:
                print("ISBN cannot be empty.")
                continue
            if not confirm(f"Are you sure you want to remove book with ISBN {isbn}?"):
                print("Cancelled.")
                continue
            if library.remove_book(isbn):
                print(f"Book {isbn} removed.")
            else:
                print("Book not found.")

        elif choice == "11":
            save_now()

        elif choice == "12":
            path = create_backup()
            print(f"Backup created at: {path}")

        elif choice == "7":
            search_menu()
            s_choice = input("Choose search type: ").strip()
            if s_choice == "1":
                title = input("Enter title or part of title: ").strip()
                results = search_by_title(library, title)
            elif s_choice == "2":
                author = input("Enter author name or part of name: ").strip()
                results = search_by_author(library, author)
            elif s_choice == "3":
                isbn = input("Enter ISBN: ").strip()
                results = search_by_isbn(library, isbn)
            else:
                print("Invalid search option.")
                continue

            if not results:
                print("No matching books found.")
            else:
                print("\n--- Search Results ---")
                for book in results:
                    print(book)

        elif choice == "9":
            # List loans
            if not library.loans:
                print("No loans recorded.")
            else:
                print("\n--- Loans ---")
                for lid, loan in library.loans.items():
                    status = "Returned" if loan.returned else "Active"
                    print(f"Loan {lid}: Member {loan.member_id} -> ISBN {loan.isbn} | Due: {loan.due_date.isoformat()} | {status}")

        elif choice == "8":
            print("\n--- Librarian Login ---")
            print("1. Login")
            print("2. Register new librarian")
            sub = input("Choose an option: ").strip()
            if sub == "1":
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                if auth.authenticate(username, password):
                    logged_in = True
                    print("Login successful.")
                else:
                    print("Invalid credentials.")
            elif sub == "2":
                username = input("New username: ").strip()
                password = input("New password: ").strip()
                if auth.register_user(username, password):
                    print("Librarian registered successfully.")
                else:
                    print("Username already exists.")
            else:
                print("Invalid option.")
        else:
            print("Invalid choice. Please try again.")
    # return state for the caller to persist if desired
    return library, auth

if __name__ == "__main__":
    import sys
    # simple CLI flag parsing
    no_save_flag = "--no-save" in sys.argv

    try:
        library, auth = main(no_save=no_save_flag)
    finally:
        # Save state on exit unless user disabled it
        if not no_save_flag:
            try:
                storage.save_state("library_db.json", library, auth)
            except Exception:
                pass
