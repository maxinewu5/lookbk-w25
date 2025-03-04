 # pip install runwayml
from runwayml import RunwayML
from dotenv import load_dotenv
import time
import os
# The env var RUNWAYML_API_SECRET is expected to contain your API key.
load_dotenv()
RUNWAYML_API_KEY = os.getenv('RUNWAYML_API_KEY')
RUNWAYML_API_SECRET = RUNWAYML_API_KEY
client = RunwayML(api_key=RUNWAYML_API_SECRET)
# change this to env variable later


task = client.image_to_video.create(
  model='gen3a_turbo',
  prompt_image='https://www.humaneworld.org/sites/default/files/styles/responsive_3_4_500w/public/2019/03/rabbit-475261_0.jpg.webp?itok=ePhKmw_y',
  prompt_text='The bunny is eating a carrot',
)
#print(task.id)

task_id = task.id 

time.sleep(10)  # Wait for a second before polling
task = client.tasks.retrieve(task_id)
while task.status not in ['SUCCEEDED', 'FAILED']:
  time.sleep(10)  # Wait for ten seconds before polling
  task = client.tasks.retrieve(task_id)

#print('Task complete:', task)