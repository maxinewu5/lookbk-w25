from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from tqdm import tqdm
import numpy as np
import os
import zipfile
import tempfile
from tempfile import mkdtemp

def create_text_clip(text, size, font_size=70, font_name='Arial', text_color=(255, 255, 255, 255), outline_color=(0, 0, 0, 255)):
    # Create a transparent image
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font = ImageFont.truetype(font_name, font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text size
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top
    
    # Calculate text position to center it
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text with outline
    for offset_x, offset_y in [(1,1), (-1,-1), (1,-1), (-1,1)]:
        draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)
    
    return np.array(img)

def add_caption_to_video(video_path, output_path, caption_text, start_time = None, duration = None,
                     font_size = 70, font_name = 'Arial', position = 'center',
                     text_color = (255, 255, 255, 255), outline_color = (0, 0, 0, 255),
                     fade_duration = 0.5):
    # Load the video
    video = VideoFileClip(video_path)
    
    
    # Calculate start time if not specified
    if start_time is None:
        start_time = video.duration / 3
    
    # Set duration if not specified
    if duration is None:
        duration = video.duration / 3
    
    # Create text frame
    text_frame = create_text_clip(caption_text, video.size, font_size, font_name, text_color, outline_color)
    
    # Create text clip
    txt_clip = (ImageClip(text_frame)
               .set_duration(duration)
               .set_position(position)
               .set_start(start_time)
               .crossfadein(fade_duration)
               .crossfadeout(fade_duration))
    
    # Overlay text on video
    final = CompositeVideoClip([video, txt_clip])
    

    # Write output keeping original format
    final.write_videofile(output_path,
                         codec='libx264')
    

    # Clean up
    video.close()
    final.close()

def bulk_add_caption_to_video(zip_file, caption_file, output_dir):
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
                    print(f"Appending: {Path(file).stem} (Full path: {full_path})")

        # if number of videos and number of captions are different, then terminate
        if len(videos) != len(captions): 
            print(f"Error: Mismatch! {len(videos)} videos but {len(captions)} captions.")
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
                    start_time=None,
                    duration=None
                )

                tqdm.write(f"✓ Processed: {video_name}")
                tqdm.write(f"  Caption: {caption}")
            except Exception as e:
                tqdm.write(f"✗ Error processing {video_name}: {str(e)}")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build full paths
    input_video = os.path.join(script_dir, "videos.zip")
    output_videos = os.path.join(script_dir, "with_captions")
    caption_file = os.path.join(script_dir, "captions.txt")
    
    print(f"Looking for files in: {script_dir}")
    print(f"Video file: {input_video}")
    print(f"Caption file: {caption_file}")
    
    bulk_add_caption_to_video(
        zip_file = input_video,
        caption_file = caption_file,
        output_dir = output_videos
    )
