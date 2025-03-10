import boto3
import os
from pathlib import Path
import tempfile
from botocore.exceptions import ClientError

class AWSService:
    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.temp_dir = Path(tempfile.gettempdir()) / "video_downloads"
        self.temp_dir.mkdir(exist_ok=True)

    async def download_video(self, s3_key: str) -> str:
        """
        Download a video from S3 and return the local path
        """
        local_path = self.temp_dir / os.path.basename(s3_key)
        
        try:
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                str(local_path)
            )
            return str(local_path)
        except ClientError as e:
            raise Exception(f"Failed to download video from S3: {str(e)}")

    async def upload_video(self, local_path: str, s3_key: str) -> str:
        """
        Upload a video to S3 and return the S3 URL
        """
        try:
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key
            )
            
            # Generate a presigned URL that's valid for 1 hour
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to upload video to S3: {str(e)}")

    def cleanup_temp_files(self):
        """
        Clean up temporary downloaded files
        """
        for file in self.temp_dir.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass 