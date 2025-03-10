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
load_dotenv()
app = Flask(__name__)
CORS(app)


MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASS = os.getenv('MYSQL_PASS')

RDS_ENDPOINT = os.getenv('RDS_ENDPOINT')
RDS_DB = "videosdb"
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

class DemoVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_url = db.Column(db.String(500), nullable=False)
    uploaded = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

#importing all the needed files

from videofunctions import generate_hooks, runwayml_login, grab_video, generate_files_array

@app.route("/api/generate-videos", methods=["POST"])
def generate_videos():
    try:
        # TODO: logic to create this route
        client = runwayml_login()
        files_array = generate_files_array()
        prompt = request.json.get("prompt", "person jumping with joy")

        videos_to_add = generate_hooks(client, prompt, files_array)

        uploaded_vids = []

        for videos in videos_to_add:
            new_video = Video(filename=filename, prompt=prompt, s3_url=s3_url)
            db.session.add(new_video)  # Add to DB session
            uploaded_videos.append({
                "filename": video.split("/")[-1],
                "s3_url": videos,
                "prompt": prompt,
                "created": new_video.created
            })
        db.session.commit()
        return jsonify({"message": "Videos generated and stored successfully", "videos": videos_to_add}), 201


    except Exception as e:
        db.session.rollback()  
        return jsonify({"error": str(e)}), 500

import boto3

@app.route("/api/upload_demo", methods=["POST"])
def upload_demo():
    try:
        # S3 bucket details
        S3_BUCKET = "lookbk-video-bucket"
        S3_REGION = "us-west-1"
        AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
        AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

        # Validate if file is in request
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Generate a unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"

        # Upload to S3
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION,
        )

        s3.upload_fileobj(file, S3_BUCKET, filename)

        # Construct S3 file URL
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

        # Save to database
        new_demo_video = DemoVideo(filename=filename, s3_url=s3_url)
        db.session.add(new_demo_video)
        db.session.commit()

        return jsonify({"message": "Video uploaded successfully", "s3_url": s3_url}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
        


if __name__ == "__main__":
    app.run(debug=True, port=5000)