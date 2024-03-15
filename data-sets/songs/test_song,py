import os
from tinytag import TinyTag


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

def get_files_info(folder_path):
    """
    Gets song info for all files in a folder.

    :param folder_path: Path to the folder containing audio files
    :return: List of tuples containing (filename, artist, album, title)
    """
    files_info = []
    for filename in os.listdir(folder_path):
        if filename.endswith(tuple(KNOWN_EXTENSIONS)):
            file_path = os.path.join(folder_path, filename)
            artist, album, title = get_song_info(file_path)
            print("File:", filename, ", Artist:", artist, ", Album:", album, ", Title:", title)
            files_info.append((filename, artist, album, title))
    return files_info

if __name__ == "__main__":
    folder_path = "/home/rohithreddy/Desktop/songs"
    files_info = get_files_info(folder_path)
    # for filename, artist, album, title in files_info:
    #     print(f"File: {filename}, Artist: {artist}, Album: {album}, Title: {title}")