from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import time
from datetime import datetime
from typing import List, Dict, Any
import uuid
import os
from dotenv import load_dotenv
from caption_generator import CaptionGenerator
from videofunctions import generate_hooks, runwayml_login, grab_video, generate_files_array
from text_overlay import text_overlay
from prisma import Prisma

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize Prisma client
prisma = Prisma()
prisma.connect()

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
        prompt = request.json.get("prompt", "")
        num_captions = request.json.get("num_captions", 3)  # Default to 3 captions
        
        # Generate captions using the prompt
        try:
            captions = caption_generator.generate_captions_from_prompt(prompt, num_captions)
        except Exception as e:
            # If caption generation fails, propagate the error
            raise Exception(f"Caption generation failed: {str(e)}")

        # Generate videos
        client = runwayml_login()
        files_array = generate_files_array()
        videos_to_add = generate_hooks(client, prompt, files_array)
        uploaded_videos = []

        for video_url in videos_to_add:
            filename = video_url.split("/")[-1]
            
            # Create video using Prisma
            new_video = prisma.video.create({
                'data': {
                    'filename': filename,
                    'prompt': prompt,
                    's3_url': video_url
                }
            })
            
            uploaded_videos.append({
                "filename": filename,
                "s3_url": video_url,
                "prompt": prompt,
                "created": new_video.created.isoformat()
            })
        
        # Apply text overlay to videos
        videos_with_caption = textoverlay(captions, [video["s3_url"] for video in uploaded_videos])
        
        # Return both videos and captions
        return jsonify({
            "message": "Videos and captions generated successfully", 
            "videos": uploaded_videos,
            "videos_with_captions": videos_with_caption,
            "captions": captions
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def textoverlay(captions, videos):
    videos_with_captions = []

    for caption, video in zip(captions, videos):
        s3_key = video.split("/")[-1]
        processed_s3_url = text_overlay(s3, BUCKET_NAME, s3_key, caption)
        videos_with_captions.append(processed_s3_url)
    
    # urls with captions
    return videos_with_captions

@app.teardown_appcontext
def shutdown_session(exception=None):
    prisma.disconnect()

if __name__ == "__main__":
    app.run(debug=True, port=5000) 