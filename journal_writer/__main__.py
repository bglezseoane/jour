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

from journal_writer.functions import *

if __name__ == "__main__":
    # Define the parser
    parser = argparse.ArgumentParser(
        prog="Journal Writer",
        description="A Borja Glez. Seoane's ad-hoc utility to write his Cartapacio.",
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
        print("[PARSE ERROR] Revise command.")
        sys.exit(1)

    # Fix journal file name
    if not args.custom_journal:
        journal_file = get_journal_filename()
    else:
        journal_file = os.path.abspath(args.custom_journal[0])

    # Check journal file existence
    if not os.path.isfile(journal_file):
        print(f"[CONFIG ERROR] Journal file in '{journal_file}' unreachable.")
        sys.exit(1)

    # Check options and run
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
        tag_last_line(journal_file, args.tag[0])
    elif args.return_tag:
        return_next_tag(journal_file, args.return_tag[0])
    elif args.save_and_tag:
        save_line(
            journal_file,
            " ".join(args.save_and_tag[1:]),
            as_command=args.command,
            printing=False,
        )
        tag_last_line(journal_file, args.save_and_tag[0])
    elif args.remove:
        remove_last_line(journal_file)
