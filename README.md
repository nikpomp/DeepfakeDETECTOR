# Deepfake Detector

A web-based application that detects deepfake videos using computer vision and machine learning techniques.

## Features

- 🎥 Upload video files (MP4, AVI, MOV, MKV, WEBM)
- 🔍 Real-time deepfake detection analysis
- 📊 Detailed analysis results with confidence scores
- 🎨 Modern, user-friendly interface
- 📱 Responsive design

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload a video file and click "Analyze Video" to get results.

## How It Works

The detector analyzes videos by:
- Extracting frames from the video
- Detecting faces in each frame
- Analyzing color consistency, edge patterns, and symmetry
- Checking frame-to-frame consistency
- Calculating a deepfake probability score

## Technical Details

- **Backend**: Flask (Python)
- **Computer Vision**: OpenCV
- **Face Detection**: Haar Cascade Classifier
- **Analysis**: Heuristic-based detection with statistical analysis

## Note

This is a demonstration application. For production use, consider integrating more advanced deepfake detection models trained on large datasets.

## License

MIT License
