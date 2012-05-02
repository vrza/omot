'''
Created on May 1, 2012

@author: random
'''
import os
import datetime

def infer_covers_dir(relative_file_path):
    r"""
    From relative file path returned by the mpd, infer the 
    directory we should search for album covers
    (usually, but not always, the same directory as the file)
        
    >>> from omot.mytools import infer_covers_dir
    >>> infer_covers_dir('Artists/d/Donald Byrd/1960 - At the Half Note Cafe - 2CD/CD1/105 - Cecile.flac')
    'Artists/d/Donald Byrd/1960 - At the Half Note Cafe - 2CD'
    >>> infer_covers_dir("Artists/d/Donald Byrd/1961 - Free Form/somefile.flac")
    'Artists/d/Donald Byrd/1961 - Free Form'
    >>> infer_covers_dir("Artists/d/Donald Byrd/discography/1961 - Free Form/somefile.flac")
    'Artists/d/Donald Byrd/discography/1961 - Free Form'
    >>> infer_covers_dir("Artists/d/Donald Byrd/discography/1961 Free Form/a/b/somefile.flac")
    'Artists/d/Donald Byrd/discography/1961 Free Form'
    >>> infer_covers_dir("Artists/d/Donald Byrd/discography/Donald Byrd & Kenny Burrell/1956 All Night Long/01.flac")
    'Artists/d/Donald Byrd/discography/Donald Byrd & Kenny Burrell/1956 All Night Long'
    >>> infer_covers_dir("Artists/b/Beatles/2009 Remasters Box Set/1968 The Beatles Disc 1 (2009 Stereo Remaster) [FLAC]/16 - I Will.flac")
    'Artists/b/Beatles/2009 Remasters Box Set/1968 The Beatles Disc 1 (2009 Stereo Remaster) [FLAC]'
    """
    
    assert relative_file_path

    path = relative_file_path.split("/")
    # usual case: parent directory
    pathdepth = len(path) - 1

    # hack for my album collection, where directory layout is
    # Artists/a/Artist Name/2012 Album Name/song
    # but also sometimes
    # Artists/a/Artist Name/2012 Album Name/CD1/song
    # or
    # Artists/a/Artist Name/collection/2012 Album Name/song
    # descend the path to try to find the album directory
    if path[0] in ['Artists', 'Various']:
        for i in range(len(path) - 2, -1, -1):
            if starts_with_recording_year(path[i]):
                pathdepth = i + 1
                break

    covers_dir = ""
    # Append part of the relative file path
    for path_component in path[0:pathdepth]:
        covers_dir = os.path.join(covers_dir, path_component)

    return covers_dir

def starts_with_recording_year(string):
    """
    Checks if string starts with a valid 
    recording year (between 1857 and now)
    """
    start_token = string.split()[0]
    try:
        year = int(start_token)
    except ValueError:
        return False

    return 1857 <= year <= datetime.datetime.now().year
