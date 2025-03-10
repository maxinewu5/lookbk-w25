from moviepy import *
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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

s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

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

class ProcessedVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_url = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

class DemoVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_url = db.Column(db.String(500), nullable=False)
    uploaded = db.Column(db.DateTime, default=datetime.utcnow)

#download videos from AWS (hooks only)
def download_video(url, save_path): #requires url from server and the path to save it at
    response = requests.get(url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return save_path #returns file path where it was downloaded

#stitch videos together
def stitch_videos(hooks, demos):
    # checks if number of hooks and number of demos are of parsable length (must be equal number of hooks & demos or demos must be a multiple of hooks)
    if(len(hooks) != len(demos) | len(demos) % len(hooks) != 0):
        raise ValueError("Hooks and Demos are not of parsable length.")

    stitched = [None] * len(demos)
    if(len(hooks) < len(demos)):
        i = 0
        while(i < len(demos) -1):
            for hook in hooks:
                stitch = concatenate_videoclips([hook, demos[i]])
                stitched[i] = stitch.write_videofile(f"video{i}.mp4").with_end(17)
    else:
        for i in range(len(hooks)):
            stitch = concatenate_videoclips([hooks[i], demos[i]])
            stitched[i] = stitch.write_videofile(f"video{i}.mp4").with_end(17)

    return stitched #returns list of stitched video clips

#organizes hooks and demos into lists to be stitched together
def arrange_video(hook_list, demo_list):
    #download hook videos from AWS
    for i in range(len(hook_list)):
        hook_files = [VideoFileClip(download_video(hook_list[i],f"hvid{i}.mp4"))]
    #demo video upload
    for i in range(len(demo_list)):
        demo_files = [VideoFileClip(download_video(demo_list[i], f"dvid{i}.mp4"))]

    #if they aren't able to be uploaded, raise error
    if not demo_files:
        raise FileNotFoundError("No video files found in the specified folder.")
    if not hook_files:
        raise ValueError("Could not upload hook files. Check if they have been properly uploaded.")

    #return tuple of hook and demo files
    return hook_files, demo_files

def process_videos():
    try:
        hooks = []
        demos = []
        videos = Video.query.all()
        demoVideos = DemoVideo.query.all()

        #retrieve s3 urls for hooks and demos
        hooks = [video.s3_url for video in videos]
        demos = [demo.s3_url for demo in demoVideos]

        processed_videos = arrange_video(hooks, demos)
        hook_list, demo_list = processed_videos

        #stitch processed videos
        stitches = stitch_videos(hook_list, demo_list)

        for video_url in stitches:
            filename = video_url.split("/")[-1]
            new_processed_video = ProcessedVideo(
                filename=filename,
                s3_url=video_url
            )

            # Add to the database session
            db.session.add(new_processed_video)

            # Commit the transaction to save the stitched videos
        db.session.commit()
        return jsonify({"message": "Videos stitched and stored successfully", "videos": stitches}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500