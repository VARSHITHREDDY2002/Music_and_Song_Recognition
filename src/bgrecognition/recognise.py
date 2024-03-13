import logging
from storage import get_cursor
import uuid
from multiprocessing import Pool, Lock, current_process
import numpy as np
from tinytag import TinyTag
from fingerprint import fingerprint_file
from storage import store_song,get_matches, get_info_for_song_id

KNOWN_EXTENSIONS = ["mp3", "wav", "flac", "m4a"]

# NOTE: Uses Tinytag to get artist, albumn, title info
def get_song_info(filename):
    tag = TinyTag.get(filename)
    artist = tag.artist if tag.albumartist is None else tag.albumartist
    return (artist, tag.album, tag.title)

# NOTE: Registers the song into the database if its in the database then we do nothing
def register_song(filename):
    if song_in_db(filename):
        return
    hashes = fingerprint_file(filename)
    song_info = get_song_info(filename)
    store_song(hashes, song_info)
    return hashes,song_info

# NOTE: it uses the offsets and computes the starttime - sample time and then put them into bins and the bin containing the largest number of items is the score
def score_match(offsets):
    # Use bins spaced 0.5 seconds apart
    binwidth = 0.5
    tks = list(map(lambda x: x[0] - x[1], offsets))

    hist, _ = np.histogram(tks,
                           bins=np.arange(int(min(tks)) -1,
                                          int(max(tks)) + binwidth + 1,
                                          binwidth))
    return np.max(hist)


# NOTE:
# out of all the songs it returns the best match
def best_match(matches):
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

# NOTE: given a filename it will recognise the song in the database
def recognise_song(filename):
    hashes = fingerprint_file(filename)
    matches = get_matches(hashes)
    matched_song = best_match(matches)
    info = get_info_for_song_id(matched_song)
    if info is not None:
        return info
    return matched_song


#NOTE: Check whether a path has already been registered.
def song_in_db(filename):
    with get_cursor() as (conn, c):
        song_id = str(uuid.uuid5(uuid.NAMESPACE_OID, filename).int)
        c.execute("SELECT * FROM song_info WHERE song_id=?", (song_id,))
        return c.fetchone() is not None

if __name__ == "__main__":
    path = "../../data-sets/songs/songsrecorded_audio3.wav"
    info = recognise_song(path)
    print("matched info:",info)
