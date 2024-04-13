# Snapchat Memories Compositor

_Composites main and overlay files from Snapchat into a single mp4 or jpg._

## Dependencies
- ImageMagick
- ffmpeg
- Python 3
    - ffmpeg-python


## Usage

1. `pip3 install -r requirements.txt`
2. Place your memories into a 'memories' in the root of this folder - make sure to delete anything that isn't an mp4 or jpg (e.g. memories.html, .DS_Store, etc).
4. `python3 ./composite.py`
_There will now be "composite" files within your memories folder, which are the main files with the overlay ontop._
