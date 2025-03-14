from moviepy import *
import os
import requests


#download videos from AWS (hooks only)
def download_video(url, save_path): #requires url from server and the path to save it at
    response = requests.get(url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return save_path #returns file path where it was downloaded

#stitch videos together
def stitch_videos(hooks, demos):
    # checks if number of hooks and number of demos are of parsable length (must be equal number of hooks & demos or demos must be a multiple of hooks)
    if(len(hooks) != len(demos) | len(demos) % len(hooks) != 0):
        raise ValueError("Hooks and Demos are not of parsable length.")

    stitched = [None] * len(demos)
    if(len(hooks) < len(demos)):
        i = 0
        while(i < len(demos) -1):
            for hook in hooks:
                stitch = concatenate_videoclips([hook, demos[i]])
                stitched[i] = stitch.write_videofile(f"video{i}.mp4").with_end(17)
    else:
        for i in range(len(hooks)):
            stitch = concatenate_videoclips([hooks[i], demos[i]])
            stitched[i] = stitch.write_videofile(f"video{i}.mp4").with_end(17)

    return stitched #returns list of stitched video clips

#organizes hooks and demos into lists to be stitched together
def upload_video(hook_list, demo_path):
    #download hook videos from AWS
    for i in range(len(hook_list)):
        hook_files = [download_video(hook_list[i],f"vid{i}.mp4")]
    #demo video upload
    folder_path = os.path.abspath(demo_path)  # Change this to folder containing videos
    demo_files = sorted(
        [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith((".mp4", ".mov"))])

    #if they aren't able to be uploaded, raise error
    if not demo_files:
        raise FileNotFoundError("No video files found in the specified folder.")
    if not hook_files:
        raise ValueError("Could not upload hook files. Check if they have been properly uploaded.")

    #return tuple of hook and demo files
    return hook_files, demo_files