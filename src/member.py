"""
Member module (Group B)

Defines the Member class used to represent members of the library.
"""

from __future__ import annotations
from typing import List


class Member:
    """
    Represents a library member.

    Attributes:
        member_id (str): Unique identifier for the member.
        name (str): Member's full name.
        borrowed_books (List[str]): List of ISBNs for borrowed books.
    """

    def __init__(self, member_id: str, name: str) -> None:
        self.member_id = member_id
        self.name = name
        self.borrowed_books: List[str] = []

    def borrow_book(self, isbn: str) -> None:
        """
        Records that the member has borrowed a book.

        Args:
            isbn (str): ISBN of the book being borrowed.
        """
        if isbn not in self.borrowed_books:
            self.borrowed_books.append(isbn)

    def return_book(self, isbn: str) -> None:
        """
        Records that the member has returned a book.

        Args:
            isbn (str): ISBN of the book being returned.
        """
        if isbn in self.borrowed_books:
            self.borrowed_books.remove(isbn)

    def has_borrowed(self, isbn: str) -> bool:
        """
        Checks if the member has borrowed a specific book.

        Args:
            isbn (str): ISBN of the book.

        Returns:
            bool: True if the book is in the member's borrowed list.
        """
        return isbn in self.borrowed_books

    def __str__(self) -> str:
        """
        Human-readable representation of the member.
        """
        return f"Member {self.member_id}: {self.name} (Borrowed: {len(self.borrowed_books)})"

    def to_dict(self) -> dict:
        """Serialize the Member to a dictionary."""
        return {
            "member_id": self.member_id,
            "name": self.name,
            "borrowed_books": list(self.borrowed_books),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        """Deserialize a Member from a dictionary."""
        m = cls(member_id=data["member_id"], name=data.get("name", ""))
        borrowed = data.get("borrowed_books") or []
        m.borrowed_books = list(borrowed)
        return m