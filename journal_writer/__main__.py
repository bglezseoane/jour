#!/usr/bin/env python3

###########################################################
#                      Journal Writer
#
#         A Borja Glez. Seoane's ad-hoc utility to
#                   write his Cartapacio
#
# Copyright 2022 Borja González Seoane. All rights reserved
###########################################################

"""
Main
====

Parser and main handler of this utility. Consume the `functions.py` module.
"""

import argparse
import sys

from colorama import Fore, Style
from ilock import ILock, ILockException

from journal_writer.functions import *


def main():
    # Define the parser
    parser = argparse.ArgumentParser(
        prog="jw",
        description="Journal Writer ('jw') is a Borja Glez. Seoane's ad-hoc "
        "utility to write his Cartapacio.",
        epilog="Copyright 2022 Borja González Seoane. All rights reserved",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--print",
        "-p",
        "--echo",  # Legacy
        "-e",  # Legacy
        help="Print the last lines of the journal. Default option",
        action="store_true",
    )
    group.add_argument(
        "--save",
        "-s",
        help="Save the input line into the journal",
        metavar="MESSAGE",
        nargs="+",
    )
    group.add_argument(
        "--append",
        "-a",
        help="Append the input to the last line of the journal",
        metavar="MESSAGE",
        nargs="+",
    )
    group.add_argument(
        "--tag",
        "-t",
        help="Append the input tag to the last line of the journal. The next "
        "index of the tag is computed",
        nargs=1,
    )
    group.add_argument(
        "--return_tag",
        "-rt",
        help="Return a full tag after compute its next index, but don't write "
        "it into the journal. This option is useful to obtain the tag to "
        "update other relative logs",
        nargs=1,
    )
    group.add_argument(
        "--save_and_tag",
        "-st",
        help="Save a new line inputted and append to it the tag inputted as "
        "first parameter",
        metavar=("TAG", "MESSAGE"),
        nargs="+",
    )
    group.add_argument(
        "--remove",
        "-r",
        help="Remove the last line of the journal",
        action="store_true",
    )
    parser.add_argument(
        "--command",
        "-c",
        help="Format the input line as a command",
        action="store_true",
    )
    parser.add_argument(
        "--custom_journal",
        "-cj",
        help="Define a custom journal where write",
        nargs=1,
    )

    # Parse
    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        print(Fore.RED + "[PARSE ERROR]" + Style.RESET_ALL + " Revise command.")
        sys.exit(1)

    # Get current machine name
    current_machine_name = (
        platform.node().split(".")[0].capitalize()
    )  # Cut '.local' and first letter upper
    # Compute emergency journal file name
    emergency_journal_file = os.path.join(
        os.path.expanduser("~"),
        "Desktop",
        f"Emergency_journal_{current_machine_name}.md",
    )

    # Fix journal file name
    if not args.custom_journal:
        journal_file = get_journal_filename()
    else:
        journal_file = os.path.abspath(args.custom_journal[0])
        if not os.path.isfile(journal_file):
            # Emergency journal support doesn't apply using custom journal
            print(
                Fore.RED
                + "[CONFIG ERROR]"
                + Style.RESET_ALL
                + f" Custom set journal file in '{journal_file}' unreachable. Aborted."
            )
            sys.exit(1)

    # Check journal file existence
    using_emergency_journal = False
    if not os.path.isfile(journal_file):
        print(
            Fore.YELLOW
            + "[WARNING]"
            + Style.RESET_ALL
            + f" Journal file in '{journal_file}' unreachable. Using emergency "
            f"journal instead."
        )
        using_emergency_journal = True
        original_journal_file = journal_file
        journal_file = use_emergency_journal(emergency_journal_file)
    # Check emergency journal file reachability
    if using_emergency_journal and not os.path.isfile(journal_file):
        # noinspection PyUnboundLocalVariable
        print(
            Fore.RED
            + "[CONFIG ERROR]"
            + Style.RESET_ALL
            + f" Emergency journal file in '{journal_file}' unreachable. Original "
            f"journal in ''{original_journal_file} also unreachable. Aborted."
        )
        sys.exit(1)

    # Warning if emergency journal exist, if not already warning
    if not using_emergency_journal:
        print(
            Fore.YELLOW
            + "[WARNING]"
            + Style.RESET_ALL
            + f" Emergency journal file in '{emergency_journal_file}' pending to be "
            f"merged with main journal."
        )

    # Check options and run. Sometimes this script is called by system daemons
    # almost at the same time, so the file can be corrupted by mixing up the
    # line numbers or adding tags to other subsequent messages. So it is
    # necessary to control script concurrent usages. This lock the use since this
    # current script, not the file itself
    try:
        with ILock("journal_writer", timeout=5 * 60):  # 5 minutes timeout
            if (
                not args.save
                and not args.append
                and not args.tag
                and not args.return_tag
                and not args.save_and_tag
                and not args.remove
            ):  # Printing is the default option. Multiple options at once disabled since parser
                print_journal(journal_file)
            elif args.save:
                save_line(journal_file, " ".join(args.save), as_command=args.command)
            elif args.append:
                append_to_last_line(
                    journal_file, " ".join(args.append), as_command=args.command
                )
            elif args.tag:
                tag_last_line(
                    journal_file, args.tag[0], indexing=not using_emergency_journal
                )
            elif args.return_tag:
                return_next_tag(
                    journal_file,
                    args.return_tag[0],
                    indexing=not using_emergency_journal,
                )
            elif args.save_and_tag:
                save_line(
                    journal_file,
                    " ".join(args.save_and_tag[1:]),
                    as_command=args.command,
                    printing=False,
                )
                tag_last_line(
                    journal_file,
                    args.save_and_tag[0],
                    indexing=not using_emergency_journal,
                )
            elif args.remove:
                remove_last_line(journal_file)
    except ILockException:
        print(
            Fore.RED
            + "[CONCURRENCY ERROR]"
            + Style.RESET_ALL
            + " Timeout was reached, but the lock wasn't acquired."
        )
        sys.exit(1)
    except Exception as e:
        print(
            Fore.RED + "[RUNTIME ERROR]" + Style.RESET_ALL + " Exception raised: '{e}'"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
