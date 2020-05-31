# password cracking

*Oct 30 2017*

I've taken part in a few CTF (Capture the Flag) challenges, and they like to include various password-cracking challenges.

[`hashcat`](https://hashcat.net/hashcat/) and [john the ripper](https://github.com/magnumripper/JohnTheRipper) are both extremely powerful password cracking tools, but it's tough to find sufficient documentataion for either of them.

Before getting into the usage of these tools, it is important to understand one thing: when cracking larger lists of (or more complex) passwords, it is important to use **wordlists** that you think address the problem well. Alongside that, the rules or masks provided by john/hashcat help with mutating the wordlists in efficient ways to guess and find symbol-ridden passwords.

Another minor thing to note is that both tools try to store progress in a "potfile" - a textfile with previously-cracked hashes and their values - to prevent doing extra work. These potfiles are in `~/.hashcat/` or `~/.john/`, and can be deleted if you want to force the tool to recalculate hashes you've cracked already.

## john the ripper

I'll mention john the ripper here, but I've found it to be slightly less powerful than hashcat in general. However, it can be tougher to find good examples using hashcat. More info on `john` may come around in another post.

When using `john`, it is highly recommended you use the community edition with extra patches, normally referred to in package managers as `john-jumbo`.

## hashcat

To install on macOS, you can use `brew install hashcat`.

### hashcat configuration

Hashcat comes bundled with a bunch of extra stuff like rules, charsets, and masks; you want to make sure these are easily reachable for you to call from the command line. Depending on you package manager, these paths may change, but with macOS Homebrew you can determine the prefix Homebrew uses with `brew --prefix`.

You should symlink hashcat's provided resources into `~/.hashcat` so you can easily reference them from the command line:

```
~ $ brew --prefix
/usr/local

~ $ ln -sfv /usr/local/opt/hashcat/share/doc/hashcat/rules ~/.hashcat/rules
.hashcat/rules -> /usr/local/opt/hashcat/share/doc/hashcat/rules

~ $ ln -sfv /usr/local/opt/hashcat/share/doc/hashcat/masks ~/.hashcat/masks
.hashcat/masks -> /usr/local/opt/hashcat/share/doc/hashcat/masks

~ $ ln -sfv /usr/local/opt/hashcat/share/doc/hashcat/charsets ~/.hashcat/charsets
.hashcat/charsets -> /usr/local/opt/hashcat/share/doc/hashcat/charsets
```

### Usage

Once you have `hashcat` set up like this, it's time to crack some passwords.

A typical password dump for a CTF might look like this:

`shadow`:
```
Ade:b632c55a33530d1433e29ffc09ba1151
Christian:19daa434fdd91a9e492fbc10e9103d83
Elyse:4f266e1da75659f61cd8ac8b8901fa13
Jenny:40e2e28b099afa39c97619bd6dbaa44d
Kristy:f45e8bd2abcd1a3a532e5caa26794a0f
```

This particular CTF challenge also gave hint that these people might be interested in Silicon Valley, so we copied the names of every company on https://yclist.com/, giving us a wordlist of 962 lines at the time.

To break these with hashcat, you want to get rid of the names so you have a file like this:

`hc-shadow`:
```
b632c55a33530d1433e29ffc09ba1151
19daa434fdd91a9e492fbc10e9103d83
4f266e1da75659f61cd8ac8b8901fa13
40e2e28b099afa39c97619bd6dbaa44d
f45e8bd2abcd1a3a532e5caa26794a0f
```

Then, a first attempt with hashcat is simple:

```
# try to break the password hashes in 'hc-shadow' using the wordlist in 'yclist'
$ hashcat hc-shadow yclist

/*
  lots of hashcat output
*/

Approaching final keyspace - workload adjusted.

4f266e1da75659f61cd8ac8b8901fa13:Justin.tv
b632c55a33530d1433e29ffc09ba1151:Reddit
```

So, `hashcat` manages to find two of our hashes without any more help than a good wordlist. To find the others, we're going to have to play around with some of the rules hashcat gives you for modifying its wordlists:

```
# use the best64 rule to mutate the wordlist
$ hashcat hc-shadow yclist -r ~/.hashcat/rules/best64.rule

/*
  snip
*/

Approaching final keyspace - workload adjusted.

f45e8bd2abcd1a3a532e5caa26794a0f:Cr0c0d0c
```

We managed to crack one more password! Now let's try a slightly more intense ruleset, dive:

```
$ hashcat hc-shadow yclist -r ~/.hashcat/rules/dive.rule

/*
  snip
*/

Approaching final keyspace - workload adjusted.

40e2e28b099afa39c97619bd6dbaa44d:Omnisio917
19daa434fdd91a9e492fbc10e9103d83:Docker591
```

Great! We've found the last two passwords we needed!

After you're done, you can always use `--show` to see what's been done:

```
$ hashcat --show hc-shadow

b632c55a33530d1433e29ffc09ba1151:Reddit
40e2e28b099afa39c97619bd6dbaa44d:Omnisio917
f45e8bd2abcd1a3a532e5caa26794a0f:Cr0c0d0c
19daa434fdd91a9e492fbc10e9103d83:Docker591
4f266e1da75659f61cd8ac8b8901fa13:Justin.tv
```

----

~ tags : #ctf * #cracking
