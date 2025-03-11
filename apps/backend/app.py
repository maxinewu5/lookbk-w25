from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from typing import List, Dict, Any
import uuid
from dotenv import load_dotenv
import os
from caption_generator import CaptionGenerator

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize caption generator
caption_generator = CaptionGenerator()

@app.route("/api/generate-videos", methods=["POST"])
def generate_videos():
    # TODO: logic to create this route
    return 

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