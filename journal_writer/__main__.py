"""
Main
====

This module is the main entry point for the `jw` command line utility. It uses the
`argparse` module to parse the command line arguments and the `JournalWriter` class
to access the functionality.
"""

import argparse
import logging

try:
    from journal_writer import JournalWriter
except ImportError:
    from .journal_writer import JournalWriter

# Setup logger
handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.setLevel("INFO")
formatter = logging.Formatter(
    "%(asctime)s - journal_writer - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_args():
    # Define the parser
    parser = argparse.ArgumentParser(
        prog="jw",
        description="An utility for a high-level machine maintenance journal. Uses the file defined in `JOURNAL` environment variable as the journal file location",
        epilog="Borja González Seoane. All rights reserved",
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--print",
        "-p",
        help="Print the last lines of the journal. Default option",
        action="store_true",
        default=True,
    )
    group.add_argument(
        "--write",
        "-w",
        help="Write the input new line into the journal",
        action="store_true",
        default=False,
    )
    group.add_argument(
        "--append",
        "-a",
        help="Append the input to the last line of the journal",
        action="store_true",
        default=False,
    )
    group.add_argument(
        "--tag",
        "-t",
        help="Add the input tag to the last line of the journal. The next "
        "index of the tag is computed",
        action="store_true",
        default=False,
    )
    group.add_argument(
        "--return_tag",
        "-rt",
        help="Return a fully composed tag after compute its next index, but don't write "
        "it into the journal. This option is useful to obtain the tag to "
        "update other relative logs or Git repositories before writing the "
        "tag into the journal",
        action="store_true",
        default=False,
    )
    group.add_argument(
        "--remove",
        "-r",
        help="Remove the last line of the journal",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--as_command",
        "-c",
        help="Format the input line as a command",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--create_journal",
        "-cj",
        help="Create the journal file if it doesn't exist",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "MESSAGE_OR_TAG",
        help="The message to be written in the journal, or the tag to be added to the last line if the `--tag` option is used",
        type=str,
        nargs="?",
        default=None,
    )

    parser.add_argument(
        "--signature",
        "-s",
        help="The signature to be added as the line author. Default is the user name",
        type=str,
        default=None,
    )

    # Parse or failpython argparse
    return parser.parse_args()


def main():
    # Parse arguments
    args = parse_args()

    # Check that a message is provided when the `--write` or `--append` options are used
    if (args.write or args.append) and args.MESSAGE_OR_TAG is None:
        logger.error("No message to write.")
        return

    # Check that a tag is provided when the `--tag` or `--return_tag` options are used
    if (args.tag or args.return_tag) and args.MESSAGE_OR_TAG is None:
        logger.error("No tag to add.")
        return

    # Create a `JournalWriter` object
    jw = JournalWriter(create_journal=args.create_journal)

    # Enter context an run the command
    with jw:
        if args.write:
            jw.write_line(
                args.MESSAGE_OR_TAG,
                as_command=args.as_command,
                signature=args.signature,
                printing=True,
            )
        elif args.append:
            jw.append_to_last_line(
                args.MESSAGE_OR_TAG, as_command=args.as_command, printing=True
            )
        elif args.tag:
            jw.tag_last_line(args.MESSAGE_OR_TAG, printing=True)

        elif args.return_tag:
            jw.get_next_tag(args.MESSAGE_OR_TAG, printing=True)

        elif args.remove:
            jw.remove_last_line()

        else:  # Default
            jw.print_journal()


if __name__ == "__main__":
    main()
