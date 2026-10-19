# Handy Tools

Small, focused tools for everyday development. Easy to inspect, easy to run, and useful across repositories.

The collection starts with **gitview**. New tools should earn their place by solving a real, recurring problem—not by filling out a catalog.

## Tools

| Tool | Purpose | Requirements |
| --- | --- | --- |
| [gitview](docs/gitview.md) | Browse branch changes in Vim with a fixed-width file sidebar and optional GitGutter highlighting | Python 3.10+, Git, Vim 8+ with JSON support |

## Install

On macOS or Linux:

```sh
git clone https://github.com/symons1992/handy-tools.git "$HOME/.local/share/handy-tools"
```

Add this line to your `~/.zshrc` or `~/.bashrc`:

```sh
export PATH="$HOME/.local/share/handy-tools/bin:$PATH"
```

Open a new terminal, then run:

```sh
gitview --help
```

If you previously installed a shell function named `gitview`, remove its definition from your shell configuration and open a new terminal. Shell functions take precedence over executables on `PATH`.

To update:

```sh
git -C "$HOME/.local/share/handy-tools" pull --ff-only
```

## Quick start

Run from any directory inside a Git repository:

```sh
gitview                             # Compare against the merge base with dev
gitview main                        # Use a different base branch
gitview origin/dev -x 'test|vendor'  # Exclude matching relative paths
gitview --width 25                   # Set the sidebar to 25% of Vim's width
gitview --list                       # Print changed files without opening Vim
```

In Vim, press **Enter** on a sidebar entry to open it. Use **Ctrl-w w** to switch between the sidebar and the editor.

The comparison includes committed, staged, and unstaged tracked changes. Untracked files and deleted paths are not shown. Remote-tracking branches are not fetched automatically.

See the [gitview guide](docs/gitview.md) for comparison semantics, GitGutter setup, and troubleshooting.

## Principles

- **Focused:** each tool does one job well.
- **Portable:** macOS and Linux first; no unnecessary dependencies.
- **Transparent:** readable source, documented behavior, actionable errors.
- **Safe by default:** no destructive repository operations or automatic network access.
- **Tested:** behavior is exercised with isolated repositories and no network access.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Tests cover Git comparisons, filtering, unusual filenames, error handling, and a real headless Vim session. The Vim test is skipped when Vim is not installed.

See [CONTRIBUTING.md](CONTRIBUTING.md) before adding a tool.

## License

[MIT](LICENSE)
