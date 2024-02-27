import os
import logging
from multiprocessing import Pool, Lock, current_process
import numpy as np
from tinytag import TinyTag
from fingerprint import fingerprint_file
from storage import store_song,get_matches, get_info_for_song_id

KNOWN_EXTENSIONS = ["mp3", "wav", "flac", "m4a"]

def get_song_info(filename):
    """Gets the ID3 tags for a file. Returns None for tuple values that don't exist.

    :param filename: Path to the file with tags to read
    :returns: (artist, album, title)
    :rtype: tuple(str/None, str/None, str/None)
    """
    tag = TinyTag.get(filename)
    artist = tag.artist if tag.albumartist is None else tag.albumartist
    return (artist, tag.album, tag.title)

def register_song(filename):
    """Register a single song.

    Checks if the song is already registered based on path provided and ignores
    those that are already registered.

    :param filename: Path to the file to register"""
    # if song_in_db(filename):
    #     return
    hashes = fingerprint_file(filename)
    song_info = get_song_info(filename)
    try:
        logging.info(f"{current_process().name} waiting to write {filename}")
        with lock:
            logging.info(f"{current_process().name} writing {filename}")
            store_song(hashes, song_info)
            logging.info(f"{current_process().name} wrote {filename}")
    except NameError:
        logging.info(f"Single-threaded write of {filename}")
        # running single-threaded, no lock needed
        store_song(hashes, song_info)
        return hashes,song_info
    
def score_match(offsets):
    """Score a matched song.

    Calculates a histogram of the deltas between the time offsets of the hashes from the
    recorded sample and the time offsets of the hashes matched in the database for a song.
    The function then returns the size of the largest bin in this histogram as a score.

    :param offsets: List of offset pairs for matching hashes
    :returns: The highest peak in a histogram of time deltas
    :rtype: int
    """
    # Use bins spaced 0.5 seconds apart
    binwidth = 0.5
    tks = list(map(lambda x: x[0] - x[1], offsets))
    hist, _ = np.histogram(tks,
                           bins=np.arange(int(min(tks)),
                                          int(max(tks)) + binwidth + 1,
                                          binwidth))
    return np.max(hist)



def best_match(matches):
    """For a dictionary of song_id: offsets, returns the best song_id.

    Scores each song in the matches dictionary and then returns the song_id with the best score.

    :param matches: Dictionary of song_id to list of offset pairs (db_offset, sample_offset)
       as returned by :func:`~abracadabra.Storage.storage.get_matches`.
    :returns: song_id with the best score.
    :rtype: str
    """
    matched_song = None
    best_score = 0
    for song_id, offsets in matches.items():
        if len(offsets) < best_score:
            # can't be best score, avoid expensive histogram
            continue
        score = score_match(offsets)
        if score > best_score:
            best_score = score
            matched_song = song_id
    return matched_song


def recognise_song(filename):
    """Recognises a pre-recorded sample.

    Recognises the sample stored at the path ``filename``. The sample can be in any of the
    formats in :data:`recognise.KNOWN_FORMATS`.

    :param filename: Path of file to be recognised.
    :returns: :func:`~abracadabra.recognise.get_song_info` result for matched song or None.
    :rtype: tuple(str, str, str)
    """
    hashes = fingerprint_file(filename)
    matches = get_matches(hashes)
    matched_song = best_match(matches)
    info = get_info_for_song_id(matched_song)
    if info is not None:
        return info
    return matched_song

if __name__ == "__main__":
    path = "C:\\Users\\DELL\\Desktop\\shazam\\recorded_audio3.wav"
    info = recognise_song(path)
    print("matched info:",info)