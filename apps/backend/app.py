from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
from caption_generator import CaptionGenerator
from videofunctions import generate_hooks, runwayml_login, generate_files_array
from text_overlay import text_overlay
from stitch import process_videos
from prisma import Prisma

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app)

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

# Initialize services
caption_generator = CaptionGenerator()

@app.route("/api/generate-videos", methods=["POST"])
def generate_videos():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        demo_video_id = data.get("demoVideoId")
        reaction_type = data.get("reactionType")
        demo_type = data.get("demoType")
        num_captions = data.get("num_captions", 3)
        
        if not all([demo_video_id, prompt, reaction_type, demo_type]):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Create processing job
        job = prisma.processingjob.create({
            'data': {
                'status': 'pending',
                'prompt': prompt,
                'demoVideoId': demo_video_id,
                'captions': [],
                'generatedIds': [],
                'finalVideoIds': []
            }
        })

        # Start async processing
        asyncio.create_task(process_video_generation(job.id, prompt, num_captions, reaction_type, demo_type))
        
        return jsonify({
            "message": "Video generation started",
            "jobId": job.id
        }), 202
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

async def process_video_generation(job_id: str, prompt: str, num_captions: int, reaction_type: str, demo_type: str):
    try:
        # Generate captions
        captions = caption_generator.generate_captions_from_prompt(prompt, num_captions)
        
        # Update job with captions
        job = prisma.processingjob.update({
            'where': {'id': job_id},
            'data': {'captions': captions}
        })
        
        # Generate videos using RunwayML
        client = runwayml_login()
        files_array = generate_files_array()
        generated_urls = generate_hooks(client, prompt, files_array)
        generated_ids = []
        
        # Save generated videos to GeneratedVideo model
        for url in generated_urls:
            filename = url.split("/")[-1]
            video = prisma.generatedvideo.create({
                'data': {
                    'filename': filename,
                    'prompt': prompt,
                    's3_url': url,
                    'reaction': reaction_type,
                    'demoType': demo_type,
                    'captions': captions
                }
            })
            generated_ids.append(video.id)
        
        # Update job with generated video IDs
        job = prisma.processingjob.update({
            'where': {'id': job_id},
            'data': {
                'status': 'processing',
                'generatedIds': generated_ids
            }
        })

        # Get demo video
        demo_video = prisma.demovideo.find_unique(
            where={'id': job.demoVideoId}
        )

        # Stitch videos and add captions
        final_video_ids = await stitch_and_overlay(
            generated_ids=generated_ids,
            demo_video=demo_video,
            captions=captions,
            prompt=prompt
        )

        # Update job as completed
        prisma.processingjob.update({
            'where': {'id': job_id},
            'data': {
                'status': 'completed',
                'finalVideoIds': final_video_ids
            }
        })
        
    except Exception as e:
        prisma.processingjob.update({
            'where': {'id': job_id},
            'data': {
                'status': 'failed',
                'error': str(e)
            }
        })

async def stitch_and_overlay(generated_ids: list, demo_video: dict, captions: list, prompt: str):
    # Get generated videos
    generated_videos = prisma.generatedvideo.find_many(
        where={'id': {'in': generated_ids}}
    )

    final_video_ids = []
    
    for idx, (gen_video, caption) in enumerate(zip(generated_videos, captions)):
        try:
            # Stitch videos
            stitched_path = f"/tmp/stitched_{idx}.mp4"
            await process_videos(gen_video.s3_url, demo_video.url, stitched_path)
            
            # Add caption overlay
            final_path = f"/tmp/final_{idx}.mp4"
            text_overlay(s3, BUCKET_NAME, stitched_path, caption, output_path=final_path)
            
            # Upload to S3
            s3_key = f"final/video_{datetime.now().timestamp()}_{idx}.mp4"
            s3.upload_file(final_path, BUCKET_NAME, s3_key)
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
            
            # Save to Video model
            final_video = prisma.video.create({
                'data': {
                    'filename': f"final_{idx}.mp4",
                    'prompt': prompt,
                    's3_url': s3_url,
                    'type': 'final',
                    'caption': caption
                }
            })
            
            final_video_ids.append(final_video.id)
            
            # Cleanup temp files
            os.remove(stitched_path)
            os.remove(final_path)
            
        except Exception as e:
            print(f"Error processing video {idx}: {str(e)}")
            continue
    
    return final_video_ids

@app.route("/api/job-status/<job_id>", methods=["GET"])
def get_job_status(job_id):
    try:
        job = prisma.processingjob.find_unique(where={'id': job_id})
        if not job:
            return jsonify({"error": "Job not found"}), 404
            
        response = {
            "status": job.status,
            "error": job.error
        }
        
        if job.status == 'completed':
            final_videos = prisma.video.find_many(
                where={'id': {'in': job.finalVideoIds}}
            )
            response["videos"] = [
                {
                    "id": v.id,
                    "url": v.s3_url,
                    "caption": v.caption
                } for v in final_videos
            ]
            
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.teardown_appcontext
def shutdown_session(exception=None):
    prisma.disconnect()

if __name__ == "__main__":
    app.run(debug=True, port=5000) 