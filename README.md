# Journal Writer

This repository contains the Journal Writer tool, an utility for a high-level machine maintenance journal. The final purpose of this tool is to write and handle a journal in which the user or some automated process can write and tag the performed actions related with the machine configuration, maintenance, and other relevant information. This way, the user can keep track of the changes and the performed actions, and also can obtain a high-level overview of the machine status over time.

Some examples of the usage of this tool could be:

- Write a journal entry with a tag, for example, to keep track of the performed updates in the machine.
- Write a journal entry with a tag with a system backup.
- Write a journal entry with a tag with a relevant system configuration change: like the installation of a new package, the change of a configuration file, etc.

After some time, the user can obtain a high-level traceability of the machine changes and fixes, helping even to debug some issues or roll back to a previous state.

## Installation

Uploaded to private GitHub repository \[[1]\] and available since private Homebrew tap \[[2]\] —once enabled—, using:

```sh
brew install journal_writer
```

## Usage

```sh
jw --help # Show the help message with the available commands and options
```

Basically, each new journal entry is a new line in the journal file, with an index and a date. The index is useful to cross-reference the journal entries. The entries are appended to the journal file sequentially. The journal file location is defined in the environment variable `JOURNAL` and if the tool cannot reach the file, the incoming entries are stored in an emergency journal file, which location is `JOURNAL_EMERGENCY` if defined or `~/.journal_emergency` otherwise. This is useful if, for example, the journal file is located in a remote file system or cloud provider and the connection is lost. The user can then arrange the journal entries merging the emergency journal manually.

In addition to the entries, the tool also handle tags, like `#backup1`, to an easier navigation of the journal file. This is specially useful to link the journal entries with tags in a configuration Git repository, for example, because a journal tag can be also set in the repo.

Journal format is Markdown, so the user can also format all the history to a more readable format, like a PDF, using a Markdown to PDF converter.

<!-- References -->

[1]: https://github.com/bglezseoane/journal-writer
[2]: https://github.com/bglezseoane/homebrew-private-tap
