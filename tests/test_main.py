"""Интеграционные тесты поведения main() без реального интерактивного ввода."""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

import main


class TestMainFlow(unittest.TestCase):
    @patch("main.Database")
    @patch("builtins.print")
    def test_startup_file_not_found_is_handled(self, mock_print: MagicMock, mock_db_cls: MagicMock) -> None:
        mock_db = mock_db_cls.return_value
        mock_db.initialize.side_effect = FileNotFoundError("schema missing")

        main.main()

        mock_db.close.assert_called_once()
        printed = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
        self.assertIn("Startup error: required file is missing", printed)

    @patch("main.Database")
    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("builtins.print")
    @patch("main.clear_screen")
    def test_keyboard_interrupt_is_handled(
        self,
        mock_clear: MagicMock,
        mock_print: MagicMock,
        _mock_input: MagicMock,
        mock_db_cls: MagicMock,
    ) -> None:
        mock_db = mock_db_cls.return_value
        mock_db.initialize.return_value = None

        main.main()

        self.assertTrue(mock_clear.called)
        mock_db.close.assert_called_once()
        printed = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
        self.assertIn("Interrupted by user. Exiting program.", printed)

    @patch("main.Database")
    @patch("builtins.print")
    def test_startup_sqlite_error_is_handled(
        self,
        mock_print: MagicMock,
        mock_db_cls: MagicMock,
    ) -> None:
        mock_db = mock_db_cls.return_value
        mock_db.initialize.side_effect = sqlite3.Error("db init failed")

        main.main()

        mock_db.close.assert_called_once()
        printed = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
        self.assertIn("Startup error: database initialization failed", printed)

    @patch("main.Database")
    @patch("main.read_yes_no", return_value=True)
    @patch("builtins.input", side_effect=["5", "0"])
    @patch("builtins.print")
    @patch("main.clear_screen")
    def test_seed_option_loads_data_when_confirmed(
        self,
        _mock_clear: MagicMock,
        mock_print: MagicMock,
        _mock_input: MagicMock,
        mock_yes_no: MagicMock,
        mock_db_cls: MagicMock,
    ) -> None:
        mock_db = mock_db_cls.return_value
        mock_db.initialize.return_value = None
        mock_db.load_seed.return_value = None

        main.main()

        mock_yes_no.assert_called_once_with("Continue? (y/n): ")
        mock_db.load_seed.assert_called_once()
        mock_db.close.assert_called_once()
        printed = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
        self.assertIn("Demo data loaded.", printed)

    @patch("main.Database")
    @patch("main.read_yes_no", return_value=False)
    @patch("builtins.input", side_effect=["5", "0"])
    @patch("builtins.print")
    @patch("main.clear_screen")
    def test_seed_option_is_skipped_when_not_confirmed(
        self,
        _mock_clear: MagicMock,
        mock_print: MagicMock,
        _mock_input: MagicMock,
        mock_yes_no: MagicMock,
        mock_db_cls: MagicMock,
    ) -> None:
        mock_db = mock_db_cls.return_value
        mock_db.initialize.return_value = None

        main.main()

        mock_yes_no.assert_called_once_with("Continue? (y/n): ")
        mock_db.load_seed.assert_not_called()
        mock_db.close.assert_called_once()
        printed = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
        self.assertIn("Cancelled.", printed)

