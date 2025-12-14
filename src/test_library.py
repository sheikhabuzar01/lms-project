"""
Unit Testing module (Group H)

Provides basic tests for the core functionality of the system.
"""

import unittest

from book import Book
from member import Member
from library import Library
from issue_return import issue_book, return_book
from search import search_by_title
import storage
from auth_system import AuthSystem
import tempfile
import os


class TestLibrarySystem(unittest.TestCase):
    """
    Unit tests for the Library Management System.
    """

    def test_add_book(self):
        library = Library()
        book = Book("123", "Test Book", "Author", 2)
        library.add_book(book)
        self.assertIn("123", library.books)
        self.assertEqual(library.books["123"].copies, 2)

    def test_issue_and_return_book(self):
        library = Library()
        book = Book("123", "Test Book", "Author", 1)
        library.add_book(book)

        member = Member("m1", "Test Member")
        library.add_member(member)

        # Issue book
        success, msg = issue_book(library, "123", member)
        self.assertTrue(success)
        self.assertEqual(library.books["123"].copies, 0)
        self.assertIn("123", member.borrowed_books)

        # Return book
        success, msg = return_book(library, "123", member)
        self.assertTrue(success)
        self.assertEqual(library.books["123"].copies, 1)
        self.assertNotIn("123", member.borrowed_books)

    def test_search_by_title(self):
        library = Library()
        library.add_book(Book("111", "Python Programming", "Author A", 3))
        library.add_book(Book("222", "Advanced Python", "Author B", 2))

        results = search_by_title(library, "python")
        self.assertEqual(len(results), 2)

    def test_loans_and_limits(self):
        library = Library()
        library.max_books_per_member = 1
        library.add_book(Book("a1", "One", "A", 1))
        library.add_book(Book("b2", "Two", "B", 1))

        member = Member("m1", "Tester")
        library.add_member(member)

        ok, msg = issue_book(library, "a1", member)
        self.assertTrue(ok)
        # loan recorded
        self.assertEqual(len(library.loans), 1)

        # second issue should fail due to limit
        ok, msg = issue_book(library, "b2", member)
        self.assertFalse(ok)

        # return first book
        ok, msg = return_book(library, "a1", member)
        self.assertTrue(ok)
        # loan should be marked returned
        loan = next(iter(library.loans.values()))
        self.assertTrue(loan.returned)

    def test_persistence_roundtrip(self):
        library = Library()
        library.add_book(Book("p1", "Persist", "X", 2))
        member = Member("mm", "Pers")
        library.add_member(member)
        ok, msg = issue_book(library, "p1", member)
        self.assertTrue(ok)

        auth = AuthSystem()
        auth.register_user("admin", "admin")

        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tf.close()
        try:
            storage.save_state(tf.name, library, auth)
            lib2, auth2 = storage.load_state(tf.name)
            self.assertIn("p1", lib2.books)
            self.assertIn("mm", lib2.members)
            self.assertTrue(len(lib2.loans) >= 1)
            self.assertIn("admin", auth2.users)
        finally:
            try:
                os.unlink(tf.name)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()