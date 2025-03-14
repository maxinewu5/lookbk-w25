from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import time
from datetime import datetime
from typing import List, Dict, Any
import uuid
from flask_sqlalchemy import SQLAlchemy
from videofunctions import generate_hooks, runwayml_login, grab_video, generate_files_array
from apps.backend.bulk_overlay import bulk_add_caption_to_video
from text_overlay import text_overlay
import os

from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASS = os.getenv('MYSQL_PASS')

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET")
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

RDS_ENDPOINT = os.getenv('RDS_ENDPOINT')
RDS_DB = os.getenv('RDS_DB')
#change these codes to .env later

#s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

#logging into RDS
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{RDS_ENDPOINT}/{RDS_DB}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

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
        client = runwayml_login()
        files_array = generate_files_array()
        prompt = request.json.get("prompt", "person jumping with joy")

        videos_to_add = generate_hooks(client, prompt, files_array)

        uploaded_videos = []

        for videos in videos_to_add:
            filename = videos.split("/")[-1]
            s3_url = videos # need to check
            new_video = Video(filename=filename, prompt=prompt, s3_url=s3_url)
            db.session.add(new_video)  # Add to DB session
            uploaded_videos.append({
                "filename": filename,
                "s3_url": videos,
                "prompt": prompt,
                "created": new_video.created
            })
        db.session.commit()
        
        # takes captions and video files and returns urls of videos w caption
        videos_with_caption = textoverlay(captions, uploaded_videos)

        return jsonify({"message": "Videos generated and stored successfully", "videos": videos_to_add}), 201

    except Exception as e:
        db.session.rollback()  
        return jsonify({"error": str(e)}), 500

def textoverlay(captions, videos):
    videos_with_captions = []

    for caption, video in zip(captions, videos):
        s3_key = video.split("/")[-1]
        processed_s3_url = text_overlay(s3, BUCKET_NAME, s3_key, caption)
        videos_with_captions.append(processed_s3_url)
    
    # urls with captions
    return videos_with_captions

if __name__ == "__main__":
    app.run(debug=True, port=5000)
