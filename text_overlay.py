import os
import boto3
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_text_clip(text, size, font_size=100, font_name='Arial', text_color=(255, 255, 255, 255), outline_color=(0, 0, 0, 255)):
    # transparent image for background
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # load font (will be default Arial)
    try:
        font = ImageFont.truetype(font_name, font_size)
    except:
        font = ImageFont.load_default()

    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top

    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # outline
    offsets = [(2,0), (-2,0), (0,2), (0,-2), (2,2), (-2,-2), (2,-2), (-2,2), (1,2), (-1,2), (2,1), (2,-1), (-2,1), (-2,-1), (1,-2), (-1,-2)]
    for offset_x, offset_y in offsets:
        draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

    return np.array(img)

def add_caption_to_video(video_path, output_path, caption_text, 
                     font_size = 100, position = 'center',
                     text_color = (255, 255, 255, 255), outline_color = (0, 0, 0, 255),
                     fade_duration = 0.5):
    # load the video
    video = VideoFileClip(video_path)

    # set caption to show for the entire video duration
    start_time = 0
    duration = video.duration

    # create text frame - always using Arial font
    text_frame = create_text_clip(caption_text, video.size, font_size, 'Arial', text_color, outline_color)

    # create text clip
    txt_clip = (ImageClip(text_frame)
                .set_duration(duration)
                .set_position(position)
                .set_start(start_time)
                .crossfadein(fade_duration)
                .crossfadeout(fade_duration))

    # overlay text on video
    final = CompositeVideoClip([video, txt_clip])

    # write output keeping original format
    final.write_videofile(output_path, codec='libx264')

    # clean up
    video.close()
    final.close()

def text_overlay(s3, bucket_name, s3_url, caption, font_size = 100, position = 'center'):
    filename = s3_url.split("/")[-1]
    local_input = f"/tmp/{filename}"
    processed_filename = f"overlaid_{filename.split('.')[0]}.mp4"
    local_output = f"/tmp/{processed_filename}"

    # download video from s3
    s3_key = "/".join(s3_url.split("/")[-2:])
    s3.download_file(bucket_name, s3_key, local_input)

    # add caption to video
    add_caption_to_video(local_input, local_output, caption, font_size, position)

    # upload processed video to s3
    s3.upload_file(local_output, bucket_name, f"overlaid/{s3_key}")
    
    processed_s3_url = f"https://{bucket_name}.s3.amazonaws.com/overlaid/{s3_key}"
    return processed_s3_url
