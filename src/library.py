"""
Library module (Group C)

Defines the Library class which manages the book collection
and registered members.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from book import Book
from member import Member


class Library:
    """
    Represents the library, managing books and members.

    Attributes:
        books (Dict[str, Book]): Maps ISBNs to Book objects.
        members (Dict[str, Member]): Maps member IDs to Member objects.
    """

    def __init__(self) -> None:
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        # loans: mapping loan_id -> Loan
        self.loans: Dict[str, Any] = {}
        # next loan id counter
        self._next_loan_id: int = 1
        # borrowing policy
        self.max_books_per_member: int = 5

    # --- Book management ---

    def add_book(self, book: Book) -> None:
        """
        Adds a book to the library. If the book already exists,
        its copy count is increased.

        Args:
            book (Book): The book to add.
        """
        if book.isbn in self.books:
            self.books[book.isbn].copies += book.copies
        else:
            self.books[book.isbn] = book

    def remove_book(self, isbn: str) -> bool:
        """
        Removes a book from the library by ISBN.

        Args:
            isbn (str): The ISBN of the book to remove.

        Returns:
            bool: True if the book was removed, False if not found.
        """
        if isbn in self.books:
            del self.books[isbn]
            return True
        return False

    def list_books(self) -> List[Book]:
        """
        Returns a list of all books in the library.
        """
        return list(self.books.values())

    def get_book(self, isbn: str) -> Optional[Book]:
        """
        Retrieves a book by its ISBN.

        Args:
            isbn (str): The ISBN of the desired book.

        Returns:
            Optional[Book]: The book if found, otherwise None.
        """
        return self.books.get(isbn)

    # --- Member management ---

    def add_member(self, member: Member) -> None:
        """
        Registers a new member in the library.

        Args:
            member (Member): The member to add.
        """
        self.members[member.member_id] = member

    def get_member(self, member_id: str) -> Optional[Member]:
        """
        Retrieves a member by ID.

        Args:
            member_id (str): The member's ID.

        Returns:
            Optional[Member]: The member if found, otherwise None.
        """
        return self.members.get(member_id)

    def list_members(self) -> List[Member]:
        """
        Returns a list of all registered members.
        """
        return list(self.members.values())

    def to_dict(self) -> dict:
        """Serialize the whole library to a dictionary."""
        return {
            "books": {isbn: book.to_dict() for isbn, book in self.books.items()},
            "members": {mid: member.to_dict() for mid, member in self.members.items()},
            "loans": {lid: loan.to_dict() for lid, loan in self.loans.items()},
            "next_loan_id": self._next_loan_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Library":
        """Reconstruct a Library from a dictionary produced by `to_dict`."""
        lib = cls()
        books = data.get("books", {}) or {}
        for isbn, bdata in books.items():
            # Book.from_dict will validate copies
            book = Book.from_dict(bdata)
            lib.books[isbn] = book

        members = data.get("members", {}) or {}
        for mid, mdata in members.items():
            member = Member.from_dict(mdata)
            lib.members[mid] = member

        # load loans if any
        loans = data.get("loans", {}) or {}
        for lid, ldata in loans.items():
            loan = Library.Loan.from_dict(ldata)
            lib.loans[lid] = loan

        lib._next_loan_id = int(data.get("next_loan_id", lib._next_loan_id))

        return lib

    @dataclass
    class Loan:
        loan_id: str
        member_id: str
        isbn: str
        issue_date: date
        due_date: date
        returned: bool = False

        def to_dict(self) -> Dict[str, Any]:
            return {
                "loan_id": self.loan_id,
                "member_id": self.member_id,
                "isbn": self.isbn,
                "issue_date": self.issue_date.isoformat(),
                "due_date": self.due_date.isoformat(),
                "returned": bool(self.returned),
            }

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "Library.Loan":
            return cls(
                loan_id=str(data["loan_id"]),
                member_id=str(data["member_id"]),
                isbn=str(data["isbn"]),
                issue_date=datetime.fromisoformat(data["issue_date"]).date(),
                due_date=datetime.fromisoformat(data["due_date"]).date(),
                returned=bool(data.get("returned", False)),
            )

    def _generate_loan_id(self) -> str:
        lid = str(self._next_loan_id)
        self._next_loan_id += 1
        return lid

    def create_loan(self, member_id: str, isbn: str, days: int = 14) -> "Loan":
        """Create and record a loan; does not check availability.

        Returns the Loan object.
        """
        lid = self._generate_loan_id()
        today = date.today()
        loan = Library.Loan(loan_id=lid, member_id=member_id, isbn=isbn, issue_date=today, due_date=today + timedelta(days=days))
        self.loans[lid] = loan
        return loan

    def close_loan(self, loan_id: str) -> bool:
        loan = self.loans.get(loan_id)
        if loan is None:
            return False
        loan.returned = True
        return True
