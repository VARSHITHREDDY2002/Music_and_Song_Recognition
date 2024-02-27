import os
import wave
import threading
import pyaudio
import numpy as np

CHUNK = 1024
"""Number of frames to buffer before writing."""
FORMAT = pyaudio.paInt16
"""The data type used to record audio. See ``pyaudio`` for constants."""
CHANNELS = 1
"""The number of channels to record."""
RATE = 44100
"""The sample rate."""
RECORD_SECONDS = 10
"""Number of seconds to record."""
SAVE_DIRECTORY = "test/"
"""Directory used to save audio when using :func:`gen_many_tests`."""


def record_audio(filename=None):
    """ Record 10 seconds of audio and optionally save it to a file

    :param filename: The path to save the audio (optional).
    :returns: The audio stream with parameters defined in this module.
    """
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    write_frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(np.frombuffer(data, dtype=np.int16))
        if filename is not None:
            write_frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    if filename is not None:
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    return np.hstack(frames)

def play_audio(filename):
    """ Play audio from a WAV file

    :param filename: The path to the WAV file to play.
    """
    os.system("start " + filename)  # For Windows, opens the default player for WAV files
    # For Linux or MacOS, you may need to use a different command or player

if __name__ == "__main__":
    # Set the filename to save the recorded audio
    current_directory = os.getcwd()
    filename = os.path.join(current_directory, "recorded_audio3.wav")
    
    print(filename)
    
    print("Recording audio for {} seconds...".format(RECORD_SECONDS))
    recorded_audio = record_audio(filename)

    print("Audio recording complete.")
    print("Recorded audio saved to:", filename)

    # Play the recorded audio
    play_audio(filename)
