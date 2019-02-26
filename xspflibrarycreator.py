"""
XSPF Library Creator
 --- xspflibrarycreator.py ---
Author: Nick Rossenbach
Created: 24.08.2016
"""

import argparse
import mutagen
import mutagen.id3 as id3
from os import walk
import re
import xml.etree.cElementTree as ET


class FileMetadata:
    """aquire metadata from supported file types"""

    def __init__(self, filename, musicfile):

        # required attributes
        self.title = None
        self.artist = None
        self.album = None

        self.type = re.split("\.", musicfile)[-1]

        try:
            self.file = mutagen.File(filename)

            # get bitrate if not flac
            if self.type != "flac":
                self.bitrate = self.file.info.bitrate

            # check for track duration
            if hasattr(self.file.info, 'length'):
                self.length = int(self.file.info.length * 1000)
            else:
                self.length = ""

            # load ID3 tags in case of mp3
            if self.type == "mp3":
                # check for ID3 tags
                id3_title = id3.ID3.get(self.file, 'TIT2')
                if id3_title:
                    self.title = id3_title.text[0]

                id3_artist = id3.ID3.get(self.file, 'TPE1')
                if id3_artist:
                    self.artist = id3_artist.text[0]

                id3_album = id3.ID3.get(self.file, 'TALB')
                if id3_album:
                    self.album = id3_album.text[0]

                id3_genre = id3.ID3.get(self.file, 'TCON')
                if id3_genre:
                    self.genre = id3_genre.text[0]

                id3_tracknumber = id3.ID3.get(self.file, 'TRCK')
                if id3_tracknumber:
                    try:
                        self.tracknumber = int(
                            re.split("/", id3_tracknumber.text[0])[0])
                    except ValueError:
                        self.tracknumber = 0

            # check for itunes tags if m4a
            elif self.type == "m4a":
                m4a_title = self.file.get('©nam')
                if m4a_title:
                    self.title = m4a_title[0]

                m4a_artist = self.file.get('©ART')
                if m4a_artist:
                    self.artist = m4a_artist[0]

                m4a_album = self.file.get('©alb')
                if m4a_album:
                    self.album = m4a_album[0]

                m4a_genre = self.file.get('©gen')
                if m4a_genre:
                    self.genre = m4a_genre[0]

                m4a_tracknumber = self.file.get('trkn')
                if m4a_tracknumber:
                    self.tracknumber = m4a_tracknumber[0][0]

            elif self.type == "flac":
                # check for flac elements
                flac_title = self.file.get('title')
                if flac_title:
                    self.title = flac_title[0]

                flac_artist = self.file.get('artist')
                if flac_artist:
                    self.artist = flac_artist[0]

                flac_album = self.file.get('album')
                if flac_album:
                    self.album = flac_album[0]

                flac_genre = self.file.get('genre')
                if flac_genre:
                    self.genre = flac_genre[0]
                
                flac_tracknumber = self.file.get('tracknumber')
                if flac_tracknumber:
                    self.tracknumber = flac_tracknumber[0]

        except Exception:
            pass

        # if no information available, generate from file path
        if not self.title:
            title_text = re.sub("(.*)\/", "", musicfile)
            title_text = re.sub("\.mp3", "", title_text)
            title_text = re.sub("\.m4a", "", title_text)
            title_text = re.sub("\.wav", "", title_text)
            self.title = title_text

        if not self.artist:
            info = re.split("\/", musicfile)
            self.artist = info[0]

        if not self.album:
            info = re.split("\/", musicfile)
            if len(info) > 2:
                self.album = info[1]


class XSPFFile(object):

    def __init__(self, library_path, target_path):
        self.library_path = library_path
        self.target_path = target_path

        self.playlist = ET.Element("playlist")
        self.playlist.set('xmlns', 'http://xspf.org/ns/0/')
        self.playlist.set(
            'xmlns:vlc', 'http://www.videolan.org/vlc/playlist/ns/0/')

        title = ET.SubElement(self.playlist, "title")
        title.text = "Playlist"

        self.tracklist = ET.SubElement(self.playlist, "trackList")

        self.num_tracks = 0

    def generate_file_list(self):

        def recursive_scanner(base_path, short_path):
            files = []
            f = []
            d = []
            for (dirpath, dirnames, filenames) in walk(base_path + short_path):
                f.extend(filenames)
                d.extend(dirnames)
                break

            for file in f:
                if(re.match('(.*).mp3', file) != None or
                        re.match('(.*).m4a', file) != None or
                        re.match('(.*).mpg', file) != None or
                        re.match('(.*).aiff', file) != None or
                        re.match('(.*).wav', file) != None or
                        re.match('(.*).flac', file) != None):

                    files = files + [short_path+file]
                    self.num_tracks += 1

            for directory in d:
                files.extend(recursive_scanner(
                    base_path, short_path+directory+"/"))

            return files

        self.files = recursive_scanner(self.library_path, "")

    def generate_playlist(self, html_conform=False):

        count = 0
        for musicfile in self.files:
            count += 1
            print("File %i of %i" % (count, self.num_tracks), end='\r')
            track = ET.SubElement(self.tracklist, "track")
            location = ET.SubElement(track, "location")

            target_file = self.target_path + musicfile
            info = FileMetadata(self.library_path + musicfile, musicfile)

            if html_conform:
                location.text = target_file.replace(" ", "%20")
                location.text = location.text.replace("#", "%23")

            title = ET.SubElement(track, "title")
            creator = ET.SubElement(track, "creator")
            album = ET.SubElement(track, "album")

            title.text = info.title
            creator.text = info.artist
            album.text = info.album

            einfo = ET.SubElement(track, "info")
            einfo.text = str(info.type)

            if hasattr(info, "genre") and info.genre:
                genre = ET.SubElement(track, "genre")
                genre.text = str(info.genre)

            if hasattr(info, "bitrate") and info.bitrate:
                bitrate = ET.SubElement(track, "bitrate")
                bitrate.text = str(info.bitrate)

            if hasattr(info, "length") and info.length:
                length = ET.SubElement(track, "duration")
                length.text = str(info.length)

            if hasattr(info, "tracknumber") and info.tracknumber:
                tracknumber = ET.SubElement(track, "trackNum")
                tracknumber.text = str(info.tracknumber)


def main():
    parser = argparse.ArgumentParser(description="XSPF Library Creator",
                                     usage='python3 xspflibrarycreator.py --target_path http://server.hoster.org/music/ --html "/path/to/MUSIC/" ~/Desktop/libraryplaylist.xspf')

    parser.add_argument('library_path', type=str,
                        help='file path to the music library folder')
    parser.add_argument('xspf_file', type=str,
                        help='target path of the resulting xspf playlist')
    parser.add_argument('--target_path', type=str,
                        help='file path to be used inside the xspf file for referencing')
    parser.add_argument('--html', action='store_true',
                        default=False, help='use html conform location strings')

    args = parser.parse_args()

    # if no target path is specified, use library path as target
    if args.target_path is None:
        args.target_path = args.library_path

    xspf = XSPFFile(args.library_path, args.target_path)

    print("Scanning library folder for music files")
    xspf.generate_file_list()

    print("Generating Playlist File")
    xspf.generate_playlist(html_conform=args.html)

    tree = ET.ElementTree(xspf.playlist)
    tree.write(args.xspf_file, encoding="UTF-8")


if __name__ == '__main__':
    main()
