import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from book import Book
from member import Member
from library import Library
from issue_return import issue_book, return_book
from search import search_by_title, search_by_author, search_by_isbn
from auth_system import AuthSystem
import storage
from pathlib import Path


DB_PATH = "library_db.json"


class LibraryGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management - GUI")
        self.geometry("900x600")

        # Load state
        self.library, self.auth = storage.load_state(DB_PATH)

        # If no users, create default
        if not getattr(self.auth, "users", {}):
            self.auth.register_user("admin", "admin")

        self.logged_in = False

        # Notebook (tabs)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.create_books_tab()
        self.create_members_tab()
        self.create_issue_tab()
        self.create_search_tab()
        self.create_admin_tab()

        # Bottom buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btn_frame, text="Save", command=self.save_state).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Backup", command=self.create_backup).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_all).pack(side=tk.RIGHT, padx=5, pady=5)

        self.refresh_all()

    def create_books_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Books")

        left = ttk.Frame(frame)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.books_list = tk.Listbox(left)
        self.books_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        right = ttk.Frame(frame)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(right, text="Add Book", command=self.add_book_popup).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(right, text="Remove Book", command=self.remove_selected_book).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(right, text="View Details", command=self.view_book_details).pack(fill=tk.X, padx=5, pady=5)

    def create_members_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Members")

        left = ttk.Frame(frame)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.members_list = tk.Listbox(left)
        self.members_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        right = ttk.Frame(frame)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(right, text="Add Member", command=self.add_member_popup).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(right, text="View Member", command=self.view_member_details).pack(fill=tk.X, padx=5, pady=5)

    def create_issue_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Issue / Return")

        f = ttk.Frame(frame)
        f.pack(padx=10, pady=10, anchor=tk.N)

        ttk.Label(f, text="Member ID:").grid(row=0, column=0, sticky=tk.W)
        self.issue_member = ttk.Entry(f)
        self.issue_member.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(f, text="ISBN:").grid(row=1, column=0, sticky=tk.W)
        self.issue_isbn = ttk.Entry(f)
        self.issue_isbn.grid(row=1, column=1, sticky=tk.W)

        ttk.Button(f, text="Issue Book", command=self.issue_book_action).grid(row=2, column=0, pady=5)
        ttk.Button(f, text="Return Book", command=self.return_book_action).grid(row=2, column=1, pady=5)

        self.issue_msg = ttk.Label(f, text="")
        self.issue_msg.grid(row=3, column=0, columnspan=2)

    def create_search_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Search")

        f = ttk.Frame(frame)
        f.pack(fill=tk.X, padx=10, pady=10)

        self.search_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.search_var, width=60).pack(side=tk.LEFT, padx=5)
        self.search_type = tk.StringVar(value="title")
        ttk.Combobox(f, textvariable=self.search_type, values=["title", "author", "isbn"], width=10).pack(side=tk.LEFT)
        ttk.Button(f, text="Search", command=self.search_action).pack(side=tk.LEFT, padx=5)

        self.search_results = tk.Listbox(frame)
        self.search_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_admin_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Librarian")

        f = ttk.Frame(frame)
        f.pack(padx=10, pady=10)

        ttk.Label(f, text="Username:").grid(row=0, column=0)
        self.user_entry = ttk.Entry(f)
        self.user_entry.grid(row=0, column=1)
        ttk.Label(f, text="Password:").grid(row=1, column=0)
        self.pass_entry = ttk.Entry(f, show="*")
        self.pass_entry.grid(row=1, column=1)

        ttk.Button(f, text="Login", command=self.login_action).grid(row=2, column=0, pady=5)
        ttk.Button(f, text="Register Librarian", command=self.register_librarian).grid(row=2, column=1, pady=5)

        self.login_status = ttk.Label(f, text="Not logged in")
        self.login_status.grid(row=3, column=0, columnspan=2)

    # --- Actions ---
    def refresh_all(self):
        self.refresh_books()
        self.refresh_members()

    def refresh_books(self):
        self.books_list.delete(0, tk.END)
        for book in self.library.list_books():
            self.books_list.insert(tk.END, f"{book.title} | {book.author} | ISBN:{book.isbn} | copies:{book.copies}")

    def refresh_members(self):
        self.members_list.delete(0, tk.END)
        for m in self.library.list_members():
            self.members_list.insert(tk.END, f"{m.member_id} | {m.name} | borrowed:{len(m.borrowed_books)}")

    def add_book_popup(self):
        if not self.logged_in:
            messagebox.showwarning("Permission", "Login as librarian to add books.")
            return
        isbn = simpledialog.askstring("ISBN", "Enter ISBN:")
        if not isbn:
            return
        title = simpledialog.askstring("Title", "Enter title:") or ""
        author = simpledialog.askstring("Author", "Enter author:") or ""
        try:
            copies = int(simpledialog.askstring("Copies", "Number of copies:") or "0")
        except Exception:
            messagebox.showerror("Error", "Invalid number of copies.")
            return
        try:
            book = Book(isbn, title, author, copies)
            self.library.add_book(book)
            messagebox.showinfo("Added", f"Book '{title}' added.")
            self.refresh_books()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_selected_book(self):
        if not self.logged_in:
            messagebox.showwarning("Permission", "Login as librarian to remove books.")
            return
        sel = self.books_list.curselection()
        if not sel:
            return
        text = self.books_list.get(sel[0])
        # ISBN is like '... ISBN:xxx ...'
        import re
        m = re.search(r"ISBN:([^\s|]+)", text)
        if not m:
            return
        isbn = m.group(1)
        if messagebox.askyesno("Confirm", f"Remove book {isbn}?"):
            if self.library.remove_book(isbn):
                messagebox.showinfo("Removed", f"Book {isbn} removed.")
                self.refresh_books()
            else:
                messagebox.showerror("Error", "Book not found.")

    def view_book_details(self):
        sel = self.books_list.curselection()
        if not sel:
            return
        text = self.books_list.get(sel[0])
        messagebox.showinfo("Book", text)

    def add_member_popup(self):
        member_id = simpledialog.askstring("Member ID", "Enter member ID:")
        if not member_id:
            return
        name = simpledialog.askstring("Name", "Enter member name:") or ""
        m = Member(member_id, name)
        self.library.add_member(m)
        messagebox.showinfo("Added", f"Member '{name}' added.")
        self.refresh_members()

    def view_member_details(self):
        sel = self.members_list.curselection()
        if not sel:
            return
        text = self.members_list.get(sel[0])
        messagebox.showinfo("Member", text)

    def issue_book_action(self):
        member_id = self.issue_member.get().strip()
        isbn = self.issue_isbn.get().strip()
        if not member_id or not isbn:
            self.issue_msg.config(text="Member ID and ISBN required")
            return
        member = self.library.get_member(member_id)
        if member is None:
            self.issue_msg.config(text="Member not found")
            return
        ok, msg = issue_book(self.library, isbn, member)
        self.issue_msg.config(text=msg)
        self.refresh_all()

    def return_book_action(self):
        member_id = self.issue_member.get().strip()
        isbn = self.issue_isbn.get().strip()
        if not member_id or not isbn:
            self.issue_msg.config(text="Member ID and ISBN required")
            return
        member = self.library.get_member(member_id)
        if member is None:
            self.issue_msg.config(text="Member not found")
            return
        ok, msg = return_book(self.library, isbn, member)
        self.issue_msg.config(text=msg)
        self.refresh_all()

    def search_action(self):
        q = self.search_var.get().strip()
        if not q:
            return
        t = self.search_type.get()
        if t == "title":
            res = search_by_title(self.library, q)
        elif t == "author":
            res = search_by_author(self.library, q)
        else:
            res = search_by_isbn(self.library, q)
        self.search_results.delete(0, tk.END)
        for b in res:
            self.search_results.insert(tk.END, f"{b.title} | {b.author} | ISBN:{b.isbn} | copies:{b.copies}")

    def login_action(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            self.login_status.config(text="Provide credentials")
            return
        if self.auth.authenticate(u, p):
            self.logged_in = True
            self.login_status.config(text=f"Logged in as {u}")
            messagebox.showinfo("Login", "Login successful")
        else:
            self.login_status.config(text="Invalid credentials")
            messagebox.showerror("Login", "Invalid credentials")

    def register_librarian(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            self.login_status.config(text="Provide credentials")
            return
        if self.auth.register_user(u, p):
            messagebox.showinfo("Registered", "Librarian registered")
        else:
            messagebox.showerror("Error", "Username already exists")

    def save_state(self):
        try:
            storage.save_state(DB_PATH, self.library, self.auth)
            messagebox.showinfo("Saved", "State saved to disk.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def create_backup(self):
        p = Path("backups")
        p.mkdir(parents=True, exist_ok=True)
        import shutil, datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = p / f"library_db_{timestamp}.json"
        try:
            storage.save_state(DB_PATH, self.library, self.auth)
            shutil.copy2(DB_PATH, dest)
            messagebox.showinfo("Backup", f"Backup created: {dest}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {e}")


if __name__ == "__main__":
    app = LibraryGUI()
    app.mainloop()