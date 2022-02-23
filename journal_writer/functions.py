###########################################################
#                      Journal Writer
#
#           A Borja G. Seoane's ad-hoc utility to
#                   write his Cartapacio
#
# Copyright 2022 Borja González Seoane. All rights reserved
###########################################################

"""
Functions module
================

This module closures the function definitions used along these package.
"""

import datetime
from collections import deque

################### MAIN FUNCTIONS ###################


def print_journal(journal_file: str) -> None:
    """Read the journal and print its last lines."""
    lines = ""
    with open(journal_file, "r") as f:
        for line in deque(f, maxlen=10):
            lines += line
    print(lines)


def save_line(journal_file: str, content: str, as_command: bool = False) -> None:
    """Save a new line to the journal."""

    # Calculate new line index
    index = calculate_next_line_index(journal_file)

    # Calculate current data and time
    now = datetime.datetime.now()
    date = (
        f"{now.year:04d}-{now.month:02d}-{now.day:02d} "
        f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
    )

    # Apply command format, if desired
    if as_command:
        content = f"`{content}`"

    new_line = f"{index}. [{date}] {content}.\n"

    # Write and print the new line
    with open(journal_file, "a") as f:
        f.write(new_line)
    print(f"\n   {new_line}")


def append_to_last_line(journal_file: str, new_content: str, as_command: bool = False):
    """Add some new content to the last line of the journal."""

    # Read the journal and get all lines but last and last line separately
    with open(journal_file, "r") as f:
        all_lines = f.readlines()
        lines_but_last = all_lines[:-1]
        last_line = all_lines[-1]
        del all_lines  # Defer

    # Apply command format, if desired
    if as_command:
        new_content = f"`{new_content}`"

    # Recompose the new last line
    new_last_line = last_line.replace("\n", f" {new_content}.\n")

    # Write again the last line and print it
    with open(journal_file, "w") as f:
        for line in lines_but_last:
            f.write(line)
        f.write(new_last_line)
    print(f"\n   {new_last_line}")


def remove_last_line(journal_file: str) -> None:
    """Remove the last line of the journal."""
    lines = []
    with open(journal_file, "r") as f:
        lines.extend(f.readlines())
    lines = lines[:-1]  # Remove last line
    with open(journal_file, "w") as f:
        for line in lines:
            f.write(line)


def tag_last_line(journal_file: str, tag_name: str) -> None:
    """Add a tag based in `tag_name` to the last line of the journal. Calculate
    the correct tag index.
    """

    # Read the journal and get all lines but last and last line separately
    with open(journal_file, "r") as f:
        all_lines = f.readlines()
        lines_but_last = all_lines[:-1]
        last_line = all_lines[-1]
        del all_lines  # Defer

    new_tag = calculate_next_tag(journal_file, tag_name)

    # Calculate the new last line to the journal and write it
    new_last_line = last_line.replace("\n", f" #{new_tag}.\n")
    with open(journal_file, "w") as f:
        for line in lines_but_last:
            f.write(line)
        f.write(new_last_line)

    print(f"\n   {new_last_line}")  # Print the new last line


def return_next_tag(journal_file: str, tag_name: str) -> None:
    """Print a new full tag, based in the provided `tag_name` and with its
    correct next index after revise the journal.
    """
    print(calculate_next_tag(journal_file, tag_name))


################### HELP FUNCTIONS ###################


def calculate_next_line_index(journal_file: str) -> str:
    """Calculate the following index in the journal, to add a new line."""

    # Read the journal and get its last line
    with open(journal_file, "r") as f:
        last_line = f.readlines()[-1]

    # Calculate entry index for the new entry
    try:
        return str(int(last_line.split(".")[0]) + 1)
    except:
        raise OSError(
            f"The last line of {journal_file} is not well-formed. "
            f"The script can not handles this situation. Check it "
            f"manually."
        )


def calculate_next_tag(journal_file: str, tag_name: str) -> str:
    """Calculate a new full tag, based in the provided `tag_name` and with its
    correct next index after revise the journal.
    """

    # Read the journal and merge getting lines
    with open(journal_file, "r") as f:
        all_lines = f.readlines()

    # Merge all lines as text to process it
    all_text = ""
    for line in reversed(all_lines):  # Reverse lines to find first last tag indexes
        all_text += line

    # First check if the tag has been already used
    tag_used = all_text.find(f"{tag_name}1") != -1
    if tag_used:
        # Calculate last index of the tag in the journal
        index = 1
        while all_text.find(f"{tag_name}{index}") != -1:
            index += 1
        new_tag_indexed = f"{tag_name}{index}"  # Last index incremented one
    else:
        new_tag_indexed = f"{tag_name}1"

    return new_tag_indexed
