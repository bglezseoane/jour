# Journal Writer

This repository contains the Journal Writer, a Borja Glez. Seoane's ad-hoc utility to write his Cartapacio.

Usage:

```
usage: jw [-h] [--print | --save MESSAGE [MESSAGE ...] | --append MESSAGE
          [MESSAGE ...] | --tag TAG | --return_tag RETURN_TAG | --save_and_tag
          TAG [MESSAGE ...] | --remove] [--command]
          [--custom_journal CUSTOM_JOURNAL]

Journal Writer ('jw') is a Borja Glez. Seoane's ad-hoc utility to write his
Cartapacio.

optional arguments:
  -h, --help            show this help message and exit
  --print, -p, --echo, -e
                        Print the last lines of the journal. Default option
  --save MESSAGE [MESSAGE ...], -s MESSAGE [MESSAGE ...]
                        Save the input line into the journal
  --append MESSAGE [MESSAGE ...], -a MESSAGE [MESSAGE ...]
                        Append the input to the last line of the journal
  --tag TAG, -t TAG     Append the input tag to the last line of the journal.
                        The next index of the tag is computed
  --return_tag RETURN_TAG, -rt RETURN_TAG
                        Return a full tag after compute its next index, but
                        don't write it into the journal. This option is useful
                        to obtain the tag to update other relative logs
  --save_and_tag TAG [MESSAGE ...], -st TAG [MESSAGE ...]
                        Save a new line inputted and append to it the tag
                        inputted as first parameter
  --remove, -r          Remove the last line of the journal
  --command, -c         Format the input line as a command
  --custom_journal CUSTOM_JOURNAL, -cj CUSTOM_JOURNAL
                        Define a custom journal where write

Copyright 2022 Borja González Seoane. All rights reserved
```

Uploaded to private GitHub repository \[[1]\] and available since private Homebrew tap \[[2]\], using:

```sh
brew install journal_writer
```

<!-- References -->

[1]: https://github.com/bglezseoane/journal-writer
[2]: https://github.com/bglezseoane/homebrew-private-tap
