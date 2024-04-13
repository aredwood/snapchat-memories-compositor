#!/usr/bin/python3
import os
import subprocess
import ffmpeg

def resize_image(image_path, dimensions, new_file):
    subprocess.run([
        # magick convert ./memories/A-overlay.png -resize 998x1920 new.png
        "magick",
        "convert",
        image_path,
        "-resize",
        str(dimensions["width"]) + "x" + str(dimensions["height"]),
        new_file
    ])

def get_image_size(image_path):
    result = subprocess.run([
        "magick",
        "identify",
        "-format",
        "%w %h",
        image_path
    ],capture_output=True)

    result_string = result.stdout.decode("utf8")

    width, height = result_string.split(" ")

    return {"height":int(height), "width":int(width)}


def composite_images(overlay_path, main_path, new_file):
    # magick composite new.png ./memories/A-main.jpg -compose over -gravity center composite.png
    subprocess.run([
        "magick",
        "composite",
        overlay_path,
        main_path,
        "-compose",
        "over",
        "-gravity",
        "center",
        new_file
    ])

# list the files in the memories folder
memories_files = os.listdir("./memories")

# loop over each one, ensuring that there are only supported filetypes
supported_file_types = [".jpg",".png",".mp4"]

# TODO optimize
for file in memories_files:
    invalid_file = True
    for supported_file_type in supported_file_types:
        if file.endswith(supported_file_type):
            invalid_file = False
    if invalid_file:
        raise Exception("UNSUPPORTED_FILE: " + file)

# get all overlay files
overlays = list(filter(lambda x : "overlay" in x, memories_files))

for overlay in overlays:
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

        mp4_path = f"./memories/{memory_id}-main.mp4"

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
            pass;

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

        # apply the overlay to the video
        ffmpeg.filter(
            [
                ffmpeg.input(mp4_path),
                ffmpeg.input(overlay_path_tmp)
            ],
            'overlay'
        ).output(f"./memories/{memory_id}-composite.mp4",loglevel="quiet").overwrite_output().run()


        os.remove(overlay_path_tmp)

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

        resize_image(overlay_path, main_size, overlay_path_tmp)

        composite_images(overlay_path_tmp, main_path, composite_path)

        os.remove(overlay_path_tmp)
        pass