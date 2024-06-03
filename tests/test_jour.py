import datetime
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jour.jour import Jour


class TestJour(unittest.TestCase):
    def setUp(self):
        # Use the name of the repository root as the preffix for the temporary directory
        self.temp_dir = Path(
            tempfile.mkdtemp(prefix=Path(__file__).parent.parent.name + "_")
        )

        self.journal_file = self.temp_dir / "journal.md"
        self.journal_emergency_file = self.temp_dir / "journal_emergency.md"

        # Fix a mock over the environment variables that contains the path to the journal files:
        # `JOURNAL` and `JOURNAL_EMERGENCY`
        self.os_env_var_patch = patch(
            "os.environ",
            {
                "JOURNAL": str(self.journal_file),
                "JOURNAL_EMERGENCY": str(self.journal_emergency_file),
                "USER": "test_user",
            },
        )
        self.os_env_var_patch.start()

    def tearDown(self):
        patch.stopall()
        shutil.rmtree(self.temp_dir)

    def test_error_if_no_context_manager(self):
        """
        Test that an error is raised if the `Jour` is not used as a context manager.
        """
        with self.assertRaises(RuntimeError) as cm:
            jour = Jour()
            jour.print_journal()

        self.assertEqual(str(cm.exception), "`Jour` context not found.")

    def test_journal_creation(self):
        """
        Test that the journal file is created when the `create_journal` flag is set to `True`.
        """
        with Jour(create_journal=True):
            self.assertTrue(os.path.isfile(self.journal_file))

    def test_journal_emergency_creation(self):
        """
        Test that the emergency journal file is created when the main journal file is not found
        and the `create_journal` flag is set to `False`. Test also that the emergency journal is
        used as target journal in this case.
        """
        jour = Jour(create_journal=False)
        with jour:
            self.assertFalse(os.path.isfile(self.journal_file))
            self.assertTrue(os.path.isfile(self.journal_emergency_file))

        # Test that the emergency journal is used as target journal
        self.assertNotEqual(jour._active_journal_file, self.journal_file)
        self.assertEqual(jour._active_journal_file, self.journal_emergency_file)

    def test_write_line_and_file_dumping(self):
        """
        Test that the `write_line` method appends a new line to the journal file. The journal file
        is created, so actually two lines should be present in the journal file.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("Test message")
            self.assertEqual(len(jour._journal), 2)

        # Assert also that the content of the journal in memory is dumped to the journal file
        with open(self.journal_file, "r") as f:
            dumped_lines = f.readlines()
        for i, line in enumerate(dumped_lines):
            self.assertTrue(line.startswith(f"{i+1}"))
            if i == 0:
                self.assertIn("Create this journal", line)
            else:
                self.assertIn("Test message", line)

    def test_append_to_last_line(self):
        """
        Assert content is correctly appended to the last line of the journal.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("Test message")
            jour.append_to_last_line("Additional message")
            self.assertIn("Test message. Additional message.", jour._journal[-1])

    def test_remove_last_line(self):
        """
        Assert that remove the last line of the journal works as expected.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("Test message")
            jour.remove_last_line()
            self.assertEqual(len(jour._journal), 1)  # One line is the creation message

    def test_get_next_tag(self):
        """
        Assert that the `get_next_tag` method returns the next tag to be used in the journal.
        """
        with Jour(create_journal=True) as jour:
            next_tag = jour.get_next_tag("Tag")
            self.assertEqual(next_tag, "#Tag1")

    def test_tag_last_line(self):
        """
        Assert the tagging of the last line of the journal works as expected. Tag index should be
        increased.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("Test message")
            jour.write_line("Other message")
            jour.tag_last_line("ExampleTag")
            self.assertIn("#ExampleTag1", jour._journal[-1])

            # Add other instance of the tag
            jour.tag_last_line("ExampleTag")
            self.assertIn("#ExampleTag2", jour._journal[-1])

    def test_print_journal_and_default_signature(self):
        """
        Test that the `print_journal` method prints the last lines of the journal as
        expected. Test also signature is added in lines.
        """
        with Jour(create_journal=True) as jour:
            for i in range(1, 25):
                jour.write_line(f"Message {i+1}")

            with patch("jour.jour.logger.info") as mock_logger:
                jour.print_journal()

                # Assert that the `logger.info` method is called with the expected lines,
                # which are the last 10 lines of the journal
                self.assertEqual(mock_logger.call_count, 1)

                # Check that the last 10 lines are printed. The lines should start by `  00ii`, where
                # `ii` is the line number; and end with `Message ii.\n`
                for i in range(15, 25):
                    self.assertIn(f"  {i+1}", mock_logger.call_args[0][0])
                    self.assertIn(f"Message {i+1}.\n", mock_logger.call_args[0][0])

    def test_custom_signature(self):
        """
        Test that the signature is correctly added to the lines of the journal when a custom
        signature is provided.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("Message", signature="CustomSignature")
            self.assertIn("CustomSignature", jour._journal[-1])

    def test_using_an_existent_journal_file(self):
        """
        Test that the `Jour` can be used normally with an existent journal file.
        """
        # Manually create file and write some content
        with open(self.journal_file, "w") as f:
            f.write("# Testing Journal\n")  # Header
            f.write("This is a testing journal only for testing purposes.\n")

        with Jour() as jour:
            self.assertEqual(jour._active_journal_file, self.journal_file)

            # Add a line to the journal
            jour.write_line("Test message")
            self.assertTrue(jour._journal[-1].startswith("1. "))
            self.assertIn("Test message", jour._journal[-1])

    def test_using_empty_file_as_journal(self):
        """
        Test that the `Jour` can be used normally with an empty but existent journal
        file.
        """
        with open(self.journal_file, "w"):
            pass

        with Jour() as jour:
            self.assertEqual(jour._active_journal_file, self.journal_file)

            # Catch message when the journal is empty
            with patch("jour.jour.logger.warning") as mock_logger:
                jour.print_journal()
                self.assertEqual(mock_logger.call_args[0][0], "The journal is empty.")

            # Try to write a line to the journal
            jour.write_line("Test message")
            self.assertTrue(jour._journal[-1].startswith("1. "))
            self.assertIn("Test message", jour._journal[-1])

    def test_messages_formatting(self):
        """
        Test that the messages are correctly formatted when written to the journal.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("This is a test message", signature="Testing Custom Author")

            # The line should be in format:
            # `0001. DD-MM-YYYY HH:MM:SS,sss - Testing Custom Author - This is a test message.`
            self.assertEqual("2", jour._journal[-1].split(".")[0])
            self.assertEqual(
                datetime.datetime.now().strftime("%Y-%m-%d %H"),
                jour._journal[-1]
                .split(". ")[1]
                .split(" - ")[0]
                .split(":")[0],  # Ignore minutes, seconds and milliseconds
            )
            self.assertEqual("Testing Custom Author", jour._journal[-1].split(" - ")[1])
            self.assertEqual(
                "This is a test message.\n", jour._journal[-1].split(" - ")[2]
            )

    def test_index_formatting_is_correct(self):
        """
        Test that the numerical index of the journal lines is correctly formatted. When dumping the
        journal to a file, the index should be padded with zeros to have a fixed length of the length
        of the highest index.
        """
        with Jour(create_journal=True) as jour:
            for _ in range(1, 20):
                jour.write_line("Test message")

            for i, line in enumerate(jour._journal):
                if i < 9:
                    self.assertEqual(f"{i+1}", line.split(".")[0])
                else:
                    self.assertEqual(f"{i+1}", line.split(".")[0])

        # Check when indexes of one and two digits are used, because the padding should be adapted to
        # the length of the highest index when dumping the journal to a file
        with open(self.journal_file, "r") as f:
            dumped_lines = f.readlines()
        for i, line in enumerate(dumped_lines):
            if i < 9:
                self.assertEqual(f"0{i+1}", line.split(".")[0])
            else:
                self.assertEqual(f"{i+1}", line.split(".")[0])

    def test_use_as_command_formatting(self):
        """
        Test that the `as_command` flag formats the message as a command.
        """
        with Jour(create_journal=True) as jour:
            jour.write_line("brew install example", as_command=True)
            self.assertIn(" - `brew install example`.\n", jour._journal[-1])

    def test_warn_about_using_emergency_journal(self):
        """
        Test that a warning is logged when the emergency journal is used.
        """
        with patch("jour.jour.logger.warning") as mock_logger:
            with Jour(create_journal=False) as jour:
                jour.write_line("Test message")
                self.assertEqual(
                    f"Using emergency journal file in `{self.journal_emergency_file}`. Manually merge this journal with the default journal file when possible.",
                    mock_logger.call_args[0][0],
                )
