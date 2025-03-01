 # pip install runwayml
from runwayml import RunwayML

# The env var RUNWAYML_API_SECRET is expected to contain your API key.
client = RunwayML(api_key="key_c2d89faa4a5ca2f054884141e2f10d1586cd93679f13b3d5f1360aea89edf70ba30014136677bdf5f9c458d96704b0515a754d2fb72bce4b4dfd1275b8ca1c01key_c2d89faa4a5ca2f054884141e2f10d1586cd93679f13b3d5f1360aea89edf70ba30014136677bdf5f9c458d96704b0515a754d2fb72bce4b4dfd1275b8ca1c01")
# change this to env variable later


task = client.image_to_video.create(
  model='gen3a_turbo',
  prompt_image='https://www.humaneworld.org/sites/default/files/styles/responsive_3_4_500w/public/2019/03/rabbit-475261_0.jpg.webp?itok=ePhKmw_y',
  prompt_text='The bunny is eating a carrot',
)
print(task.id)