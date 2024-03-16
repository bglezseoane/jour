import datetime
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from journal_writer.journal_writer import JournalWriter


class TestJournalWriter(unittest.TestCase):
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
        Test that an error is raised if the `JournalWriter` is not used as a context manager.
        """
        with self.assertRaises(RuntimeError) as cm:
            jw = JournalWriter()
            jw.print_journal()

        self.assertEqual(str(cm.exception), "`Journal Writer` context not found.")

    def test_journal_creation(self):
        """
        Test that the journal file is created when the `create_journal` flag is set to `True`.
        """
        with JournalWriter(create_journal=True):
            self.assertTrue(os.path.isfile(self.journal_file))

    def test_journal_emergency_creation(self):
        """
        Test that the emergency journal file is created when the main journal file is not found
        and the `create_journal` flag is set to `False`. Test also that the emergency journal is
        used as target journal in this case.
        """
        jw = JournalWriter(create_journal=False)
        with jw:
            self.assertFalse(os.path.isfile(self.journal_file))
            self.assertTrue(os.path.isfile(self.journal_emergency_file))

        # Test that the emergency journal is used as target journal
        self.assertNotEqual(jw._active_journal_file, self.journal_file)
        self.assertEqual(jw._active_journal_file, self.journal_emergency_file)

    def test_write_line_and_file_dumping(self):
        """
        Test that the `write_line` method appends a new line to the journal file. The journal file
        is created, so actually two lines should be present in the journal file. Implicitly, this
        test also checks that the Markdown format custom fixes are applied to the journal file.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("Test message")
            self.assertEqual(len(jw._journal), 2)

        # Assert also that the content of the journal in memory is dumped to the journal file
        with open(self.journal_file, "r") as f:
            dumped_lines = f.readlines()
        for i, line in enumerate(dumped_lines):
            self.assertTrue(line.startswith(f"000{i+1}"))
            if i == 0:
                self.assertIn("Create this journal", line)
            else:
                self.assertIn("Test message", line)

    def test_append_to_last_line(self):
        """
        Assert content is correctly appended to the last line of the journal.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("Test message")
            jw.append_to_last_line("Additional message")
            self.assertIn("Test message. Additional message.", jw._journal[-1])

    def test_remove_last_line(self):
        """
        Assert that remove the last line of the journal works as expected.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("Test message")
            jw.remove_last_line()
            self.assertEqual(len(jw._journal), 1)  # One line is the creation message

    def test_get_next_tag(self):
        """
        Assert that the `get_next_tag` method returns the next tag to be used in the journal.
        """
        with JournalWriter(create_journal=True) as jw:
            next_tag = jw.get_next_tag("Tag")
            self.assertEqual(next_tag, "#Tag1")

    def test_tag_last_line(self):
        """
        Assert the tagging of the last line of the journal works as expected. Tag index should be
        increased.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("Test message")
            jw.write_line("Other message")
            jw.tag_last_line("ExampleTag")
            self.assertIn("#ExampleTag1", jw._journal[-1])

            # Add other instance of the tag
            jw.tag_last_line("ExampleTag")
            self.assertIn("#ExampleTag2", jw._journal[-1])

    def test_print_journal_and_default_signature(self):
        """
        Test that the `print_journal` method prints the last lines of the journal as
        expected. Test also signature is added in lines.
        """
        with JournalWriter(create_journal=True) as jw:
            for i in range(1, 25):
                jw.write_line(f"Message {i+1}")

            with patch("journal_writer.journal_writer.logger.info") as mock_logger:
                jw.print_journal()

                # Assert that the `logger.info` method is called with the expected lines,
                # which are the last 10 lines of the journal
                self.assertEqual(mock_logger.call_count, 1)

                # Check that the last 10 lines are printed. The lines should start by `  00ii`, where
                # `ii` is the line number; and end with `Message ii.\n`
                for i in range(15, 25):
                    self.assertIn(f"  00{i+1}", mock_logger.call_args[0][0])
                    self.assertIn(f"Message {i+1}.\n", mock_logger.call_args[0][0])

    def test_custom_signature(self):
        """
        Test that the signature is correctly added to the lines of the journal when a custom
        signature is provided.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("Message", signature="CustomSignature")
            self.assertIn("CustomSignature", jw._journal[-1])

    def test_using_an_existent_journal_file(self):
        """
        Test that the `JournalWriter` can be used normally with an existent journal file.
        """
        # Manually create file and write some content
        with open(self.journal_file, "w") as f:
            f.write("# Testing Journal\n")  # Header
            f.write("This is a testing journal only for testing purposes.\n")

        with JournalWriter() as jw:
            self.assertEqual(jw._active_journal_file, self.journal_file)

            # Add a line to the journal
            jw.write_line("Test message")
            self.assertTrue(jw._journal[-1].startswith("0001. "))
            self.assertIn("Test message", jw._journal[-1])

    def test_using_empty_file_as_journal(self):
        """
        Test that the `JournalWriter` can be used normally with an empty but existent journal
        file.
        """
        with open(self.journal_file, "w"):
            pass

        with JournalWriter() as jw:
            self.assertEqual(jw._active_journal_file, self.journal_file)

            # Catch message when the journal is empty
            with patch("journal_writer.journal_writer.logger.warning") as mock_logger:
                jw.print_journal()
                self.assertEqual(mock_logger.call_args[0][0], "The journal is empty.")

            # Try to write a line to the journal
            jw.write_line("Test message")
            self.assertTrue(jw._journal[-1].startswith("0001. "))
            self.assertIn("Test message", jw._journal[-1])

    def test_messages_formatting(self):
        """
        Test that the messages are correctly formatted when written to the journal.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("This is a test message", signature="Testing Custom Author")

            # The line should be in format:
            # `0001. DD-MM-YYYY HH:MM:SS,sss - Testing Custom Author - This is a test message.`
            self.assertEqual("0002", jw._journal[-1].split(".")[0])
            self.assertEqual(
                datetime.datetime.now().strftime("%Y-%m-%d %H"),
                jw._journal[-1]
                .split(". ")[1]
                .split(" - ")[0]
                .split(":")[0],  # Ignore minutes, seconds and milliseconds
            )
            self.assertEqual("Testing Custom Author", jw._journal[-1].split(" - ")[1])
            self.assertEqual(
                "This is a test message.\n", jw._journal[-1].split(" - ")[2]
            )

    def test_use_as_command_formatting(self):
        """
        Test that the `as_command` flag formats the message as a command.
        """
        with JournalWriter(create_journal=True) as jw:
            jw.write_line("brew install example", as_command=True)
            self.assertIn(" - `brew install example`.\n", jw._journal[-1])

    def test_warn_about_using_emergency_journal(self):
        """
        Test that a warning is logged when the emergency journal is used.
        """
        with patch("journal_writer.journal_writer.logger.warning") as mock_logger:
            with JournalWriter(create_journal=False) as jw:
                jw.write_line("Test message")
                self.assertEqual(
                    f"Using emergency journal file in `{self.journal_emergency_file}`. Manually merge this journal with the default journal file when possible.",
                    mock_logger.call_args[0][0],
                )
