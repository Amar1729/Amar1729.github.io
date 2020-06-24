# Cleaning up `pip`

*May 05 2020*


The `python` programming language has been around since 1989 - much longer ago than you would think, given how popular it is as an easy-to-learn language and how well it's transitioned into the "modern" era of computing. There are a lot of things it does well - decent standard library, easy syntax for beginners, good abstractions for complex concepts, ease of use as a scripting tool - but it certainly has its problems too.


One of the more serious issues with _using_ the language is the problems it has with packaging. Package management is by no means easy, and the process for packaging and installing python code has undergone many changes in the last three decades. Installation of standalone CLI tools or project dependencies has nearly always been done with `pip`. However, many newcomers run into a preponderance of python tutorials suggesting to just run `pip install flask` - or, even worse, `sudo pip install virtualenv`.

Aside: when installing dependencies for a project, you should use `virtualenv` (or a newer solutions like [`poetry`](https://python-poetry.org/)). This article focuses more on the issues with python CLI tools installed via pip.

## The Problem

On many Linux systems, `python` comes pre-installed (as of 2019, most versions of Ubuntu and CentOS still packaged `python2`, but that's been switched to `python3` with the sunset of Python 2 in late 2019). On certain systems, the package manager itself actually **depends** on python and certain python dependencies (looking at you, `yum`). This means that you can run `pip list` and see what packages the **system** already has installed. It also means if you ever try to upgrade out-of-date modules with `pip`, you might break your package manager.

An initial solution to this problem is to install tools into your user profile, with `pip3 install --user virtualenv`. This will install binaries into a user-specific directory without `sudo`, ideally keeping your tools separate from system tools. However, after accruing a lot of installed tools, your pip-installed packages are going to look a lot like this:

```
$ pip list

appdirs==1.4.4
astroid==2.4.2
atomicwrites==1.4.0
attrs==19.3.0
beets==1.4.9
black==19.10b0
black-macchiato==1.3.0
CacheControl==0.12.6
cachy==0.3.0
certifi==2020.4.5.2
chardet==3.0.4
cleo==0.7.6
click==7.1.2

# snipped for brevity

$ pip list | wc -l

85
```

Great. Thanks pip. I don't know which of those packages are dependencies or explicitly installed, and I don't even know which of those modules is installed by the system or installed in my home directory.

Using a tool such as [`pipdeptree`](https://pypi.org/project/pipdeptree/) mitigates the issue somewhat:

```
$ pipdeptree

Warning!!! Possibly conflicting dependencies found:
* poetry==1.0.9
 - importlib-metadata [required: >=1.1.3,<1.2.0, installed: 1.6.1]
------------------------------------------------------------------------
astroid==2.4.2
  - lazy-object-proxy [required: ==1.4.*, installed: 1.4.3]
  - six [required: ~=1.12, installed: 1.15.0]
  - typed-ast [required: >=1.4.0,<1.5, installed: 1.4.1]
  - wrapt [required: ~=1.11, installed: 1.12.1]
atomicwrites==1.4.0
beets==1.4.9
  - jellyfish [required: Any, installed: 0.8.2]
  - munkres [required: >=1.0.0, installed: 1.1.2]
  - musicbrainzngs [required: >=0.4, installed: 0.7.1]
  - mutagen [required: >=1.33, installed: 1.44.0]
  - pyyaml [required: Any, installed: 5.3.1]
  - six [required: >=1.9, installed: 1.15.0]
  - unidecode [required: Any, installed: 1.1.1]
black-macchiato==1.3.0
  - black [required: Any, installed: 19.10b0]
    - appdirs [required: Any, installed: 1.4.4]
    - attrs [required: >=18.1.0, installed: 19.3.0]
    - click [required: >=6.5, installed: 7.1.2]
    - pathspec [required: >=0.6,<1, installed: 0.8.0]
    - regex [required: Any, installed: 2020.6.8]
    - toml [required: >=0.9.4, installed: 0.10.1]
    - typed-ast [required: >=1.4.0, installed: 1.4.1]
coverage==5.1
flake8==3.8.3
  - importlib-metadata [required: Any, installed: 1.6.1]
    - zipp [required: >=0.5, installed: 3.1.0]
  - mccabe [required: >=0.6.0,<0.7.0, installed: 0.6.1]
  - pycodestyle [required: >=2.6.0a1,<2.7.0, installed: 2.6.0]
  - pyflakes [required: >=2.2.0,<2.3.0, installed: 2.2.0]
isort==4.3.21
lockfile==0.12.2
mypy==0.780
  - mypy-extensions [required: >=0.4.3,<0.5.0, installed: 0.4.3]
  - typed-ast [required: >=1.4.0,<1.5.0, installed: 1.4.1]
  - typing-extensions [required: >=3.7.4, installed: 3.7.4.2]

# snipped
```

Well, now I can somewhat see what depends on what, I can get a sense of what I explicitly installed ... and `pipdeptree` helpfully informs me there is a possible conflict of dependency versions for some of the modules I have installed.

## The Solution

Over time, some of the python tools you've installed may become outdated. They may even stay up-to-date but have a locked dependency requirement that conflicts with a different tool you have on your system. Pip really doesn't like when this is the case, and you run the risk of one tool or another not working because it has the wrong dependency installed.

Enter [pipx](https://github.com/pipxproject/pipx) - another "package installer for python", but one that installs tools into their own isolated virtual environments. A tool like this will allow you never to have to deal with version conflicts again, do away entirely with the risk of breaking system tools after an upgrade, and lets you never to have to hack together a "pip upgrade all" script[[1]](#sources).

### Untangling your Uninstalls

Unfortunately, pip doesn't really make it easy to uninstall things safely. You can run `pip uninstall six`, and pip won't ever complain that you are uninstalling a module on which 10 others depend. You could try to walk through the output of `pipdeptree` which is irritatingly manual and tedious, but I cleaned out my depencency tree with a fork of [pip-autoremove](https://github.com/invl/pip-autoremove/issues/27#issuecomment-612529876)[[2]](#sources).

```
$ pip-autoremove black-macchiato

importlib-metadata 1.6.1 is installed but importlib-metadata<1.2.0,>=1.1.3; python_version < "3.8" is required
Redoing requirement with just package name...
black-macchiato 1.3.0 (/private/tmp/venv/lib/python3.7/site-packages)
    black 19.10b0 (/private/tmp/venv/lib/python3.7/site-packages)
        pathspec 0.8.0 (/private/tmp/venv/lib/python3.7/site-packages)
        regex 2020.6.8 (/private/tmp/venv/lib/python3.7/site-packages)
Uninstall (y/N)? y
Found existing installation: regex 2020.6.8
Uninstalling regex-2020.6.8:
  Successfully uninstalled regex-2020.6.8
Found existing installation: pathspec 0.8.0
Uninstalling pathspec-0.8.0:
  Successfully uninstalled pathspec-0.8.0
Found existing installation: black 19.10b0
Uninstalling black-19.10b0:
  Successfully uninstalled black-19.10b0
Found existing installation: black-macchiato 1.3.0
Uninstalling black-macchiato-1.3.0:
  Successfully uninstalled black-macchiato-1.3.0
```

You can do this with all of your old pip-installed tools, resulting in a much cleaner tree (with no version conflicts!):

```
$ pipdeptree

-BB==0.1
astroid==2.4.0
  - lazy-object-proxy [required: ==1.4.*, installed: 1.4.3]
  - six [required: ~=1.12, installed: 1.14.0]
  - typed-ast [required: >=1.4.0,<1.5, installed: 1.4.1]
  - wrapt [required: ~=1.11, installed: 1.12.1]
atomicwrites==1.4.0
backports.shutil-get-terminal-size==1.0.0
neovim-remote==2.4.0
  - psutil [required: Any, installed: 5.7.0]
  - pynvim [required: Any, installed: 0.4.1]
    - greenlet [required: Any, installed: 0.4.13]
    - msgpack [required: >=0.5.0, installed: 1.0.0]
  - setuptools [required: Any, installed: 46.0.0]
pip-autoremove==0.9.1
pipdeptree==0.13.2
  - pip [required: >=6.0.0, installed: 20.0.2]
pipx==0.15.1.3
  - argcomplete [required: >=1.9.4,<2.0, installed: 1.11.1]
    - importlib-metadata [required: >=0.23,<2, installed: 1.6.0]
      - zipp [required: >=0.5, installed: 3.1.0]
  - userpath [required: Any, installed: 1.4.0]
    - click [required: Any, installed: 7.1.2]
wheel==0.34.2

$ pip3 list | wc -l

24
```

### Isolate your Installs

After cleaning up pip's packages, `pipx install` can be used to install everything you need into its own isolated environment. Once you've installed the tools you used to have, you can deal with them much more easily using `pipx uninstall` or `pipx upgrade-all`.

```
$ pipx list

venvs are in /Users/Amar/.local/pipx/venvs
apps are exposed on your $PATH at /Users/Amar/.local/bin
   package beets 1.4.9, Python 3.7.7
    - beet
   package black 19.10b0, Python 3.7.7
    - black
    - blackd
   package black-macchiato 1.3.0, Python 3.7.7
    - black-macchiato
   package flake8 3.8.3, Python 3.7.7
    - flake8
   package ipython 7.15.0, Python 3.7.7
    - iptest
    - iptest3
    - ipython
    - ipython3
   package isort 4.3.21, Python 3.7.7
    - isort
   package mypy 0.780, Python 3.7.7
    - dmypy
    - mypy
    - mypyc
    - stubgen
    - stubtest
   package poetry 1.0.9, Python 3.7.7
    - poetry
   package pytest-cov 2.10.0, Python 3.7.7
    - coverage
    - coverage-3.7
    - coverage3
    - py.test
    - pytest
   package pywal 3.3.1, Python 3.7.7
    - wal
   package tox 3.15.2, Python 3.7.7
    - tox
    - tox-quickstart
   package virtualenv 20.0.23, Python 3.7.7
    - virtualenv
```

From now on, you never have to deal with pip's dependency conflicts or tedious uninstallation.

## sources

1. An old suggested way to upgrade all of your pip-installed modules went something like this: `pip3 list --user --outdated | cut -f1 -d '=' | xargs -n 1 pip3 install --user -U`. Too bad you can't just `pip3 --upgrade-all`.

2. Package managers should hopefully let you uninstall a tree of dependencies without uninstalling packages that others depend on. On Ubuntu, you can `apt remove --autoremove`; on Arch, you can remove a package and dependencies with `pacman -Rcn`; with Mac's Homebrew, check out [homebrew-rmtree](https://github.com/beeftornado/homebrew-rmtree).

----

~ tags : #python
