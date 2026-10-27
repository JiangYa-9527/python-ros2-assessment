"""Executable examples and boundary cases for the three plain-Python exercises."""

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAM1 = ROOT / "exam1"


def run_program(filename, input_text):
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-B", str(EXAM1 / filename)],
        input=input_text,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=5,
        env=environment,
        cwd=ROOT,
    )


class ScoresTests(unittest.TestCase):
    def test_required_example(self):
        result = run_program(
            "question1_scores.py", "78 92 65 88 70 95 82 60 100 85\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "100 95 92 88 85 82 78 70 65 60\n")

    def test_multiple_lines_commas_and_duplicates(self):
        result = run_program(
            "question1_scores.py", "0,100，50\n75 75\n60\n90 10 0 99\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "100 99 90 75 75 60 50 10 0 0\n")

    def test_missing_scores_are_reported(self):
        result = run_program("question1_scores.py", "78 92\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("10", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_extra_scores_are_reported(self):
        result = run_program("question1_scores.py", "1 2 3 4 5 6 7 8 9 10 11\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("10", result.stderr)

    def test_non_integer_is_reported(self):
        result = run_program("question1_scores.py", "1 2 3 4 5 6 7 8 9 bad\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


class BookTests(unittest.TestCase):
    def test_required_example(self):
        result = run_program("question2_book.py", "C++入门\n45.5\n20\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "书名：C++入门\n价格：45.5\n库存：20\n")

    def test_title_keeps_spaces_and_zero_stock(self):
        result = run_program("question2_book.py", "Python 入门 教程\n0\n0\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "书名：Python 入门 教程\n价格：0\n库存：0\n")

    def test_constructor_initializes_displayed_values(self):
        specification = importlib.util.spec_from_file_location(
            "assessment_book", EXAM1 / "question2_book.py"
        )
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        book = module.Book("算法", 12.5, 7)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            book.display_data()
        self.assertEqual(output.getvalue(), "书名：算法\n价格：12.5\n库存：7\n")


class CharacterCountTests(unittest.TestCase):
    def assert_counts(self, text, expected):
        result = run_program("question3_char_count.py", text + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        letters, digits, others = expected
        self.assertEqual(
            result.stdout,
            f"英文字母个数：{letters}\n数字个数：{digits}\n其他字符个数：{others}\n",
        )

    def test_ascii_letters_numbers_and_punctuation(self):
        self.assert_counts("Hello ROS2! 123", (8, 4, 3))

    def test_unicode_is_other_not_ascii_letter_or_digit(self):
        self.assert_counts("Az09 中文é１２🙂!", (2, 2, 8))

    def test_empty_string(self):
        self.assert_counts("", (0, 0, 0))

    def test_spaces_and_tab_are_counted(self):
        self.assert_counts(" \t ", (0, 0, 3))


if __name__ == "__main__":
    unittest.main()
