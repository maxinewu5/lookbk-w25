from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import time
from datetime import datetime
from typing import List, Dict, Any
import uuid
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from caption_generator import CaptionGenerator
from videofunctions import generate_hooks, runwayml_login, grab_video, generate_files_array

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# Database configuration
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASS = os.getenv('MYSQL_PASS')
RDS_ENDPOINT = os.getenv('RDS_ENDPOINT')
RDS_DB = "videosdb"

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{RDS_ENDPOINT}/{RDS_DB}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialize services
caption_generator = CaptionGenerator()

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.String(255), nullable=False)
    s3_url = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

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
            new_video = Video(filename=filename, prompt=prompt, s3_url=video_url)
            db.session.add(new_video)
            
            # Create a timestamp for the created field
            created_time = datetime.utcnow().isoformat()
            
            uploaded_videos.append({
                "filename": filename,
                "s3_url": video_url,
                "prompt": prompt,
                "created": created_time
            })
        
        db.session.commit()
        
        # Return both videos and captions
        return jsonify({
            "message": "Videos and captions generated successfully", 
            "videos": uploaded_videos,
            "captions": captions
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-captions", methods=["POST"])
def generate_captions():
    """
    Generate captions for a video based on its type.
    
    Expected JSON payload:
    {
        "video_type": str,
        "num_captions": int (optional)
    }
    """
    try:
        data = request.json
        if not data or "video_type" not in data:
            return jsonify({"error": "Missing video_type in request"}), 400
            
        video_type = data["video_type"]
        num_captions = data.get("num_captions", 15)  # Default to 15 captions if not specified
        
        # Generate captions
        captions = caption_generator.generate_captions(video_type, num_captions)
        
        if not captions:
            return jsonify({"error": "Failed to generate captions"}), 500
            
        # Return the generated captions
        return jsonify({
            "captions": captions,
            "video_type": video_type,
            "count": len(captions)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000) 