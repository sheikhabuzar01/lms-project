"""
Book module (Group A)

Defines the Book class used to represent books in the library.
"""

from __future__ import annotations


class Book:
    """
    Represents a single book in the library.

    Attributes:
        isbn (str): Unique identifier for the book.
        title (str): The title of the book.
        author (str): The author of the book.
        copies (int): Number of copies available in the library.
    """

    def __init__(self, isbn: str, title: str, author: str, copies: int) -> None:
        if copies < 0:
            raise ValueError("Number of copies cannot be negative.")

        self.isbn = isbn
        self.title = title
        self.author = author
        self.copies = copies

    @property
    def available(self) -> bool:
        """
        Returns True if at least one copy of the book is available.
        """
        return self.copies > 0

    def __str__(self) -> str:
        """
        Human-readable string representation of the book.
        """
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, copies: {self.copies})"

    def to_dict(self) -> dict:
        """Serialize the Book to a dictionary."""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "copies": self.copies,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Deserialize a Book from a dictionary."""
        return cls(
            isbn=data["isbn"],
            title=data.get("title", ""),
            author=data.get("author", ""),
            copies=int(data.get("copies", 0)),
        )