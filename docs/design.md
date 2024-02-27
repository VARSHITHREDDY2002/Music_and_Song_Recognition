
# Design

we have decided to devolop a music retrival system that would work on a personal music library i.e can index upto 1k - 2k songs.

It involves two Neural Networks

1. Hum/MIDI to UDS (Network 1)
2. Orginal Song to UDS (N2)

### N1

This nueral network takes in input of two succesive frames (i.e a small time sample of audio) of audio-spectrogram it outputs a decsriptor for that instance. Then we do this for the entire song to get a UDS annotation of that Hum/MIDI.

### N2

This nueral network takes in the orginal song as the input same as N1, we split the song into small time frames and generates an UDS annotation of that song.

To train this nueral network we have taken the MIDI-version of the orginal song and generated a UDS annotation using N1 and used it as the expected output of N2 for the song.

## IDEA 

we would to emulate the pitch tracker used in querey by Humming. with N1

And as the pitch tracker described in querey by Humming doesn't work on a complicted audio signal we would like N2 to emulate that..

## Terms

Fingerprint : .....

UDS:

Component1 Threshold :

## Experminents

**N1** 

classfaction nureal network with just current and previous frame

current and a set of previous frames

**N2**

classfaction nureal network with just current and previous frame

current and a set of previous frames
DNN-LSTM

we also want to experiment with UDS (i.e using 3 levels or  5 or 7)

## Search

Hashing :

Fuzzy Search :

## Evaluation Metrics

Mean Reciprocal rank (describe)

1,3,5,10 hit ratio's (describe)
