import os
import tempfile
from pathlib import Path
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from typing import List, Optional

class VideoService:
    def __init__(self, output_dir: str = "generated_videos"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)

    async def generate_reaction_video(
        self,
        input_video_path: str,
        reaction_type: str,
        demo_type: str,
        prompt: str
    ) -> dict:
        """
        Generate a reaction video based on the input parameters.
        Returns metadata about the generated video.
        """
        # TODO: Implement actual AI video generation here
        # For now, we'll return a mock response
        return {
            "id": f"gen_{os.path.basename(input_video_path)}",
            "url": input_video_path,  # In production, this would be the generated video URL
            "prompt": prompt,
            "reaction": reaction_type,
            "demoType": demo_type,
            "previewUrl": input_video_path,
            "description": f"Generated {reaction_type} reaction for {demo_type} demo"
        }

    async def combine_videos(
        self,
        hook_video_path: str,
        demo_video_path: str,
        output_filename: str
    ) -> str:
        """
        Combine a hook video with a demo video.
        Returns the path to the combined video.
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        with VideoFileClip(hook_video_path) as hook_clip, \
             VideoFileClip(demo_video_path) as demo_clip:
            
            # Ensure both videos have the same dimensions
            if hook_clip.size != demo_clip.size:
                demo_clip = demo_clip.resize(hook_clip.size)
            
            # Combine the videos
            final_clip = concatenate_videoclips([hook_clip, demo_clip])
            
            # Write the combined video
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac'
            )
        
        return output_path

    async def add_captions(
        self,
        video_path: str,
        captions: List[str],
        output_filename: str,
        font_size: int = 70
    ) -> str:
        """
        Add captions to a video.
        Returns the path to the captioned video.
        """
        from bulk_overlay import add_caption_to_video
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # For now, we'll just add the first caption
        # In a full implementation, you might want to handle multiple captions
        # at different timestamps
        if captions:
            add_caption_to_video(
                video_path=video_path,
                output_path=output_path,
                caption_text=captions[0],
                font_size=font_size,
                position='center'
            )
        
        return output_path 