# speeding up zsh startup

*Sept 09 2019*

While `zsh` is a powerful upgrade to the bash shell, its learning curve can be daunting. As a result, lots of new users will find themselves following whatever looks prettiest or most popular in the way of "getting zsh setup" - and one of the loudest pieces of advice out there is to use [ohmyzsh](https://github.com/ohmyzsh/ohmyzsh).

(at the risk of sounding alarmist ...)

**do NOT use oh-my-zsh!**

Oh-My-Zsh is a great project, but it ends up just bloating your zsh startup. Now if you only spawn a shell infrequently, or your primary editor is VSCode or Atom, it doesn't really matter how fast or slow your shell starts. But if you primarly use tmux+vim and your workflow regularly has you spawning and terminating shells to do simple one-off things, saving half a second of startup time feels like a huge improvement.

The OMZ prompts are pretty, but they can make your REPL feel like molasses. Even worse, the ones rely on [`oh-my-zsh/lib/git.zsh`](https://github.com/ohmyzsh/ohmyzsh/blob/master/lib/git.zsh) for Version Control System helper functions slow to crawl when you `cd` into any decently large or hierarchical git project. (For a neat fix to this problem, see [[1]](#sources)).

## alternatives ...

Before getting back to oh-my-zsh, I'll point out a neat dotfiles repo I found a while back (and in particular, the zsh configuration):

* https://github.com/ThiefMaster/zsh-config/tree/master/zshrc.d

You can check out the various files `ThiefMaster` (most well-commented) to see exactly what all settings you might like in your own .zshrc or .zshrc.d. I'd encourage you to take a glance and use some of these settings as the basis for your own configurations.

And the simplified theme I currently use (internal code roughly based of off the [agnoster theme](https://github.com/agnoster/agnoster-zsh-theme):

* https://github.com/Amar1729/bash-extended

## ... and workarounds

As for Oh-My-Zsh - it is popular, in part, because it helps to provide some nice, sane defaults that zsh is missing. Well, if you are using a plugin manager like [antibody](http://getantibody.github.io/) (highly recommended) you can strip out the settings/tweaks parts of OMZ easily:

```
# ~/.zsh_plugins.txt
robbyrussell/oh-my-zsh kind:zsh path:lib/completion.zsh
robbyrussell/oh-my-zsh kind:zsh path:lib/history.zsh
robbyrussell/oh-my-zsh kind:zsh path:lib/key-bindings.zsh
```

This allows you to pull out the parts of omz that are really useful all-around settings, like options for more history, keybindings like `space` for history expansion or `\C-x\C-e` for opening the current line in your `$EDITOR`, and helpful zstyle completions and menu options for taking advantage of zsh's completion system.

It **also** allows you to avoid sourcing the other **16** (currently) zsh files in `lib/` which you may never use! I don't need bzr or nvm functionality at all; `functions.zsh` and `git.zsh` are mainly helper functions for other omz-internal scripts or themes; and I don't need settings defined in `directories.zsh` when I've already written them [in my .zshrc](https://github.com/Amar1729/dotfiles/blob/a8ddd0ffd9f8464bd584f50da956b7b489e239fb/.zshrc#L53-L59) and use [rupa/z](https://github.com/rupa/z) + [Tarrasch/zsh-bd](https://github.com/Tarrasch/zsh-bd) + [junegunn/fzf](https://github.com/junegunn/fzf) to move around.

If you take a look at [oh-my-zsh's init script](https://github.com/ohmyzsh/ohmyzsh/blob/master/oh-my-zsh.sh) you'll see that there are quite a few other files that may be sourced even though you don't really need them.

## profiling

Lots of great blog posts have been written on profiling zsh startup times[[2]](#sources)[[3]](#sources)[[4]](#sources)[[5]](#sources)[[6]](#sources).

For this section, I'll let those references stand, and just include a few snippets of my own I've found helpful.

```
# timing zsh startup quickly
$ for i in {1..10}; do /usr/bin/time zsh -i -c ''; done
```

```
# ~/.zshrc
# source: 4,5,7

# only run full compinit once a day - compinit -C does not run compaudit, whereas compinit does
autoload -Uz compinit

for dump in ~/.zcompdump(N.mh+24); do
  compinit
done

compinit -C
```

`compaudit` is a part of the zsh completion system that will attempt to check whether there are unsafe paths/files in your `fpath` that it shouldn't load completions from. Initializing `compinit` will generally call `compaudit`, but it can be slow. From [the zsh completion manpages](http://zsh.sourceforge.net/Doc/Release/Completion-System.html#Initialization) ("20.2.1 Use of compinit"):

> For security reasons compinit also checks if the completion system would use files not owned by root or by the current user, or files in directories that are world- or group-writable or that are not owned by root or by the current user. If such files or directories are found, compinit will ask if the completion system should really be used. To avoid these tests and make all files found be used without asking, use the option -u, and to make compinit silently ignore all insecure files and directories use the option -i. This security check is skipped entirely when the -C option is given.

So we should make sure you use `compinit -C` for typical shell loads, and just `compinit` every once in a while.

```
# lazy-load sdkman (a cli tool to help manage java/bulid system versions
# source: 8

# ~/.profile
export SDKMAN_DIR="$HOME/.sdkman"
sdk () {
    if [[ "$(which sdk | wc -l)" -le 10 ]]; then
        unset -f sdk
        source "$SDKMAN_DIR/bin/sdkman-init.sh"
    fi
    sdk "$@"
}
```

On the topic of lazy-loading, peep [[9]](#sources) - a plugin that helps you do lazy-loading could help reduce your startup time even more.

```
# and finally, my zsh startup time ... in the old days this was anywhere from ~0.50 to ~0.80
/tmp $ for i in {1..10}; do /usr/bin/time zsh -i -c ''; done

        0.15 real         0.08 user         0.05 sys
        0.13 real         0.07 user         0.04 sys
        0.13 real         0.07 user         0.04 sys
        0.13 real         0.07 user         0.04 sys
        0.14 real         0.07 user         0.05 sys
        0.13 real         0.07 user         0.04 sys
        0.14 real         0.08 user         0.05 sys
        0.13 real         0.07 user         0.05 sys
        0.16 real         0.08 user         0.06 sys
        0.15 real         0.08 user         0.05 sys
```

## sources

1. [powerlevel10k](https://github.com/romkatv/powerlevel10k), a prompt that uses a highly efficient [gitstatus](https://github.com/romkatv/gitstatus) to provide fast VCS prompt updates
2. https://stevenvanbael.com/profiling-zsh-startup
3. https://htr3n.github.io/2018/07/faster-zsh/
4. https://carlosbecker.com/posts/speeding-up-zsh/
5. https://medium.com/@dannysmith/little-thing-2-speeding-up-zsh-f1860390f92
6. https://esham.io/2018/02/zsh-profiling
7. https://gist.github.com/ctechols/ca1035271ad134841284
8. https://gist.github.com/Amar1729/294c6e310b191405bf8fceb72e96b399
9. https://github.com/qoomon/zsh-lazyload

----

~ tags : #ricing * #zsh
