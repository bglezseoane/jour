# Jour

This repository contains the Jour tool, an utility for a high-level machine maintenance journal. The final purpose of this tool is to write and handle a journal in which the user or some automated process can write and tag the performed actions related with the machine configuration, maintenance, and other relevant information. This way, the user can keep track of the changes and the performed actions, and also can obtain a high-level overview of the machine status over time.

Some examples of the usage of this tool could be:

1. Write a journal entry to register an OS update. Just run the following command in the terminal:

```sh
jour --write 'OS update to 24.5.2'
```

Output:

```
0014. 2024-03-16 17:04:50,123 - test_username - OS update to 24.5.2.
```

2. Write a journal entry about a backup of the machine. Use a Jour tag.

```sh
jour --write 'General system backup' && jour --tag 'BUP'
```

Output:

```
0015. 2024-03-16 17:06:08,630 - test_username - General system backup. #BUP1
```

3. Register other backup some time later. Use the same tag. Take into account that the tag index is automatically incremented, like the entry index.

```sh
jour --write 'General system backup' && jour --tag 'BUP'
```

Output:

```
0016. 2024-03-16 17:09:14,123 - test_username - General system backup. #BUP2
```

You could then use these same tags `BUP1`, `BUP2`, etc. to also tag a commit in a Git repository with your machine config or dotfiles. This way your Jour journal and your machine config are paired.

### The journal file

Basically, each new journal entry is a new line in the journal file, with an index and a date. The index is useful to cross-reference the journal entries. The entries are appended to the journal file sequentially. The journal file location is defined in the environment variable `$JOURNAL` (or, by default in `~/journal.md`). If the tool cannot reach the file, the incoming entries are stored in an emergency journal file, which location is `$JOURNAL_EMERGENCY`, if defined, or `~/journal_emergency.md`, otherwise. This is useful if, for example, the journal file is located in a remote file system or cloud provider and the connection is lost. The user can then manually arrange the journal entries merging the emergency journal.

In addition to the entries, like explained before, the tool also handle tags, like `#BUP1`, to an easier navigation of the journal file. This is specially useful to link the journal entries with tags in a configuration Git repository, for example, because a journal tag can be also set in the repo.

Journal format is Markdown, so the user can also export all the history to a more readable format, like a PDF, using a Markdown to PDF converter.

After some time, the user can obtain with Jour a high-level traceability of the machine changes and fixes, helping even to debug some issues or roll back to a previous state.

## Installation

### Homebrew

First add Jour author's public [tap](https://github.com/bglezseoane/homebrew-tap):

```sh
brew tap bglezseoane/tap
```

Then install Jour with:

```sh
brew install jour
```

### PyPI

This tool is [publicly available in PyPI](https://pypi.org/project/jour), so you could use any method that consumes this registry to install it (like `pip`). As a recommendation, you could use PipX:

```
pipx install jour

# Or...
pip install jour
```
