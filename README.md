# dime - say it to me


## how to run
```
root@voyage:~/share# ./runner.sh
```


## demo system


### hardware
pc engines alix3d3
 * http://www.pcengines.ch/alix3d3.htm

## os
voyage linux

additional packages (and dependencies):
 * python3
 * python-pip3
 * festival
 * festival-czech
 * festlex-cmu
 * festlex-oald
 * festlex-poslex
 * festvox-czech-ph
 * festvox-don
 * festvox-kallpc16k
 * festvox-kdlpc16k
 * festvox-rablpc16k
 * alsa-utils

### alsa mixer configuration
to support multiple audio sources, enable the alse mixer plugin.
```
root@voyage:~/share# cat ~/.asoundrc

pcm.!default {
    type plug
    slave.pcm "dmixer"
}
pcm.dsp0 {
    type plug
    slave.pcm "dmixer"
}
pcm.dmixer {
    type dmix
    ipc_key 1024
    slave {
        pcm "hw:0,0"
        period_time 0
        period_size 1024
        buffer_size 8192
        #periods 128
        rate 44100
     }
     bindings {
        0 0
        1 1
     }
}
ctl.mixer0 {
    type hw
    card 0
}

```

## synthesizer tested
### festival
 * https://wiki.archlinux.org/index.php/Festival

## links


On Thu, Apr 14, 2016 at 9:23 AM, Samuel Casa <samuelcasa9@gmail.com> wrote:

    http://stackoverflow.com/questions/1614059/how-to-make-python-speak



    On Thu, Apr 14, 2016 at 8:48 AM, Samuel Casa <samuel.casa@neratec.com> wrote:

        read this

        http://askubuntu.com/questions/21811/how-can-i-install-and-use-text-to-speech-software

        http://askubuntu.com/questions/53896/natural-sounding-text-to-speech

           freetts

        festival
        Review: Text to speech on linux
         libttspico-data
        Review: Text to speech on linux

        https://www.youtube.com/watch?v=cziGpZTKZko
        HakTip - Free Text to Speech with Linux
        HakTip - Free Text to Speech with Linux
        https://www.youtube.com/watch?v=h2VbcoCw_oM

        festival

        http://xmpppy.sourceforge.net/examples/bot.py

