# Contributing

Small, useful tools are welcome. Open an issue first when proposing a new tool or a substantial behavior change.

## Adding a tool

1. Describe a recurring development problem and explain why a small standalone tool helps.
2. Put the executable in `bin/`, with a descriptive name and a working `--help` option.
3. Prefer standard-library implementations and avoid unnecessary dependencies.
4. Document requirements, installation, examples, limitations, side effects, and exit codes in `docs/`.
5. Add automated tests using temporary directories. Do not access personal repositories, credentials, or the network in tests.
6. Add the tool to the README catalog.

Do not add placeholder tools just to expand the collection.

## Conventions

- Use English for code, documentation, command output, and commit messages.
- Support macOS and Linux unless a tool explicitly documents a narrower target.
- Quote paths, avoid shell evaluation of user input, and test filenames containing spaces.
- Never silently delete user data or overwrite an existing installation.
- Make network access and destructive actions explicit.
- Keep error messages actionable and send them to standard error.

## Running checks

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile bin/gitview
```

For `gitview`, install Vim to run the headless integration test rather than skipping it.

## Pull requests

Explain the problem, summarize the solution, and include the commands used to test it. Keep each pull request focused on one change.
