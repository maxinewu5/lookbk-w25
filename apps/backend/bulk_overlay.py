from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from tqdm import tqdm
import numpy as np
import os
import zipfile
import tempfile
from tempfile import mkdtemp

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
    final.write_videofile(output_path,
                         codec='libx264')
    
    # clean up
    video.close()
    final.close()

def bulk_add_caption_to_video(zip_file, caption_file, output_dir, font_size=70, position='center'):
    extracted_videos = mkdtemp()
    temp_output = mkdtemp()

    # creating output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # extracting captions from caption file
    with open(caption_file, 'r') as cf:
        captions = [line.strip() for line in cf if line.strip()]
    
    # extracting videos from zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.wmv')
        videos = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.startswith('._'):
                    continue

                if (file.lower().endswith(video_extensions)):
                    full_path = os.path.join(root, file)
                    videos.append(full_path)

        # if number of videos and number of captions are different, then terminate
        if len(videos) != len(captions): 
            print(f"Mismatch! {len(videos)} videos but {len(captions)} captions.")
            return
        
        # processing video with its caption pair
        for i, (video_file, caption) in enumerate(zip(videos, captions)):
            try:
                video_name = Path(video_file).stem
                output_path = str(Path(output_dir) / f"{video_name}_captioned.mp4")
                
                print(f"Processing video from: {video_file}")
                add_caption_to_video(
                    video_path=video_file,  # Already have full path
                    output_path=output_path,
                    caption_text=caption,
                    font_size=font_size,
                    position=position
                )

                tqdm.write(f"✓ Processed: {video_name}")
                tqdm.write(f"  Caption: {caption}")
            except Exception as e:
                tqdm.write(f"✗ Error processing {video_name}: {str(e)}")

if __name__ == "__main__":
    # get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_video = os.path.join(script_dir, "videos.zip")
    output_videos = os.path.join(script_dir, "with_captions")
    caption_file = os.path.join(script_dir, "captions.txt")
    
    # frontend UI will supply parameters as needed
    bulk_add_caption_to_video(
        zip_file = input_video,
        caption_file = caption_file,
        output_dir = output_videos,
        font_size = 100,  # default font size
        position = 'center'  # default position
    )