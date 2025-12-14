"""
Issue and Return module (Group D)

Provides functions to issue and return books for members.
"""

from __future__ import annotations
from typing import Tuple

from library import Library
from member import Member
from book import Book


def issue_book(library: Library, isbn: str, member: Member) -> Tuple[bool, str]:
    """
    Issues a book from the library to a member.

    Args:
        library (Library): The library instance.
        isbn (str): ISBN of the book to issue.
        member (Member): The member borrowing the book.

    Returns:
        (success, message): Tuple[bool, str]
    """
    book = library.get_book(isbn)
    if book is None:
        return False, "Book not found."
    if book.copies <= 0:
        return False, "No copies available."

    # Enforce borrowing limit
    if len(member.borrowed_books) >= getattr(library, "max_books_per_member", 5):
        return False, f"Member has reached borrowing limit ({library.max_books_per_member})."

    # Update book copies, create loan and member record
    book.copies -= 1
    loan = library.create_loan(member.member_id, isbn)
    member.borrow_book(isbn)
    return True, f"Book '{book.title}' issued to {member.name}. Due: {loan.due_date.isoformat()} (Loan ID: {loan.loan_id})"


def return_book(library: Library, isbn: str, member: Member) -> Tuple[bool, str]:
    """
    Returns a book from a member back to the library.

    Args:
        library (Library): The library instance.
        isbn (str): ISBN of the book to return.
        member (Member): The member returning the book.

    Returns:
        (success, message): Tuple[bool, str]
    """
    book = library.get_book(isbn)
    if book is None:
        return False, "Book not found in library."

    if not member.has_borrowed(isbn):
        return False, "Member did not borrow this book."

    # Find active loan for this member and isbn
    active_loan_id = None
    for lid, loan in library.loans.items():
        if loan.member_id == member.member_id and loan.isbn == isbn and not loan.returned:
            active_loan_id = lid
            break

    if active_loan_id is None:
        # fall back to simple return
        book.copies += 1
        member.return_book(isbn)
        return True, f"Book '{book.title}' returned by {member.name}."

    # Close loan, update book and member
    library.close_loan(active_loan_id)
    book.copies += 1
    member.return_book(isbn)
    return True, f"Book '{book.title}' returned by {member.name}. (Loan {active_loan_id} closed)"