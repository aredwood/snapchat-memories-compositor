# Snapchat Memories Compositor

_Composites main and overlay files from Snapchat into a single mp4 or jpg._

## Dependencies
### System
- ImageMagick (CLI binaries)
- ffmpeg (CLI Binaries)
- Python 3

### Python
- ffmpeg-python

## Setup

### Getting your data from Snapchat
Go to https://accounts.snapchat.com/v2/download-my-data and complete the form to get your data compiled from Snapchat. Be sure to select the "Include your Memories, Chat Media and Shared Stories" option at the top and select an appropriate time frame for what you want downloaded. This process can take some time.

### ImageMagick
The downloadable binaries for ImageMagick can be found [here.](https://imagemagick.org/script/download.php)

### ffmpeg
The downloadable binaries for ffmpeg can be found [here.](https://ffmpeg.org/download.html)

#### ffmpeg on Windows
Binaries for Windows installations of ffmpeg are instead  hosted [here.](https://www.gyan.dev/ffmpeg/builds/#release-builds)

When using the windows binaries, you have to add the contents of the `bin` folder to your system PATH. A very simple guide on how to do that is found [here.](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/) 

## Usage

Supported file typings are: `[".jpg",".png",".mp4"]`

1. `pip3 install -r requirements.txt`
2. Place your memories into a 'memories' in the root of this folder
    - The script should filter by supported file types and `file` types only. But should something be missed, delete anything that isn't supported (e.g. memories.html, .DS_Store, etc).
3. `python3 ./composite.py`
_A `composite` folder is created inside of your `memories` folder that contains the finalized files with their overlays on top._
