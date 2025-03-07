from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from typing import List, Dict, Any
import uuid

app = Flask(__name__)
CORS(app)

@app.route("/api/generate-videos", methods=["POST"])
def generate_videos():
    # TODO: logic to create this route
    return 

if __name__ == "__main__":
    app.run(debug=True, port=5000) 