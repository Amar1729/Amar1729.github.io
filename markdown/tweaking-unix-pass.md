# QoL Tweaks for Unix PASS

*Jun 18 2020*

With increasing frequency of corporate hacks and password dumps, using a password manager has become more and more important recently. While many "password manager as a service" tools like Dashlane or 1Password exist, there are also open-source options like [KeePass](https://keepass.info/), [gopass](https://github.com/gopasspw/gopass), and [pass](https://www.passwordstore.org/).

I personally use `pass` to manage passwords. While there are many tutorials out there on setting up GPG keys, using `pass`, using its git integration, and using apps built for `pass`, this post focuses more on some of the minor "quality of life" tweaks I've done to make using it easier.

## fuzzy-find nested passwords

I use a nested hierarchy to keep my passwords and sensitive codes somewhat organized:

```
$ pass list

Password Store
├── social
│   ├── discord
│   ├── irc
│   └── keybase
├── banks
│   ├── bank1
│   ├── cc1
│   └── cc2

/* snipped */
```

But attempting to tab-complete for passwords when I don't immediately remember which directory they're in can be tedious. Enter [fzf](https://github.com/junegunn/fzf), a command-line fuzzy finder. If you're not using this already, you should check it out, but one of the things I used it for is fuzzy tab completion of passwords. Based off of a snippet in fzf's wiki, I dropped this snippet in a file sourced by my shell startup:

```
# $XDG_CONFIG_HOME/fzf/fzf_aliases

# pass completion suggested by @d4ndo (#362) (slightly modified)
_fzf_complete_pass() {
  _fzf_complete '+m' "$@" < <(
    local pwdir=${PASSWORD_STORE_DIR-~/.password-store/}
    find "$pwdir" -name "*.gpg" -print |
        sed -e "s#${pwdir}/\{0,1\}##" |
        sed -e 's/\(.*\)\.gpg/\1/'
  )
}
```

And now I can simply use fzf's default trigger `**` for fuzzy tab-completion:

```
$ pass show gith**[TAB]

$ pass show gith**
> gith
  2/215
> backups/github1
  social/github.com
```

## Prefer `pinentry-curses` for CLI usage

Since I use [`browserpass`](https://github.com/browserpass/browserpass-extension) - which I highly recommend - for web page logins, I need `pass` to be able to query a GUI pinentry program for my master password (you need to enter this every time you query a password from your password store). However, many times I'll copy or show a password using the command-line, and in those cases I'd prefer `pass` to fall back to using `pinentry-curses`, rather than a GUI pop-up.

I found [this post](https://kevinlocke.name/bits/2019/07/31/prefer-terminal-for-gpg-pinentry/) by Kevin Locke a while back detailing this problem. Relevant post text copied here:

> As a result of [Task 799](https://dev.gnupg.org/T799), GnuPG 2.08 and later pass the `PINENTRY_USER_DATA` environment
> variable from the calling environment to gpg-agent to pinentry. The format of this variable
> is not specified (and not used by any programs in the standard pinentry collection that I can
> find). [pinentry-mac](https://github.com/GPGTools/pinentry-mac) [assumes it is a comma-separated sequence of NAME=VALUE pairs with no quoting
> or escaping](https://github.com/GPGTools/pinentry-mac/blob/v0.9.4/Source/AppDelegate.m#L78) and [recognizes USE_CURSES=1 to control curses fallback](https://github.com/GPGTools/pinentry-mac/pull/2). I adopted this convention
> for a simple pinentry script which chooses the UI based on the presence of `USE_TTY=1` in `$PINENTRY_USER_DATA`:

The original post includes a script which I have slightly modified for my use on macOS:

```
#! /usr/bin/env bash

# Based on:
# https://kevinlocke.name/bits/2019/07/31/prefer-terminal-for-gpg-pinentry

set -Ceu

case "${PINENTRY_USER_DATA-}" in
    *USE_TTY=1*)
        exec /usr/local/bin/pinentry-curses "$@"
        ;;
    *)
        # fallback
        exec /usr/local/bin/pinentry-mac "$@"
        ;;
esac
```

On Linux, similar to the original post, you would use `pinentry-x11` rather than `pinentry-mac` for the GUI fallback.

Note - the paths may have to be edited somewhat if you've installed these binaries to different locations.

And to use it (re-copied for posterity from post):

> To use this script for pinentry:
> 
> 1. Save the script (e.g. as `~/bin/pinentry-auto`).
> 2. Make it executable (`chmod +x pinentry-auto`).
> 3. Add `pinentry-program /path/to/pinentry-auto` to `~/.gnupg/gpg-agent.conf`.
> 4. `export PINENTRY_USER_DATA=USE_TTY=1` in environments where prompting via TTY is desired (e.g. alongside `$GPG_TTY` in `~/.bashrc`).

When testing `pass` with this updated pinentry, make sure to execute `gpgconf --kill gpg-agent` after editing `~/.gnupg/gpg-agent.conf`.

### Aside: Writing a HomeBrew Formula

I like to have my tools and scripts easily installable, so I screwed around a little and made a homebrew formula for slightly easier install of this script on macOS.

The [introductory commit](https://github.com/Amar1729/homebrew-formulae/commit/ce19e14e61899ad5eb8b04669f35f4810af4413b) can be seen in my homebrew tap. This formula utilizes some common patterns for formulae, such as the use of `inreplace` and using the fully-qualified path of a formula with `#{Formula["pinentry"].opt_bin}`.

Check out homebrew's [formula cookbook](https://docs.brew.sh/Formula-Cookbook) for more information, or take a look at the homebrew formula files - usually found in `$(brew --prefix)/Homebrew/Library/Taps/homebrew/homebrew-core/Formula`.

----

~ tags : #ricing * #brew
