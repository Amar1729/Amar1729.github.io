# more password cracking

*Oct 30 2017*

Another example on using `john` and `hashcat` to crack passwords from a CTF challenge.

[previous pw cracking post](./password-cracking-with-hashcat-1.html)

In this CTF challenge, we're given the following `shadow` file:

```
Ade:706cb8c2abdbf0adbebfbf571c1ae9e1
Christian:7e389b3dd4161c85ffc1f399044fa6a1
Elyse:457bfc6d77b0e262ed8e03e4a545564e
Jenny:44c1d1671a78ab3ff7dd13c3268086d4
Kristy:7f6021304d7b3e6f10a4e86ad0c1ce44
```

and we're told that each of these people are interested in flights. I'm going to assume that these passwords look like flight numbers: `[A-Z][A-Z][A-Z][0-9]*`.

Since we know (or are we guessing?) what the passwords look like, we'll be using a mask attack to break these hashes. Mask attacks are like brute-force attacks, but they let you narrow down the problem space by focusing on certain characters or character sets.

## hashcat

As always, use `hashcat --help` to see what the tool offers you. In particular, take a look at the `Charsets` section near the bottom of the help text.

We're going to remove the names from our `shadow` file, giving us a resultant file `hc-shadow`:
```
706cb8c2abdbf0adbebfbf571c1ae9e1
7e389b3dd4161c85ffc1f399044fa6a1
457bfc6d77b0e262ed8e03e4a545564e
44c1d1671a78ab3ff7dd13c3268086d4
7f6021304d7b3e6f10a4e86ad0c1ce44
```

With hashcat, we can use conduct a mask attack like this:
```
# -m 0 specifies --hash-type "MD5" (not always necessary)
# -a 3 specifies --attack-mode "Brute-force"
# ?u is the signifier for any uppercase digit
$ hashcat -m 0 -a 3 hc-shadow '?u?u?u'
```

If you give hashcat this mask, it'll assume all your passwords look like `[A-Z][A-Z][A-Z]` and only hash those possibilites. However, we need some numbers at the end of our passwords too:
```
$ hashcat -a 3 hc-shadow '?u?u?u?d'

/*
    snip
*/

Approaching final keyspace - workload adjusted.

44c1d1671a78ab3ff7dd13c3268086d4:MAS2
```

Look at that! We got lucky, and one of our passwords only had one digit at the end. We don't know about the rest though, so let's investigate hashcat's `--increment` flag.

Using a mask like `?d?d?d?d` would tell hashcat that all our passwords are exactly four digits. If we also pass `--increment`, hashcat would try incrementally adding to its mask starting from one, meaning it would try all masks like this:

```
?d
?d?d
?d?d?d
?d?d?d?d
```

We'd like to try that for our passwords, but you can't combine `--increment` with a mask that has different character classes in it. There are a couple ways around this, like writing a few charsets into your own small `masks.hcmask` file, but the quickest I'm comfortable with using the command line is defining your own character set and incrementing on that.

Hashcat allows you to define custom charsets using numbers as flags: `-1 '<charset>'` defines the first custom set, `-2 <charset>` defines the second, and you can have up to four in a single session.

We'll define one like this: `-1 '?u?d'` - a charset made up of only uppercase letters and digets - and then run a slightly larger incremental mask attack:

```
hashcat -1 '?u?d' -a 3 hc-shadow '?1?1?1?1?1?1' --increment

/*
    snip
*/

Approaching final keyspace - workload adjusted.

7e389b3dd4161c85ffc1f399044fa6a1:SCX401
7f6021304d7b3e6f10a4e86ad0c1ce44:KLM887
457bfc6d77b0e262ed8e03e4a545564e:AAL126
706cb8c2abdbf0adbebfbf571c1ae9e1:SWG427
```

And just like that, we've cracked the rest of the passwords. You can see all of them with `hashcat hc-shadow --show`.

## john the ripper

With `john` our approach is similar (make sure to use the more powerful community edition, `john-jumbo`).

I initially used the following command:
```
$ john shadow --fork=4 --format=Raw-MD5 --incremental=UpperNum     

Using default input encoding: UTF-8
Loaded 5 password hashes with no different salts (Raw-MD5 [MD5 128/128 SSE4.1 4x5])
Node numbers 1-4 of 4 (fork)
Press 'q' or Ctrl-C to abort, almost any other key for status
MAS2             (Jenny)
AAL126           (Elyse)
KLM887           (Kristy)
SWG427           (Ade)

^C
```

For some reason, `john` really took a while finding the fifth hash for me, so I just canceled it and ran it by specifying the mask manually:

```
$ john --pot=john.pot shadow --fork=4 --format=Raw-MD5 -mask='?u?u?u?d?d?d'

Using default input encoding: UTF-8
Loaded 5 password hashes with no different salts (Raw-MD5 [MD5 128/128 SSE4.1 4x5])
Remaining 1 password hash
Node numbers 1-4 of 4 (fork)
Press 'q' or Ctrl-C to abort, almost any other key for status
SCX401           (Christian)
1 1g 0:00:00:00 DONE (2020-05-29 22:37) 33.33g/s 10517Kp/s 10517Kc/s 10517KC/s ISX401..MJX401
Waiting for 3 children to terminate
4 0g 0:00:00:00 DONE (2020-05-29 22:37) 0g/s 13315Kp/s 13315Kc/s 13315KC/s XWQ777..QQQ777
2 0g 0:00:00:00 DONE (2020-05-29 22:37) 0g/s 12205Kp/s 12205Kc/s 12205KC/s XWQ779..QQQ779
3 0g 0:00:00:00 DONE (2020-05-29 22:37) 0g/s 11563Kp/s 11563Kc/s 11563KC/s XWQ794..QQQ794
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed
```

### helpful resources

* https://www.4armed.com/blog/perform-mask-attack-hashcat/
* https://countuponsecurity.files.wordpress.com/2016/09/jtr-cheat-sheet.pdf

----

~ tags : #ctf * #cracking
