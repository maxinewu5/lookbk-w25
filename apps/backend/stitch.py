from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import requests
import boto3
from datetime import datetime
from prisma import Prisma
from typing import List, Dict
# import asyncio
from dotenv import load_dotenv

load_dotenv()

# Initialize Prisma client
prisma = Prisma()
prisma.connect()

# AWS S3 setup
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def download_video(url: str, save_path: str) -> str:
    """Download video from S3 URL to local path"""
    response = requests.get(url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return save_path

def stitch_videos(hook_paths: List[str], demo_paths: List[str]) -> List[str]:
    """Stitch hook and demo videos together"""
    if len(hook_paths) != len(demo_paths) and len(demo_paths) % len(hook_paths) != 0:
        raise ValueError("Hooks and Demos are not of parsable length.")

    stitched_paths = []
    output_dir = "/tmp/stitched"
    os.makedirs(output_dir, exist_ok=True)

    if len(hook_paths) < len(demo_paths):
        for i, demo_path in enumerate(demo_paths):
            hook_idx = i % len(hook_paths)
            hook_clip = VideoFileClip(hook_paths[hook_idx])
            demo_clip = VideoFileClip(demo_path)
            
            output_path = f"{output_dir}/stitched_{i}.mp4"
            final_clip = concatenate_videoclips([hook_clip, demo_clip])
            final_clip.write_videofile(output_path)
            
            hook_clip.close()
            demo_clip.close()
            final_clip.close()
            
            stitched_paths.append(output_path)
    else:
        for i in range(len(hook_paths)):
            hook_clip = VideoFileClip(hook_paths[i])
            demo_clip = VideoFileClip(demo_paths[i])
            
            output_path = f"{output_dir}/stitched_{i}.mp4"
            final_clip = concatenate_videoclips([hook_clip, demo_clip])
            final_clip.write_videofile(output_path)
            
            hook_clip.close()
            demo_clip.close()
            final_clip.close()
            
            stitched_paths.append(output_path)

    return stitched_paths

async def process_videos(job_id: str) -> Dict:
    """Process videos for a given job"""
    try:
        # Update job status
        job = prisma.processingjob.update(
            where={'id': job_id},
            data={'status': 'processing'}
        )

        # Get generated videos and demo video
        generated_videos = prisma.video.find_many(
            where={
                'id': {'in': job.generatedIds},
                'type': 'generated'
            }
        )
        
        demo_video = prisma.video.find_first(
            where={
                'id': job.demoVideoId,
                'type': 'demo'
            }
        )

        if not generated_videos or not demo_video:
            raise ValueError("Missing required videos")

        # Download videos locally
        hook_paths = []
        demo_paths = []
        
        for video in generated_videos:
            local_path = f"/tmp/hook_{video.id}.mp4"
            hook_paths.append(download_video(video.s3_url, local_path))
        
        demo_paths = [download_video(demo_video.s3_url, f"/tmp/demo_{demo_video.id}.mp4")] * len(generated_videos)

        # Stitch videos
        stitched_paths = stitch_videos(hook_paths, demo_paths)

        # Upload stitched videos to S3 and save to database
        final_video_ids = []
        for i, path in enumerate(stitched_paths):
            # Upload to S3
            s3_key = f"final/stitched_{datetime.now().timestamp()}_{i}.mp4"
            s3.upload_file(path, BUCKET_NAME, s3_key)
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

            # Save to database
            final_video = prisma.video.create({
                'data': {
                    'filename': os.path.basename(path),
                    'prompt': generated_videos[i].prompt,
                    's3_url': s3_url,
                    'type': 'final',
                    'caption': job.captions[i] if i < len(job.captions) else None
                }
            })
            final_video_ids.append(final_video.id)

        # Update job with final video IDs
        updated_job = prisma.processingjob.update(
            where={'id': job_id},
            data={
                'status': 'completed',
                'finalVideoIds': final_video_ids
            }
        )

        # Cleanup temporary files
        for path in hook_paths + demo_paths + stitched_paths:
            if os.path.exists(path):
                os.remove(path)

        return {
            "message": "Videos processed successfully",
            "job": updated_job
        }

    except Exception as e:
        # Update job with error
        prisma.processingjob.update(
            where={'id': job_id},
            data={
                'status': 'failed',
                'error': str(e)
            }
        )
        raise e

    finally:
        # Cleanup any remaining temporary files
        for file in os.listdir("/tmp"):
            if file.startswith(("hook_", "demo_", "stitched_")):
                try:
                    os.remove(os.path.join("/tmp", file))
                except:  # noqa: E722
                    pass