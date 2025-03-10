import os
from pathlib import Path
import tempfile
from typing import List, Dict
from .aws_service import AWSService
from generate_captions import generate_captions
from stitch import stitch_videos, download_video
from bulk_overlay import add_caption_to_video

class VideoPipelineService:
    def __init__(self, aws_bucket: str, output_dir: str = "processed_videos"):
        self.aws_service = AWSService(aws_bucket)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path(tempfile.gettempdir()) / "video_pipeline"
        self.temp_dir.mkdir(exist_ok=True)

    async def process_videos(
        self,
        hook_urls: List[str],
        demo_urls: List[str],
        video_type: str
    ) -> List[Dict[str, str]]:
        """
        Process videos through the complete pipeline:
        1. Download videos from AWS
        2. Generate AI captions
        3. Stitch videos together
        4. Add captions to videos
        5. Upload processed videos back to AWS
        """
        try:
            # Step 1: Download all videos
            hook_paths = []
            demo_paths = []
            
            for i, url in enumerate(hook_urls):
                local_path = self.temp_dir / f"hook_{i}.mp4"
                download_video(url, str(local_path))
                hook_paths.append(str(local_path))
            
            for i, url in enumerate(demo_urls):
                local_path = self.temp_dir / f"demo_{i}.mp4"
                download_video(url, str(local_path))
                demo_paths.append(str(local_path))

            # Step 2: Generate captions
            caption_file = self.temp_dir / "captions.txt"
            generate_captions(video_type, str(caption_file))
            
            with open(caption_file, 'r') as f:
                captions = [line.strip() for line in f if line.strip()]

            # Step 3: Stitch videos
            stitched_videos = stitch_videos(hook_paths, demo_paths)

            # Step 4: Add captions to stitched videos
            processed_videos = []
            for i, (video_path, caption) in enumerate(zip(stitched_videos, captions)):
                output_path = self.output_dir / f"final_video_{i}.mp4"
                
                add_caption_to_video(
                    video_path=video_path,
                    output_path=str(output_path),
                    caption_text=caption,
                    font_size=70,
                    position='center'
                )
                
                # Step 5: Upload to AWS and get URL
                s3_key = f"processed_videos/final_video_{i}.mp4"
                url = await self.aws_service.upload_video(str(output_path), s3_key)
                
                processed_videos.append({
                    "id": f"video_{i}",
                    "url": url,
                    "caption": caption
                })

            return processed_videos

        except Exception as e:
            raise Exception(f"Error in video pipeline: {str(e)}")
        
        finally:
            # Cleanup temporary files
            self.cleanup()

    def cleanup(self):
        """
        Clean up temporary files
        """
        try:
            for file in self.temp_dir.glob("*"):
                file.unlink()
            self.aws_service.cleanup_temp_files()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}") 