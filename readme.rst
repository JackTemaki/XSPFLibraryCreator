XSPF Library Creator
--------------------

The xspf library creator is a small python script that generates a playlist in xspf file format from a specified music folder.
It supports reading meta-tags from mp3, m4a and flac. If the format is different, or tags are incomplete, it will assume an itunes-like folder structure like /artist/album/song_name.mp3.

Usage
^^^^^

As the script was originally designed to create a playlist for streaming music from a http webserver, it allows to specify a custom file prefix.
Assuming you run a web-server where files are located in /var/www/music/ and your server runs under http://server.domain.com, the command would be

.. highlight::
    python3 xspflibrarycreator--target_path http://server.domain.com/music/ --html /var/www/music/ libraryplaylist.xspf

Depending on the size of the playlist, a lot of music players are not capable of reading such big playlist files.
The recommended player is Clementine, also it works also fine with VLC.

Requirements
^^^^^^^^^^^^

Mutagen (https://mutagen.readthedocs.io/en/latest/) is used to read the meta-tags.