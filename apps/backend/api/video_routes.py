from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.video_service import VideoService
from services.video_pipeline_service import VideoPipelineService
import os

router = APIRouter()
video_service = VideoService()
video_pipeline = VideoPipelineService(
    aws_bucket=os.getenv("AWS_BUCKET_NAME", "your-bucket-name")
)

class GenerateVideoRequest(BaseModel):
    video_url: str
    prompt: str
    reaction_type: str
    demo_type: str

class CombineVideosRequest(BaseModel):
    hook_video_path: str
    demo_video_path: str
    output_filename: str

class AddCaptionsRequest(BaseModel):
    video_path: str
    captions: List[str]
    output_filename: str
    font_size: int = 70

class ProcessVideosRequest(BaseModel):
    hook_urls: List[str]
    demo_urls: List[str]
    video_type: str

@router.post("/generate-videos")
async def generate_videos(request: GenerateVideoRequest):
    try:
        result = await video_service.generate_reaction_video(
            request.video_url,
            request.reaction_type,
            request.demo_type,
            request.prompt
        )
        return {"options": [result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/combine-videos")
async def combine_videos(request: CombineVideosRequest):
    try:
        output_path = await video_service.combine_videos(
            request.hook_video_path,
            request.demo_video_path,
            request.output_filename
        )
        return {"url": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-captions")
async def add_captions(request: AddCaptionsRequest):
    try:
        output_path = await video_service.add_captions(
            request.video_path,
            request.captions,
            request.output_filename,
            request.font_size
        )
        return {"url": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-videos")
async def process_videos(request: ProcessVideosRequest):
    """
    Process videos through the complete pipeline:
    1. Download videos from AWS
    2. Generate AI captions
    3. Stitch videos together
    4. Add captions to videos
    5. Upload processed videos back to AWS
    """
    try:
        processed_videos = await video_pipeline.process_videos(
            hook_urls=request.hook_urls,
            demo_urls=request.demo_urls,
            video_type=request.video_type
        )
        return {"videos": processed_videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 