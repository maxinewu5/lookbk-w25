import os

folder_path = "stockimages"
files_array = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

output_folder = "outputvideos"


 # pip install runwayml
from runwayml import RunwayML
import time
from dotenv import load_dotenv

# The env var RUNWAYML_API_SECRET is expected to contain your API key.
load_dotenv()
RUNWAYML_API_KEY = os.getenv('RUNWAYML_API_KEY')
RUNWAYML_API_SECRET = RUNWAYML_API_KEY
client = RunwayML(api_key=RUNWAYML_API_SECRET)

import requests
#grabbing the streamed output to save it as a file
def grab_output(link):
  video_filename = os.path.join(output_folder, link.split("/")[-1].split("?")[0])

  if os.path.exists(video_filename):
    print(f"File already exists: {video_filename}, skipping download.")
    return  # Skip downloading if the file is already there

  response = requests.get(link, stream=True)
  if response.status_code == 200:
    with open(video_filename, "wb") as file:
      for chunk in response.iter_content(1024):
        file.write(chunk)
        print(f"Download complete: {video_filename}")
  else:
    print("Failed to download the video.")

#encoding each image because runwayml does not accept a local file path
import base64
def encode_image(image_path):
  with open(image_path, "rb") as img_file:
      return "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')

for file in files_array:
  image_path = os.path.join(folder_path, file)
  encoded_image = encode_image(image_path)
  task = client.image_to_video.create(
      model='gen3a_turbo',
      prompt_image=encoded_image,
      prompt_text='Person is happy and excited!',
  )
  print(task.id)
  

  task_id = task.id 

  time.sleep(10)  # Wait for a second before polling
  task = client.tasks.retrieve(task_id)
  while task.status not in ['SUCCEEDED', 'FAILED']:
      time.sleep(10)  # Wait for ten seconds before polling
      task = client.tasks.retrieve(task_id)

  print(task)

  if task.status == 'SUCCEEDED':
    url = task.output[0]
    grab_output(url)

  else:
    print("task failed")
    print(file)
  