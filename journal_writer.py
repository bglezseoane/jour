#!/Users/bglezseoane/.pyenv/versions/scripts/bin/python

"""Journal Writer

Script to add a new service entry in the Cartapacio's journal of the
current machine, avoiding the necessity of open and edit the file manually.

Creation: 12/12/2020.
Author: Borja González Seoane.
"""

import os
import platform
import shutil
import sys
from collections import deque
from datetime import datetime

from ilock import ILock, ILockException

################### AUXILIARY FUNCTIONS ###################
def calculate_new_tag_indexed(tag_name: str) -> str:
    """Auxiliary function to calculate a new tag with its correspondent index
    after revise the journal. Isolated here to reuse since different modes."""
    # Read the journal and merge getting lines
    with open(JOURNAL_FILE, "r") as f:
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


###########################################################


# Catch input to a variable
input = sys.argv[1:]

# Help petition
if input[0] == "-h" or input[0] == "--help":
    print(
        """
        Journal Writer script

        Script to add a new service entry in the Cartapacio's 
        journal of the current machine, avoiding the necessity of 
        open and edit the file manually. With the flag '-c' the input is 
        saved formatted as a command (Markdown code syntax).
        With the '-a' flag, the input is appended to the 
        last line, which is useful to edit line with more comments 
        or tags.

        A secondary function ('-e' flag) is echo in the terminal 
        the last lines of the journal.

        Other function is remove ('-r' flag)  the last line of
        the journal, to facilitate its correction.
        
        The journal also has the function to append to the last entry 
        a tag. Using the tag flag ('-t') and the tag name without the 
        index, a tag with the index increased will be added at the 
        final of the last entry. Example: '-t tag' will add 'tag34' if
        the last occurrence of tag 'tag' in the journal was 33. If the 
        name had been never used, uses it and the index 1.
        
        Inputting the flag '-rt' and a tag name is calculated 
        the updated tag index like with the '-t' option, but this time, 
        it is not appended but returned. This option is useful to obtain 
        the tag to update other relative logs. The return include the
        tag name and the tag index, like would be added to the journal.
        
        The new '-st' flag saves a new entry that immediately tags. '-st' 
        refers to save and tag. It is used to collapse this very common 
        operation in an unique call which reduces that possible problems when a
        lot of calls exist in a small space of time. The first chunk still a 
        space after the flag will be the tag, and the rest of the line, 
        the entry.

        Only the first param will be considered as a flag.
        """
    )
    sys.exit(0)

# Normal execution if no help petition...


# Get current machine name
current_machine_name = (
    platform.node().split(".")[0].capitalize()
)  # Cut '.local' and first letter upper
JOURNAL_FILE = os.path.join(
    os.path.expanduser("~"),
    "Cartapacio",
    "Machines",
    f"Journal_of_{current_machine_name}.md",
)
JOURNAL_BACKUP_FILE = f"{JOURNAL_FILE.replace('.md', '.Writer-bup.md')}"

# Parse
command_format_flag = False  # If is set to true, input as command format
append_mode_flag = False  # If is set to true, script as append mode
echo_mode_flag = False  # If is set to true, script as echo mode
remove_mode_flag = False  # If is set to true, script as remove mode
tag_mode_flag = False  # If is set to true, script as tag mode
return_tag_mode_flag = False  # If is set to true, script as return tag mode
save_and_tag_mode_flag = False  # If is set to true, script as save and tag mode
try:
    if not input:
        raise ValueError("Wrong input! Can't be null.")
    # These flags are exclusive with content input, so it is discarded
    if input[0] == "-e":
        echo_mode_flag = True
    elif input[0] == "-r":
        remove_mode_flag = True
    elif input[0] == "-t":
        tag_mode_flag = True
        input.pop(0)  # Consume first param: '-t' flag
        tag_name = input[0]  # Assert string, not list
    elif input[0] == "-rt":
        return_tag_mode_flag = True
        input.pop(0)  # Consume first param: '-t' flag
        tag_name = input[0]  # Assert string, not list
    else:
        if input[0] == "-c":  # This flag is inclusive with content input
            command_format_flag = True
            input.pop(0)  # Consume first param: '-c' flag
        elif input[0] == "-a":  # This flag is inclusive with content input
            append_mode_flag = True
            input.pop(0)  # Consume first param: '-a' flag
        elif input[0] == "-st":  # This flag is inclusive with content input
            save_and_tag_mode_flag = True
            input.pop(0)  # Consume first param: '-st' flag
            tag_name = input[0]  # Consume ans save the tag
            input.pop(0)
        new_entry_content = " ".join(input)
        if not new_entry_content:
            raise ValueError("Wrong input! Can't be null.")
except:
    raise ValueError("Wrong input!")

"""Sometimes this script is called by system daemons almost at the same time, 
so the file can be corrupted by mixing up the line numbers or adding tags to 
other subsequent messages. So it is necessary to control concurrency"""
try:
    with ILock("journal_writer_lock", timeout=25):
        # Save a journal backup copy, if it is going to be written
        shutil.copy(JOURNAL_FILE, JOURNAL_BACKUP_FILE)

        if (
            not echo_mode_flag
            and not remove_mode_flag
            and not tag_mode_flag
            and not return_tag_mode_flag
        ):
            if not append_mode_flag:  # Normal save mode or save and tag mode
                # Read the journal and get its last line
                with open(JOURNAL_FILE, "r") as f:
                    last_line = f.readlines()[-1]

                # Calculate entry index for the new entry
                try:
                    new_entry_index = int(last_line.split(".")[0]) + 1
                except:
                    raise OSError(
                        f"The last line of {JOURNAL_FILE} is not well-formed. "
                        f"The script can not handles this situation. Check it "
                        f"manually."
                    )

                # Append the new entry line to the journal
                now = datetime.now()
                formatted_date = (
                    f"{now.year:04d}-{now.month:02d}-{now.day:02d} "
                    f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
                )
                if command_format_flag:
                    new_entry_content = f"`{new_entry_content}`"  # Apply command format
                new_entry = (
                    f"{new_entry_index}. [{formatted_date}] {new_entry_content}.\n"
                )
                if save_and_tag_mode_flag:
                    new_tag_indexed = calculate_new_tag_indexed(tag_name)
                    new_entry = new_entry.replace("\n", f" #{new_tag_indexed}.\n")

                with open(JOURNAL_FILE, "a") as f:
                    f.write(new_entry)
                print(f"\n   {new_entry}")  # Echo the new added line
            else:  # Append mode
                # Read the journal and get all lines but last and last line separately
                with open(JOURNAL_FILE, "r") as f:
                    all_lines = f.readlines()
                    lines = all_lines[:-1]
                    last_line = all_lines[-1]
                    del all_lines  # Defer

                # Calculate the new last line
                new_last_entry = last_line.replace("\n", f" {new_entry_content}.\n")
                with open(JOURNAL_FILE, "w") as f:
                    for line in lines:
                        f.write(line)
                    f.write(new_last_entry)

                print(f"\n   {new_last_entry}")  # Echo the new last line
        elif echo_mode_flag:
            # Read the journal and print its last lines
            lines = ""
            with open(JOURNAL_FILE, "r") as f:
                for line in deque(f, maxlen=10):
                    lines += line
            print(lines)
        elif remove_mode_flag:
            lines = []
            with open(JOURNAL_FILE, "r") as f:
                lines.extend(f.readlines())
            lines = lines[:-1]  # Remove last line
            with open(JOURNAL_FILE, "w") as f:
                for line in lines:
                    f.write(line)
        elif tag_mode_flag or return_tag_mode_flag:
            # Read the journal and merge getting lines
            with open(JOURNAL_FILE, "r") as f:
                all_lines = f.readlines()
                lines = all_lines[:-1]
                last_line = all_lines[-1]

            new_tag_indexed = calculate_new_tag_indexed(tag_name)

            if tag_mode_flag:
                # Calculate the new last line to the journal and append it
                new_last_entry = last_line.replace("\n", f" #{new_tag_indexed}.\n")
                with open(JOURNAL_FILE, "w") as f:
                    for line in lines:
                        f.write(line)
                    f.write(new_last_entry)

                print(f"\n   {new_last_entry}")  # Echo the new last line
            elif return_tag_mode_flag:
                # Echo the calculated tag, but no use it
                print(new_tag_indexed)

        # If the process has finished well, the backup file can be removed
        os.remove(JOURNAL_BACKUP_FILE)

except ILockException:
    print("Concurrency error: timeout was reached, but the lock wasn't acquired.")
    sys.exit(1)
