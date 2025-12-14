"""
Search module (Group E)

Provides search functions for books in the library.
"""

from __future__ import annotations
from typing import List

from library import Library
from book import Book


def search_by_title(library: Library, title: str) -> List[Book]:
    """
    Searches for books by title (case-insensitive, partial match).

    Args:
        library (Library): The library instance.
        title (str): Title or partial title to search for.

    Returns:
        List[Book]: Matching books.
    """
    title = title.lower()
    return [
        book for book in library.list_books()
        if title in book.title.lower()
    ]


def search_by_author(library: Library, author: str) -> List[Book]:
    """
    Searches for books by author (case-insensitive, partial match).

    Args:
        library (Library): The library instance.
        author (str): Author name or partial name.

    Returns:
        List[Book]: Matching books.
    """
    author = author.lower()
    return [
        book for book in library.list_books()
        if author in book.author.lower()
    ]


def search_by_isbn(library: Library, isbn: str) -> List[Book]:
    """
    Searches for books by exact ISBN.

    Args:
        library (Library): The library instance.
        isbn (str): ISBN of the book.

    Returns:
        List[Book]: A list with the book if found, otherwise empty.
    """
    book = library.get_book(isbn)
    return [book] if book is not None else []