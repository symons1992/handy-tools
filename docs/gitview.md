# gitview

Browse your branch's changes in Vim without searching through the entire project tree.

```text
+-------------------+------------------------------------------------+
| Changed files     | Code                                           |
|                   |                                                |
| src/client.py     | Selected file, with your usual Vim setup       |
| src/config.py     |                                                |
| docs/api.md       |                                                |
+-------------------+------------------------------------------------+
       ~20%                            ~80%
```

The sidebar uses Vim's built-in quickfix window. No file-tree plugin is required.

## Requirements

- Python 3.10 or later, with no third-party Python packages.
- A recent Git supporting `rev-parse --end-of-options`.
- Vim 8 or later, built with JSON support.
- Optional: [vim-gitgutter](https://github.com/airblade/vim-gitgutter) for changed-line signs.

## Usage

```sh
gitview [BRANCH] [OPTIONS]
```

| Argument / option | Default | Description |
| --- | --- | --- |
| `BRANCH` | `dev` | Branch, remote-tracking branch, tag, or commit to compare against |
| `-x, --exclude REGEX` | None | Exclude repository-relative paths matching a Python regular expression |
| `--width PERCENT` | `20` | Initial sidebar width, from 1 to 80 percent |
| `--vim EXECUTABLE` | `vim` | Vim executable name or path; shell command strings are not supported |
| `--list` | Off | Print repository-relative paths without opening Vim |
| `-0, --null` | Off | Use NUL separators with `--list` for machine-readable output |
| `--version` | | Print the tool version |
| `-h, --help` | | Show help |

Examples:

```sh
gitview
gitview main
gitview origin/dev --exclude '(^|/)(tests?|vendor)/'
gitview dev --width 25
gitview --vim /usr/bin/vim
gitview --list --null | xargs -0 -n 1 printf '%s\n'
```

The tool works from subdirectories and runs Vim from the repository root. It does not change the calling shell's working directory.

## What counts as a change?

The comparison base is:

```sh
git merge-base HEAD dev
```

The file set is equivalent to:

```sh
git diff --name-only --diff-filter=d "$(git merge-base HEAD dev)"
```

This includes committed changes on your branch, staged changes, and unstaged changes to tracked files. It does **not** include:

- Untracked files: inspect these with `git status --short`.
- Deleted paths: these cannot be opened as existing files.
- Changes exclusive to `dev` after the branches diverged.

The final net difference is what matters. A committed edit that is later fully undone will not appear.

The branch must exist locally. For a remote-tracking branch, fetch explicitly when needed:

```sh
git fetch origin
gitview origin/dev
```

Nothing is fetched, staged, committed, or pushed automatically. A normal Vim session can still save files as usual, and your own Vim configuration and plugins are loaded.

## Navigation

| Action | Key or command |
| --- | --- |
| Open the selected file | `Enter` in the sidebar |
| Switch windows | `Ctrl-w w` |
| Next changed file | `:cnext` |
| Previous changed file | `:cprevious` |
| Close the sidebar | `:cclose` |
| Reopen it vertically | `:vertical copen` |

The initial width is calculated from Vim's total screen width. `noequalalways` prevents automatic equal sizing, and the sidebar uses `winfixwidth` to preserve its width during ordinary window changes. This is not a continuously maintained percentage: terminal resizing and plugins that explicitly resize windows can still affect it.

The changed-file list is a snapshot taken at launch. Restart `gitview` to refresh it after edits, branch switches, or updates to the comparison branch.

## Optional GitGutter integration

With Vundle, add this inside your plugin block:

```vim
Plugin 'airblade/vim-gitgutter'
```

Restart Vim, then run:

```vim
:PluginInstall
```

`gitview` sets `g:gitgutter_diff_base` to the same merge-base commit used for its file list. GitGutter can therefore display committed and uncommitted line changes relative to that base, instead of only changes relative to `HEAD`.

For full-line highlighting:

```vim
:GitGutterLineHighlightsEnable
```

## Troubleshooting

### `gitview` still runs an old shell function

Remove the old function from your shell configuration, then open a new terminal. Use `type gitview` to inspect what your shell resolves.

### Missing branch

Pass an existing branch, or fetch a remote branch explicitly. The default is `dev`, not an automatically detected default branch.

### Sidebar width changes unexpectedly

A directory plugin may explicitly resize other windows, overriding Vim's width preferences. Focus the sidebar and restore its width:

```vim
:execute 'vertical resize ' . max([1, &columns * 20 / 100])
:setlocal winfixwidth
```

### Filenames with spaces or newlines

Git paths are read with NUL separators and passed to Vim as JSON quickfix entries, not shell commands. Use `--list --null` when consuming the output programmatically. Plain `--list` is intended for human-readable paths and is ambiguous for filenames containing newlines.

## Exit status

- `0`: successful listing, no matching changes, or a normally exited Vim session.
- `1`: Git, filesystem, or missing-editor error.
- `2`: invalid command-line arguments.
- `130`: interrupted by the user during Python execution.

When Vim is launched, its exit status is returned.
