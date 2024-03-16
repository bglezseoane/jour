import datetime
import logging
import os
from pathlib import Path
from typing import Optional

import mdformat
from ilock import ILock

# Setup logger
handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s - jour - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Jour:
    """
    Jour central class. This class is intended to be used as a context manager
    to implement a lock to manipulate the journal file securely. It also provides a set
    of methods to write, append, tag, and print the journal.
    """

    _journal_lock: Optional[ILock] = None
    _journal: Optional[list] = None

    def __init__(self, create_journal: bool = False):
        """
        Initialize the Jour. This class should be used as a context manager
        to ensure a singleton behavior over the journal file, obtaining a lock over it.

        :param create_journal: If `True`, create a new journal file.
        """
        self.journal_file = Path().home() / "journal.md"  # Default
        self.journal_emergency_file = Path().home() / "journal_emergency.md"  # Default
        self.__set_journals_file_locations()

        # Check journal reachability
        if os.path.isfile(self.journal_file):
            self._active_journal_file = Path(self.journal_file)
        elif create_journal:
            self.__create_journal_file(self.journal_file)
            self._active_journal_file = Path(self.journal_file)
        else:
            logger.warning(
                f"Journal file in `{self.journal_file}` unreachable. Using emergency "
                f"journal instead... If you want to use the default journal file, check if "
                f"it exists and is reachable. If not exists and want to create it, use the "
                f"`create_journal` parameter."
            )
            if os.path.isfile(self.journal_emergency_file):
                self._active_journal_file = Path(
                    self.journal_emergency_file
                )  # pragma: no cover
            else:
                logger.warning(
                    f"Creating emergency journal file in `{self.journal_emergency_file}`..."
                )
                self.__create_journal_file(
                    self.journal_emergency_file,
                    first_line="Create this emergency journal",
                )
                self._active_journal_file = Path(self.journal_emergency_file)

        # Warn the user if using the emergency journal, because probably it should be merged
        # with the default journal file when possible
        if self._active_journal_file == self.journal_emergency_file:
            logger.warning(
                f"Using emergency journal file in `{self.journal_emergency_file}`. Manually merge this journal with the default journal file when possible."
            )

    def __enter__(self):
        """
        Enter the context manager to get a lock over the journal file.
        """
        logger.debug(
            f"Using journal file: `{self._active_journal_file}`..."
        )  # Debug level

        self._journal_lock = ILock(
            f"jw_lock_{self._active_journal_file.name}", reentrant=True, timeout=10
        )
        with self._journal_lock:
            # Load the journal file to memory
            with open(self._active_journal_file, "r") as f:
                self._journal = f.readlines()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager to release the lock over the journal file.
        """
        self.__check_context()

        # Before dumping the journal to the file, format Markdown with Mdformat
        journal_fmt = mdformat.text(
            "".join(self._journal), options={"number": True, "wrap": "keep"}
        )

        # However Mdformat's, preserve the line index format with four digits, that is considered
        # here as a particularity of the type of file to facilitate reading
        now = datetime.datetime.now().strftime(
            "%Y-%m"
        )  # Used for protect the following replacement, affecting only the line index and not other possible numbers in the journal
        for i, _ in enumerate(journal_fmt.split("\n")):
            journal_fmt = journal_fmt.replace(
                f"{i+1}. {now}", f"{str(i+1).zfill(4)}. {now}"
            )

        with self._journal_lock:
            # Write the journal back to the file
            with open(self._active_journal_file, "w") as f:
                f.write(journal_fmt)

        self._journal_lock = None

    def __check_context(self) -> None:
        """
        Check if the context manager is active. If not, raise an error.
        """
        if not self._journal_lock:
            logger.error("Jour context not found. Use this class as a context manager.")
            raise RuntimeError("`Jour` context not found.")

    def __set_journals_file_locations(self) -> None:
        """
        Recover the journal file and emergency journal file names from environment
        variables. If not found, do not change the default values.
        """
        journal_file = os.getenv("JOURNAL")
        if journal_file:
            self.journal_file = Path(journal_file)

        journal_emergency_file = os.getenv("JOURNAL_EMERGENCY")
        if journal_emergency_file:
            self.journal_emergency_file = Path(journal_emergency_file)

    def __create_journal_file(
        self, journal_file: Path, first_line: str = "Create this journal"
    ) -> None:
        """
        Create a new journal file with a first line.

        :param journal_file: The file name to create.
        :param first_line: The first line to write in the journal.
        """
        # Create empty journal file
        with open(journal_file, "w") as f:
            f.write(self.__format_new_line(first_line, index=1, signature="jour"))

        logger.info(f"Journal file created in `{journal_file}`.")

    def print_journal(self) -> None:
        """
        Read the journal and print its last lines.
        """
        self.__check_context()

        # Print last 10 lines or all the journal if it has less than 10 lines
        n_lines = 10 if len(self._journal) > 10 else len(self._journal)
        if n_lines > 0:
            message = f"Journal last {n_lines} lines:\n"
            for line in self._journal[-n_lines:]:
                message += f"  {line}"
            logger.info(message)
        else:
            logger.warning(f"The journal is empty.")

    def write_line(
        self,
        message: str,
        signature: Optional[str] = None,
        as_command: bool = False,
        printing: bool = True,
    ) -> None:
        """
        Write a new line to the journal.

        :param message: The message to write.
        :param signature: The signature to add as the line author. Default is the user name.
        :param as_command: If `True`, format the message as a command.
        :param printing: If `True`, print the new line.
        """
        self.__check_context()

        # Compose the new line
        new_line = self.__format_new_line(
            message=message, signature=signature, as_command=as_command
        )

        # Append the new line to the journal
        self._journal.append(new_line)

        if printing:
            logger.info(f"New line:\n  {new_line}")

    def append_to_last_line(
        self, new_message: str, as_command: bool = False, printing: bool = True
    ) -> None:
        """
        Add some new content to the last line of the journal.

        :param new_message: The new message part to add.
        :param as_command: If `True`, format the new message as a command.
        :param printing: If `True`, print the new last line.
        """
        self.__check_context()

        last_line = self._journal[-1]

        # Apply command format, if desired
        if as_command:
            new_message = f"`{new_message}`"  # pragma: no cover

        # Recompose the new last line
        new_last_line = last_line.replace("\n", f" {new_message}.\n")

        # Replace the last line with the new last line
        self._journal[-1] = new_last_line

        if printing:
            logger.info(f"New line:\n  {new_last_line}")

    def remove_last_line(self) -> None:
        """
        Remove the last line of the journal.
        """
        self.__check_context()

        self._journal.pop()
        logger.info("Last line removed.")

    def tag_last_line(
        self, tag_name: str, indexing: bool = True, printing: bool = True
    ) -> None:
        """
        Add a tag based in `tag_name` to the last line of the journal. Calculate
        the correct tag index, if not disabled with `indexing`.

        :param tag_name: The tag name to add.
        :param indexing: If `True`, calculate the next index of the tag.
        :param printing: If `True`, print the new last line.
        """
        self.__check_context()

        last_line = self._journal[-1]

        # Compose the new tag
        new_tag = self.get_next_tag(tag_name, indexing)

        # Compose the new last line to the journal adding the new tag
        new_last_line = last_line.replace("\n", f" {new_tag}.\n")

        # Replace the last line with the new last line
        self._journal[-1] = new_last_line

        if printing:
            logger.info(f"New line:\n  {new_last_line}")

    def get_next_tag(
        self, tag_name: str, indexing: bool = True, printing: bool = True
    ) -> str:
        """
        Print a new full tag, based in the provided `tag_name` and with its
        correct next index after revise the journal, if not disabled with
        `indexing`. This is useful to obtain the tag outside the journal, to
        for example arrange a relative Git repo tag paired with the journal.

        :param tag_name: The tag name to add.
        :param indexing: If `True`, calculate the next index of the tag, if not
            not use an index, only the tag name formatted as `#{tag_name}`.
        :param printing: If `True`, print the new tag.
        :return: The new full tag.
        """
        self.__check_context()

        if indexing:
            new_tag_index = self.__calculate_next_tag_index(tag_name)
        else:
            new_tag_index = ""  # pragma: no cover

        new_tag = f"#{tag_name}{new_tag_index}"

        if printing:
            print(
                new_tag
            )  # Clean output because typically this method is used to capture the tag by a script or command

        return new_tag

    def __format_new_line(
        self,
        message: str,
        signature: Optional[str] = None,
        index: Optional[int] = None,
        as_command: bool = False,
    ) -> str:
        """
        Format a new line to the journal. Caller function should check if the context
        manager is active.

        :param message: The message to write.
        :param signature: The signature to add as the line author. Default is the user name.
        :param index: The index to add to the line. If `None`, next index is calculated.
        :param as_command: If `True`, format the message as a command.
        :param printing: If `True`, print the new line.
        :return: The new line.
        """
        # Calculate the next index
        if index is None:
            index = self.__calculate_next_line_index()

        # Fix next index to have a fixed length
        index = str(index).zfill(4)

        # Solve signature
        if not signature:
            signature = os.getenv("USER")

        # Calculate current data and time
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[
            :-3
        ]  # The last 3 digits of the milliseconds

        # Apply command format, if desired
        if as_command:
            message = f"`{message}`"

        # Compose the new line
        return f"{index}. {now} - {signature} - {message}.\n"

    def __calculate_next_line_index(self) -> int:
        """
        Calculate the next index in the journal, to add a new line.

        :return: The next index.
        """
        try:
            last_line = self._journal[-1]

            # Calculate the next index, which is the `N` of the last line `N. ...`
            index = last_line.split(".")[0]

            return int(index) + 1
        except (IndexError, ValueError):
            return 1  # If the journal is empty, start with 1

    def __calculate_next_tag_index(self, tag_name: str) -> int:
        """
        Calculate the next tag index, to add a new tag to the last line of the journal.

        :param tag_name: The tag name to add.
        :return: The next tag index.
        """
        # Merge all lines as text to process it. Reverse the journal to find the last tag
        all_journal_as_str = "".join(self._journal[::-1])

        # First check if the tag has been already used
        tag_used = all_journal_as_str.find(f"{tag_name}1") != -1
        if tag_used:
            # Calculate last index of the tag in the journal
            index = 1
            while all_journal_as_str.find(f"{tag_name}{index}") != -1:
                index += 1
        else:  # Never used
            index = 1

        return index
