#!/usr/bin/python3
"""
    Composite overlay and main files from Snapchat's memory data.
"""
import os
import subprocess
import ffmpeg
import shutil
import platform
from pathlib import Path

def run_subprocess(commands,capture_output = False):
    is_windows = platform.system == "Windows"

    return subprocess.run(commands,shell=is_windows,capture_output=capture_output)


def resize_image(image_path, dimensions, new_file):

    resize_image_command = [
        # magick convert ./memories/A-overlay.png -resize 998x1920 new.png
        "magick",
        "convert",
        image_path,
        "-resize",
        str(dimensions["width"]) + "x" + str(dimensions["height"]),
        new_file
    ]

    return run_subprocess(resize_image_command)


def get_image_size(image_path):
    
    get_image_command = [
            "magick",
            "identify",
            "-format",
            "%w %h",
            image_path
    ]

    result = run_subprocess(get_image_command,capture_output=True)

    result_string = result.stdout.decode("utf8")

    width, height = result_string.split(" ")

    return {"height":int(height), "width":int(width)}


def composite_images(overlay_path, main_path, new_file):
    # magick composite new.png ./memories/A-main.jpg -compose over -gravity center composite.png
    composite_image_command = [
            "magick",
            "composite",
            overlay_path,
            main_path,
            "-compose",
            "over",
            "-gravity",
            "center",
            new_file
    ]

    return run_subprocess(composite_image_command)


def move_composited_file(old_file_path, new_path):
    # should the composited directory not exist, make it
    # then move the composited file into it. Helps
    # with file organization
    Path("./memories/composited").mkdir(parents=True, exist_ok=True)
    shutil.move(old_file_path, new_path)

# list the files in the memories folder
memories_files_raw = os.listdir("./memories")
memories_files_filtered = []

# loop over each one, ensuring that there are only supported filetypes
supported_file_types = [".jpg",".png",".mp4"]

# TODO optimize further
for file in memories_files_raw:
    file_path, file_extension = os.path.splitext(file)
    if os.path.isfile(f'./memories/{file}') and file_extension in supported_file_types:
        memories_files_filtered.append(file)
    elif os.path.isdir(f'./memories/{file}'):
        print(f"'./memories/{file}' is a directory. Skipping...")
    else:
        # since we filter the files that are parsed,
        # there should be no need to throw an exception
        # and halt the script
        print("UNSUPPORTED_FILE: " + f'./memories/{file}')

file_count = len(memories_files_filtered)
print(f"You have {file_count} files to process. Beginning...")

# get all overlay files
overlays = list(filter(lambda x : "overlay" in x, memories_files_filtered))

for index, overlay in enumerate(overlays):
    print(f'Processing file {overlay} ({index}/{len(overlays)})')
    # get the corresponding file
    # which is all files that contain everything before "-overlay"
    # that are not this file
    memory_id = overlay.split("-overlay")[0]

    # as opposed to searching the array, which could be inefficient,
    # its probably faster to just test for an mp4 and a jpg,
    # and see which one hits
    mp4_exists = os.path.isfile("./memories/" + memory_id + "-main.mp4")

    jpg_exists = os.path.isfile("./memories/" + memory_id + "-main.jpg")

    if (mp4_exists and jpg_exists) or (not mp4_exists and not jpg_exists):
        raise Exception("SOMETHING_IS_VERY_WRONG")

    overlay_path = f"./memories/{memory_id}-overlay.png"

    # we need to use ffmpeg to apply the overlay to a video
    if mp4_exists:
        mp4_path = fr"./memories/{memory_id}-main.mp4"

        # get the size of the video
        mp4_probe = ffmpeg.probe(mp4_path)

        video_streams = [
                stream for stream in mp4_probe["streams"]
                if stream['codec_type'] == 'video'
        ]

        if len(video_streams) != 1:
            raise Exception(f"UNABLE_TO_FIND_STREAM: {memory_id}")

        mp4_stream = video_streams[0]

        # we need to check display matrix to get the rotation of the video,
        # so we know whether its height x width or width x height.
        # if this fails, just assume the video is rotated.
        rotated = True
        try:
            display_matrix = [
                side_data for side_data in mp4_stream["side_data_list"]
                if side_data["side_data_type"] == "Display Matrix"
            ][0]

            rotation = display_matrix["rotation"]

            # if we can get the display matrix,
            # check if its rotated by 90 deg,
            # 180 deg doesn't matter because the dimensions remain the same
            rotated = abs(rotation / 90) % 2 == 1
        except:
            pass

        if rotated:
            mp4_dimemsions = {
                "height":mp4_stream["coded_width"],
                "width":  mp4_stream["coded_height"],
            }
        else:
            mp4_dimemsions = {
                "height": mp4_stream["coded_height"],
                "width": mp4_stream["coded_width"]
            }


        overlay_path_tmp = overlay_path + ".tmp.png"



        # resize the overlay
        resize_image(overlay_path,mp4_dimemsions,overlay_path_tmp)
        composite_path = f"./memories/{memory_id}-composite.mp4"

        # apply the overlay to the video
        ffmpeg.filter(
            [
                ffmpeg.input(mp4_path),
                ffmpeg.input(overlay_path_tmp)
            ],
            'overlay'
        ).output(composite_path,loglevel="quiet").overwrite_output().run()


        os.remove(overlay_path_tmp)
        
        finalized_path = f"./memories/composited/{memory_id}-composite.mp4"

        move_composited_file(composite_path, finalized_path)


    # we need to use image magick to apply the overlay to a picture
    if jpg_exists:
        main_path = f"./memories/{memory_id}-main.jpg"

        overlay_size = get_image_size(overlay_path)
        main_size = get_image_size(main_path)

        # main seems to be always larger
        # TODO double check this

        # resize the overlay to be the same size as the main
        overlay_path_tmp = overlay_path + ".tmp.png"
        composite_path = f"./memories/{memory_id}-composite.jpg"
        finalized_path = f"./memories/composited/{memory_id}-composite.jpg"

        resize_image(overlay_path, main_size, overlay_path_tmp)

        composite_images(overlay_path_tmp, main_path, composite_path)

        os.remove(overlay_path_tmp)
        
        move_composited_file(composite_path, finalized_path)
