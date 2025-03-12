from runwayml import RunwayML
import os
import time
import requests
import boto3
import uuid
from botocore.config import Config
import base64
from dotenv import load_dotenv
load_dotenv()



def runwayml_login():
  RUNWAYML_API_KEY = os.getenv('RUNWAYML_API_KEY')
  RUNWAYML_API_SECRET = RUNWAYML_API_KEY
  client = RunwayML(api_key=RUNWAYML_API_SECRET)
  return client

def generate_files_array():
  folder_path = "stockimages"
  files_array = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
  return files_array

def grab_video(link, names3):
  #s3 bucket information and access
  S3_BUCKET = "lookbk-video-bucket"
  S3_REGION = "us-west-1"
  AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
  AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
  #video_filename = os.path.join(output_folder, link.split("/")[-1].split("?")[0])

  if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS credentials not found. Check your .env file or environment variables.")

  s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION,
    config=Config(signature_version="s3v4")
  )

  # Stream video from URL
  response = requests.get(link, stream=True)
  response.raise_for_status()

  # Upload directly to S3
  s3_client.upload_fileobj(response.raw, S3_BUCKET, names3, ExtraArgs={"ContentType": "video/mp4"})

  # Construct and return the S3 URL
  s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{names3}"
  print(f"Upload complete: {s3_url}")
  return s3_url


def encode_image(image_path):
  with open(image_path, "rb") as img_file:
    return "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')

def generate_hooks(client, prompt, files_array): #add the demo video portion later

  final_hooks = []
    #need an array of files
  for file in files_array:
    image_path = os.path.join('stockimages', file)
    encoded_image = encode_image(image_path)
    task = client.image_to_video.create(
      model='gen3a_turbo',
      prompt_image=encoded_image,
      prompt_text=prompt,
    )
    print(task.id)
    task_id = task.id 

    time.sleep(10)  # Wait for a second before polling
    task = client.tasks.retrieve(task_id)
    while task.status not in ['SUCCEEDED', 'FAILED']:
      time.sleep(10)  # Wait for ten seconds before polling
      task = client.tasks.retrieve(task_id)

    #print(task)

    if task.status == 'SUCCEEDED':
      url = task.output[0]
      s3_url = grab_video(url, file)
      if s3_url:
        final_hooks.append(s3_url)
    else:
      print()

  return final_hooks