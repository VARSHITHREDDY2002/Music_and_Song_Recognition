import uuid
import sqlite3
from collections import defaultdict
from contextlib import contextmanager
from values import DB_PATH


# NOTE:
# when a curser is need intead of creating it we just use this function 
# So we can manage 
@contextmanager
def get_cursor():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        yield conn, conn.cursor()
    finally:
        conn.close()


# NOTE:
# Creating tables for the database
def setup_db():
    with get_cursor() as (conn, c):
        c.execute("CREATE TABLE IF NOT EXISTS hash (hash int, offset real, song_id text)")
        c.execute("CREATE TABLE IF NOT EXISTS song_info (artist text, album text, title text, song_id text)")
        # dramatically speed up recognition
        c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON hash (hash)")
        # faster write mode that enables greater concurrency
        # https://sqlite.org/wal.html
        c.execute("PRAGMA journal_mode=WAL")
        # reduce load at a checkpoint and reduce chance of a timeout
        c.execute("PRAGMA wal_autocheckpoint=300")

# NOTE:
# store all the hases along with their song ID
def store_song(hashes, song_info):
    if len(hashes) < 1:
        # TODO: After experiments have run, change this to raise error
        # Probably should re-run the peaks finding with higher efficiency
        # or maybe widen the target zone
        return
    with get_cursor() as (conn, c):
        c.executemany("INSERT INTO hash VALUES (?, ?, ?)", hashes)
        insert_info = [i if i is not None else "Unknown" for i in song_info]
        c.execute("INSERT INTO song_info VALUES (?, ?, ?, ?)", (*insert_info, hashes[0][2]))
        conn.commit()


# NOTE:
# Takes in hashes and returns a dict whoese key is matched song_id and value is a list of tuples of form sample_time, offset
def get_matches(hashes, threshold=5):
    h_dict = {}
    for h, t, _ in hashes:
        h_dict[h] = t
    in_values = f"({','.join([str(h[0]) for h in hashes])})"
    with get_cursor() as (conn, c):
        c.execute(f"SELECT hash, offset, song_id FROM hash WHERE hash IN {in_values}")
        results = c.fetchall()
    result_dict = defaultdict(list)
    for r in results:
        result_dict[r[2]].append((r[1], h_dict[r[0]]))
    return result_dict


# NOTE: Lookup song information for a given ID.
def get_info_for_song_id(song_id):
    with get_cursor() as (conn, c):
        c.execute("SELECT artist, album, title FROM song_info WHERE song_id = ?", (song_id,))
        return c.fetchone()


if __name__ == "__main__":
    setup_db()
    print("completed")

