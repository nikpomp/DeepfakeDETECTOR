import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load a simple deepfake detection model
# For this demo, we'll use a combination of face detection and basic analysis
# In production, you'd use a trained deepfake detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_frames(video_path, num_frames=10):
    """Extract frames from video for analysis"""
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Sample frames evenly throughout the video
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    
    cap.release()
    return frames

def analyze_frame(frame):
    """Analyze a single frame for deepfake indicators"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        return None
    
    # Get the largest face
    largest_face = max(faces, key=lambda x: x[2] * x[3])
    x, y, w, h = largest_face
    
    # Extract face region
    face_roi = frame[y:y+h, x:x+w]
    
    # Basic analysis features
    # 1. Check for inconsistencies in face boundaries
    # 2. Analyze color consistency
    # 3. Check for artifacts
    
    # Convert to different color spaces for analysis
    hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)
    
    # Calculate statistics
    bgr_std = np.std(face_roi, axis=(0, 1))
    hsv_std = np.std(hsv, axis=(0, 1))
    lab_std = np.std(lab, axis=(0, 1))
    
    # Deepfake indicators (simplified heuristic approach)
    # Real faces typically have more consistent color distribution
    color_variance = np.mean(bgr_std) + np.mean(hsv_std) + np.mean(lab_std)
    
    # Edge detection to find artifacts
    edges = cv2.Canny(cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY), 50, 150)
    edge_density = np.sum(edges > 0) / (w * h)
    
    # Calculate face symmetry (real faces are more symmetric)
    left_half = face_roi[:, :w//2]
    right_half = cv2.flip(face_roi[:, w//2:], 1)
    if left_half.shape == right_half.shape:
        symmetry_diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))
    else:
        symmetry_diff = 1000
    
    return {
        'color_variance': float(color_variance),
        'edge_density': float(edge_density),
        'symmetry_diff': float(symmetry_diff),
        'face_size': float(w * h)
    }

def detect_deepfake(video_path):
    """Main deepfake detection function"""
    try:
        frames = extract_frames(video_path, num_frames=15)
        
        if len(frames) == 0:
            return {
                'is_deepfake': False,
                'confidence': 0.0,
                'error': 'Could not extract frames from video'
            }
        
        frame_analyses = []
        for frame in frames:
            analysis = analyze_frame(frame)
            if analysis:
                frame_analyses.append(analysis)
        
        if len(frame_analyses) == 0:
            return {
                'is_deepfake': False,
                'confidence': 0.0,
                'error': 'No faces detected in video'
            }
        
        # Aggregate analysis across frames
        avg_color_variance = np.mean([a['color_variance'] for a in frame_analyses])
        avg_edge_density = np.mean([a['edge_density'] for a in frame_analyses])
        avg_symmetry_diff = np.mean([a['symmetry_diff'] for a in frame_analyses])
        
        # Heuristic scoring (these thresholds are tuned for demonstration)
        # In production, use a trained model
        
        deepfake_score = 0.0
        
        # High color variance might indicate manipulation
        if avg_color_variance > 45:
            deepfake_score += 0.3
        
        # Unusual edge patterns
        if avg_edge_density > 0.15:
            deepfake_score += 0.2
        
        # Asymmetry (though this is less reliable)
        if avg_symmetry_diff > 30:
            deepfake_score += 0.1
        
        # Consistency check across frames (real videos are more consistent)
        color_variance_std = np.std([a['color_variance'] for a in frame_analyses])
        if color_variance_std > 10:
            deepfake_score += 0.2
        
        # Additional check: face size consistency
        face_sizes = [a['face_size'] for a in frame_analyses]
        face_size_variance = np.std(face_sizes) / np.mean(face_sizes) if np.mean(face_sizes) > 0 else 0
        if face_size_variance > 0.2:
            deepfake_score += 0.2
        
        # Normalize score
        deepfake_score = min(deepfake_score, 1.0)
        
        is_deepfake = deepfake_score > 0.5
        confidence = deepfake_score if is_deepfake else (1 - deepfake_score)
        
        return {
            'is_deepfake': bool(is_deepfake),
            'confidence': float(confidence),
            'score': float(deepfake_score),
            'frames_analyzed': len(frame_analyses),
            'details': {
                'color_variance': float(avg_color_variance),
                'edge_density': float(avg_edge_density),
                'symmetry': float(avg_symmetry_diff),
                'consistency': float(color_variance_std)
            }
        }
    
    except Exception as e:
        return {
            'is_deepfake': False,
            'confidence': 0.0,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv, webm'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Perform deepfake detection
        result = detect_deepfake(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
