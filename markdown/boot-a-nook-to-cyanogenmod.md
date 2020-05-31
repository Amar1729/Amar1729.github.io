# Booting Cyanogenmod on a Nook HD+

*Feb 19 2017*

Full disclosure: this post is meant to serve as a recording of the steps I used for this process. I’ve had SD cards die on me so I’ve had to repeat this process 3 times by now.

Another disclosure: Be careful about performing any of this stuff on your device! Installing custom ROMs or rooting will void your warranty so make sure you read a full tutorial before you start (so you know what you’re getting into) and backup your data safely.

Note that you should NOT unzip the CM or gapps files you find - the cyanobootloader installs these programs from a zip file. The recovery image, however, should be unzipped until its extensions is `.img`.

User Amaces offers a shared Box folder for download of lots of relevant files:
* [general files](https://notredame.app.box.com/s/26a4bygh9vbaw7jjq08xr5evomvaw5ww)
* [ovation-specific](https://notredame.app.box.com/s/26a4bygh9vbaw7jjq08xr5evomvaw5ww/1/3332706778), for Nook HD+ (hummingbird is for the Nook HD)

I used CM10.1 on my Nook HD+ (even though the current version is CM11) because I had slightly better speed using CM10.

Thanks to XDA users `Hashcode` and `verygreen`, who provided writeups and files for rooting the Nook! I used the recovery image from this this XDA thread (which I’ll also include below in case of a broken link), but downloaded CM10 and gapps from their respective download pages. I’ll also link the specific - but outdated - versions I used. On this post, the recovery image is the “initial sdcard image for ovation” in the “for completeness” part of the tutorial. The recovery image is the one part of this process that’s the most difficult, since you have to find a properly-working image for your device. It doesn’t help that a lot of the links turn up dead since the HD+ is an older device at this point. I also keep finding a bunch of broken recovery images: a proper one for the Nook is about 120 MB, but a lot of the ones you may find are only 10MB.

First you’ll have to write the recovery image to your SD card. This can be done with Windisk32Imager if you’re on Windows (yeah you’ll need some bloatware) or with the simple `dd` command if you’re on Mac or Linux. On a \*nix system, you’ll have to unmount the disk first , and then `dd` the image like this:

```
# the r specifies "raw" - not required but helps speed up the process
dd bs=4m if=recovery.img of=/dev/rdisk3
```

I used `adb` (the Android Debug Bridge) to push the cm10 and gapps image to my Nook, but I think (?) you can also load them onto the SD card after creating the recovery image. Then, you shut the Nook off, insert the SD card, and boot it up. You should be presented with the Cyanobootloader trying to boot into the recovery SD.

Once the Nook boots into recovery, you’ll want to make a backup of your system. When I tried it first, the backup and restore process kept failing for me, so I just went ahead with the install anyway. You can go to install from zip and navigate to the location where you saved the cm and gapps zip files. For me, I chose install from /emmc and navigated to the Downloads folder of the original Nook OS; you can also choose install from /sdcard if you loaded the files there. I initially tried install zip from sideload but for some reason adb never managed to establish a proper sideload session, so I couldn’t do that either. Once you’ve installed the cm image, go ahead and install gapps and reboot your Nook!

Hopefully, when cyanoboot intercepts the regular boot order, it should now inform you that you are "booting Cyanogenmod from SD". The first boot will take a little while, but once you’re in you can just connect to WiFi and sign in to your Cyanogenmod and/or Google accounts (if you want). Once you’re done with that, enjoy your rooted Android tablet!

----

~ tags : #android
