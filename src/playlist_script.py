from os import listdir
from os.path import isfile, join
from os import walk
import re
import sh
import xml.etree.cElementTree as ET

network_path = "http://music:mightymusic@jacktemaki.duckdns.org/music/music_files/"

path = "/var/www/music/music_files/"

full_filelist = []
def browse_directory(path,short_path):
	files = []
	f = []
	d = []
	for (dirpath, dirnames, filenames) in walk(path+short_path):
    		f.extend(filenames)
    		d.extend(dirnames)
    		break


	for file in f:
		if(re.match('(.*).mp3',file) != None or 
			re.match('(.*).m4a',file) != None or
			re.match('(.*).mpg',file) != None or
			re.match('(.*).aiff',file) != None or
			re.match('(.*).wav',file) != None):

			files = files + [network_path+short_path+file]

	for directory in d:
		files.extend(browse_directory(path,short_path+directory+"/"))
        
	playlist = ET.Element("playlist")
	playlist.set('xmlns','http://xspf.org/ns/0/')
	playlist.set('xmlns:vlc','http://www.videolan.org/vlc/playlist/ns/0/')

	title = ET.SubElement(playlist,"title")
	title.text = "Wiedergabeliste"

	tracklist = ET.SubElement(playlist,"trackList")

	#delete empty folders (RISKY)
	#if len(files) == 0:
		#cmd = sh.Command("rm")
		#cmd("-r",path+short_path)
		#print("delete: "+path+short_path)
	
	for musicfile in files:
		track = ET.SubElement(tracklist,"track")
		location = ET.SubElement(track,"location")
		location.text = musicfile.replace(" ","%20").decode('utf-8')
		location.text = location.text.replace("#", "%23")
		if re.match('(.*).mp3',musicfile) or True:
			ttitle = ET.SubElement(track,"title")
			title_text = re.sub("http\:\/(.*)\/","",musicfile)
			title_text = re.sub("\.mp3","",title_text)
			title_text = re.sub("\.m4a","",title_text)
			ttitle.text = title_text.decode('utf-8')
			creator = ET.SubElement(track,"creator")
			raw_info = re.sub(network_path,"",musicfile)
			info = re.split("\/",raw_info)
			creator.text = info[0].decode('utf-8')
			#check if album available
			if len(info) > 2:
				album = ET.SubElement(track,"album")
				album.text = info[1].decode('utf-8') 
        
	path_info = re.split("\/",short_path)
	
	if len(path_info) == 1:
		playlist_name = "archive.xspf"
	else:
		creator = path_info[0]
		album = ""
		playlist_name = creator+".xspf"        
		if len(path_info) > 2:
			album = path_info[1]	
			playlist_name = creator+" - "+album+".xspf"        

	tree = ET.ElementTree(playlist)
	tree.write(path+short_path+playlist_name,encoding="UTF-8")
	return files

full_filelist = browse_directory(path, "")
print(len(full_filelist))
#print(full_filelist)
print("success")
