import mutagen
import mutagen.id3 as id3
import re

class FileMetadata:

    def __init__(self, filename, musicfile):

        self.title = None
        self.artist = None
        self.album = None

        self.type = re.split("\.", musicfile)[-1]
        
        try:
            self.file = mutagen.File(filename)
           
            if self.type != "flac":
                self.bitrate = self.file.info.bitrate
            
            if hasattr(self.file.info, 'length'):
                self.length = int(self.file.info.length*1000)
            else:
                self.length = ""

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
            
            elif self.type == "m4a":
                #check for itunes tags
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
            
            elif self.type == "flac":
                #check for flac elements
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

        except Exception:
            pass

        if not self.title:
            title_text = re.sub("(.*)\/","",musicfile)
            title_text = re.sub("\.mp3","",title_text)
            title_text = re.sub("\.m4a","",title_text)
            title_text = re.sub("\.wav","",title_text)
            self.title = title_text
        
        if not self.artist:
            info = re.split("\/",musicfile)
            self.artist = info[0]
        
        if not self.album:
            info = re.split("\/",musicfile)
            if len(info) > 2:
                self.album = info[1]


