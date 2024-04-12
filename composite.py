#!/usr/bin/python3
import os
import subprocess

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

    # if (mp4_exists and jpg_exists) or (not mp4_exists and not jpg_exists):
    #     raise Exception("SOMETHING_IS_VERY_WRONG")

    # we need to use ffmpeg to apply the overlay to a video
    if mp4_exists:
        pass

    # we need to use image magick to apply the overlay to a picture
    if jpg_exists:

        overlay_path = f"./memories/{memory_id}-overlay.png"
        main_path = f"./memories/{memory_id}-main.jpg"

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