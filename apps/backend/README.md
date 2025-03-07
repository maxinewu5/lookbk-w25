# Backend Server

This is the Flask backend server for the video generation and combination service.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the development server:
```bash
python app.py
```

The server will run on `http://localhost:5000`

## API Endpoints

### Generate Videos
`POST /api/generate-videos`


## Development

The server uses Flask with CORS enabled for development. Current implementation includes mock data and simulated processing times. Video processing functionality to be implemented. 