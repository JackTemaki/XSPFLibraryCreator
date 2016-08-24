"""
XSPF Library Creator
 --- xlc.py ---
Author: Nick Rossenbach
Created: 24.08.2016
"""

import argparse

from os import listdir
from os.path import isfile, join
from os import walk
import re
import sh
import xml.etree.cElementTree as ET


class XSPFFile(object):

    def __init__(self, library_path, target_path):
        self.library_path = library_path
        self.target_path = target_path

        self.playlist = ET.Element("playlist")
        self.playlist.set('xmlns','http://xspf.org/ns/0/')
        self.playlist.set('xmlns:vlc','http://www.videolan.org/vlc/playlist/ns/0/')

        title = ET.SubElement(self.playlist, "title")
        title.text = "Wiedergabeliste"

        self.tracklist = ET.SubElement(self.playlist, "trackList")


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
                if(re.match('(.*).mp3',file) != None or 
                    re.match('(.*).m4a',file) != None or
                    re.match('(.*).mpg',file) != None or
                    re.match('(.*).aiff',file) != None or
                    re.match('(.*).wav',file) != None):

                    files = files + [short_path+file]

            for directory in d:
                files.extend(recursive_scanner(base_path, short_path+directory+"/"))
            
            return files
        
        self.files = recursive_scanner(self.library_path, "")

    def generate_playlist(self, html_conform=True):
        for musicfile in self.files:
            track = ET.SubElement(self.tracklist, "track")
            location = ET.SubElement(track, "location")

            target_file = self.target_path + musicfile 

            if html_conform:
                location.text = target_file.replace(" ", "%20")
                location.text = location.text.replace("#", "%23")
            else:
                location.text = target_file.replace(" ", "\\ ")


            title = ET.SubElement(track, "title")
            creator = ET.SubElement(track, "creator")
            album = ET.SubElement(track, "album")


            title_text = re.sub("(.*)\/","",musicfile)

            title_text = re.sub("\.mp3","",title_text)
            title_text = re.sub("\.m4a","",title_text)
            title_text = re.sub("\.wav","",title_text)

            title.text = title_text
            # raw_info = re.sub(network_path,"",musicfile)
            info = re.split("\/",musicfile)
            creator.text = info[0]
            # check if album available
            if len(info) > 2:
                album.text = info[1]


def main():
    parser = argparse.ArgumentParser(description='XSPF Library Creator')
    parser.add_argument('library_path', type=str, 
                        help='file path to the music library folder')
    parser.add_argument('xspf_file', type=str, 
                        help='target path of the resulting xspf playlist')
    parser.add_argument('--target_path', type=str,
                        help='file path to be used inside the xspf file for referencing')
    args = parser.parse_args()

    if args.target_path is None:
        args.target_path = args.library_path

    xspf = XSPFFile(args.library_path, args.target_path)
    print("Scanning library folder for music files")
    xspf.generate_file_list()
    print("Generating Playlist File")
    xspf.generate_playlist()

    tree = ET.ElementTree(xspf.playlist)
    tree.write(args.xspf_file,encoding="UTF-8")


if __name__ == '__main__':
        main()
