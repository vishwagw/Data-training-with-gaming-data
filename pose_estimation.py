import cv2
import mediapipe as mp
import numpy as np
import webview
import threading
import base64
from io import BytesIO
from PIL import Image

class PoseEstimationApp:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.video_path = None
        
    def process_frame(self, frame):
        """Process a single frame for pose estimation"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
            
            # Add angle calculations for key joints
            landmarks = results.pose_landmarks.landmark
            
            # Calculate elbow angle (example)
            shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW]
            wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
            
            angle = self.calculate_angle(
                [shoulder.x, shoulder.y],
                [elbow.x, elbow.y],
                [wrist.x, wrist.y]
            )
            
            # Display angle on frame
            h, w = frame.shape[:2]
            cv2.putText(frame, f'L Elbow: {int(angle)}°', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 255), 2)
        
        return frame
    
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def frame_to_base64(self, frame):
        """Convert frame to base64 for display in webview"""
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    
    def load_video(self, path):
        """Load video file"""
        self.video_path = path
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        return {"success": True, "message": "Video loaded successfully"}
    
    def load_webcam(self):
        """Load webcam"""
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        self.video_path = "webcam"
        return {"success": True, "message": "Webcam loaded successfully"}
    
    def start_processing(self):
        """Start video processing"""
        if not self.cap or not self.cap.isOpened():
            return {"success": False, "message": "No video source loaded"}
        
        self.is_running = True
        threading.Thread(target=self._process_loop, daemon=True).start()
        return {"success": True, "message": "Processing started"}
    
    def stop_processing(self):
        """Stop video processing"""
        self.is_running = False
        return {"success": True, "message": "Processing stopped"}
    
    def _process_loop(self):
        """Main processing loop"""
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                if self.video_path and self.video_path != "webcam":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            processed_frame = self.process_frame(frame)
            self.current_frame = self.frame_to_base64(processed_frame)
    
    def get_frame(self):
        """Get current processed frame"""
        return self.current_frame
    
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.pose.close()

# Global app instance
app = PoseEstimationApp()

# API class for webview
class Api:
    def load_video(self, path):
        return app.load_video(path)
    
    def load_webcam(self):
        return app.load_webcam()
    
    def start(self):
        return app.start_processing()
    
    def stop(self):
        return app.stop_processing()
    
    def get_frame(self):
        return app.get_frame()

# HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Pose Estimation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .video-container {
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            min-height: 480px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #videoFrame {
            max-width: 100%;
            max-height: 600px;
            display: block;
        }
        
        .placeholder {
            color: #888;
            font-size: 18px;
        }
        
        .status {
            margin-top: 15px;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .status.info {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .status.success {
            background: #e8f5e9;
            color: #388e3c;
        }
        
        .status.error {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .file-input {
            display: none;
        }
        
        .info-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .info-box h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .info-box ul {
            list-style: none;
            padding-left: 0;
        }
        
        .info-box li {
            padding: 5px 0;
            color: #555;
        }
        
        .info-box li:before {
            content: "✓ ";
            color: #667eea;
            font-weight: bold;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Gaming Pose Estimation</h1>
        <p class="subtitle">Real-time human pose detection for gaming videos</p>
        
        <div class="controls">
            <button class="btn-primary" onclick="loadWebcam()">📹 Use Webcam</button>
            <button class="btn-primary" onclick="document.getElementById('fileInput').click()">
                📁 Load Video
            </button>
            <button class="btn-secondary" onclick="startProcessing()">▶️ Start</button>
            <button class="btn-danger" onclick="stopProcessing()">⏹️ Stop</button>
            <input type="file" id="fileInput" class="file-input" accept="video/*" onchange="loadVideo(this)">
        </div>
        
        <div class="video-container">
            <img id="videoFrame" style="display: none;">
            <div id="placeholder" class="placeholder">Load a video or webcam to begin</div>
        </div>
        
        <div id="status" class="status info">Ready to process video</div>
        
        <div class="info-box">
            <h3>Features</h3>
            <ul>
                <li>Real-time pose detection using MediaPipe</li>
                <li>Joint angle calculations</li>
                <li>Support for video files and webcam</li>
                <li>Visual skeleton overlay</li>
                <li>Gaming motion analysis</li>
            </ul>
        </div>
    </div>
    
    <script>
        let updateInterval;
        
        function updateFrame() {
            pywebview.api.get_frame().then(frame => {
                if (frame) {
                    const img = document.getElementById('videoFrame');
                    const placeholder = document.getElementById('placeholder');
                    img.src = frame;
                    img.style.display = 'block';
                    placeholder.style.display = 'none';
                }
            });
        }
        
        function loadWebcam() {
            pywebview.api.load_webcam().then(result => {
                updateStatus(result.message, result.success ? 'success' : 'error');
            });
        }
        
        function loadVideo(input) {
            if (input.files && input.files[0]) {
                const file = input.files[0];
                pywebview.api.load_video(file.path).then(result => {
                    updateStatus(result.message, result.success ? 'success' : 'error');
                });
            }
        }
        
        function startProcessing() {
            pywebview.api.start().then(result => {
                if (result.success) {
                    updateStatus('Processing started - Detecting poses...', 'success');
                    if (!updateInterval) {
                        updateInterval = setInterval(updateFrame, 33); // ~30 FPS
                    }
                } else {
                    updateStatus(result.message, 'error');
                }
            });
        }
        
        function stopProcessing() {
            pywebview.api.stop().then(result => {
                updateStatus(result.message, 'info');
                if (updateInterval) {
                    clearInterval(updateInterval);
                    updateInterval = null;
                }
            });
        }
        
        function updateStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }
    </script>
</body>
</html>
"""

def main():
    api = Api()
    window = webview.create_window(
        'Gaming Pose Estimation',
        html=html_content,
        js_api=api,
        width=1200,
        height=900,
        resizable=True
    )
    
    def on_closing():
        app.cleanup()
    
    webview.start(on_closing)

if __name__ == '__main__':
    main()
