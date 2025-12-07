import webview
import json
import base64
import os
from pathlib import Path

class RobotTrainingAPI:
    def __init__(self):
        self.videos = []
        self.training_data = []
        self.output_dir = Path("robot_training_data")
        self.output_dir.mkdir(exist_ok=True)
        
    def upload_video(self, file_data):
        """Handle video upload"""
        try:
            # Parse base64 data
            header, encoded = file_data.split(',', 1)
            video_bytes = base64.b64decode(encoded)
            
            # Save video
            video_id = len(self.videos)
            filename = f"video_{video_id}.mp4"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(video_bytes)
            
            video_info = {
                'id': video_id,
                'filename': filename,
                'path': str(filepath),
                'size': len(video_bytes),
                'status': 'uploaded'
            }
            self.videos.append(video_info)
            
            return {'success': True, 'video': video_info}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_video(self, video_id):
        """Process video to extract pose keypoints"""
        try:
            # Simulate pose estimation processing
            # In production, this would use MediaPipe, OpenPose, or similar
            import time
            time.sleep(2)  # Simulate processing
            
            video = next((v for v in self.videos if v['id'] == video_id), None)
            if not video:
                return {'success': False, 'error': 'Video not found'}
            
            # Generate sample keypoints data
            # Each frame has 17 keypoints (typical skeleton)
            keypoints_data = {
                'video_id': video_id,
                'frames': 150,  # Example frame count
                'fps': 30,
                'keypoints': self._generate_sample_keypoints(150)
            }
            
            # Save keypoints
            keypoints_file = self.output_dir / f"keypoints_{video_id}.json"
            with open(keypoints_file, 'w') as f:
                json.dump(keypoints_data, f)
            
            self.training_data.append(keypoints_data)
            video['status'] = 'processed'
            video['keypoints_file'] = str(keypoints_file)
            
            return {'success': True, 'data': keypoints_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_sample_keypoints(self, num_frames):
        """Generate sample keypoint data for demonstration"""
        import random
        
        keypoint_names = [
            'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
        ]
        
        frames = []
        for frame in range(num_frames):
            keypoints = {}
            for i, name in enumerate(keypoint_names):
                # Generate smooth movement
                t = frame / num_frames * 2 * 3.14159
                keypoints[name] = {
                    'x': 0.5 + 0.3 * (i / len(keypoint_names)) * random.uniform(0.8, 1.2),
                    'y': 0.5 + 0.2 * random.uniform(0.9, 1.1) + 0.1 * (i % 3),
                    'z': 0.5 + 0.1 * random.uniform(0.95, 1.05),
                    'confidence': random.uniform(0.85, 0.99)
                }
            frames.append(keypoints)
        
        return frames
    
    def get_videos(self):
        """Get list of uploaded videos"""
        return {'success': True, 'videos': self.videos}
    
    def get_training_data(self):
        """Get processed training data"""
        return {'success': True, 'data': self.training_data}
    
    def export_training_data(self, format_type):
        """Export training data in specified format"""
        try:
            if format_type == 'json':
                export_file = self.output_dir / 'training_data_export.json'
                with open(export_file, 'w') as f:
                    json.dump(self.training_data, f, indent=2)
            elif format_type == 'csv':
                export_file = self.output_dir / 'training_data_export.csv'
                # Convert to CSV format
                with open(export_file, 'w') as f:
                    f.write('frame,keypoint,x,y,z,confidence\n')
                    for data in self.training_data:
                        for frame_idx, frame in enumerate(data['keypoints']):
                            for kp_name, kp_data in frame.items():
                                f.write(f"{frame_idx},{kp_name},{kp_data['x']},{kp_data['y']},{kp_data['z']},{kp_data['confidence']}\n")
            
            return {'success': True, 'file': str(export_file)}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def create_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaming to Robot Training Data</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        h1 {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .subtitle {
            opacity: 0.9;
            font-size: 16px;
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 30px;
        }
        .panel {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            border: 2px solid #e9ecef;
        }
        .panel h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .upload-zone {
            border: 3px dashed #667eea;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
        }
        .upload-zone:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }
        .upload-zone input {
            display: none;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s;
            margin: 5px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .btn-secondary {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .video-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .video-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #e9ecef;
        }
        .video-info {
            flex: 1;
        }
        .video-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }
        .video-status {
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }
        .status-uploaded {
            background: #fff3cd;
            color: #856404;
        }
        .status-processed {
            background: #d4edda;
            color: #155724;
        }
        .status-processing {
            background: #d1ecf1;
            color: #0c5460;
        }
        .canvas-container {
            background: #1a1a2e;
            border-radius: 12px;
            height: 400px;
            position: relative;
            overflow: hidden;
        }
        canvas {
            width: 100%;
            height: 100%;
            display: block;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Gaming to Robot Training Data</h1>
            <p class="subtitle">Convert game character movements into humanoid robot training data</p>
        </header>
        
        <div class="main-content">
            <!-- Upload Section -->
            <div class="panel">
                <h2>📹 Video Upload & Processing</h2>
                <div class="upload-zone" id="uploadZone">
                    <input type="file" id="videoInput" accept="video/*" multiple>
                    <div style="font-size: 48px; margin-bottom: 15px;">📤</div>
                    <div style="font-size: 16px; font-weight: 600; color: #667eea; margin-bottom: 8px;">
                        Click to upload gaming videos
                    </div>
                    <div style="font-size: 14px; color: #666;">
                        Supports MP4, AVI, MOV formats
                    </div>
                </div>
                
                <div id="alertContainer"></div>
                
                <div style="margin-top: 20px;">
                    <h3 style="font-size: 16px; margin-bottom: 10px; color: #333;">Uploaded Videos</h3>
                    <div class="video-list" id="videoList">
                        <div style="text-align: center; color: #999; padding: 20px;">
                            No videos uploaded yet
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Statistics Section -->
            <div class="panel">
                <h2>📊 Training Data Statistics</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="statVideos">0</div>
                        <div class="stat-label">Videos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="statFrames">0</div>
                        <div class="stat-label">Frames</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="statKeypoints">0</div>
                        <div class="stat-label">Keypoints</div>
                    </div>
                </div>
                
                <div style="margin-top: 25px;">
                    <h3 style="font-size: 16px; margin-bottom: 15px; color: #333;">Export Training Data</h3>
                    <div class="controls">
                        <button class="btn btn-secondary" onclick="exportData('json')">
                            Export as JSON
                        </button>
                        <button class="btn btn-secondary" onclick="exportData('csv')">
                            Export as CSV
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Visualization Section -->
            <div class="panel full-width">
                <h2>🎮 Humanoid Robot Simulator</h2>
                <div class="canvas-container">
                    <canvas id="robotCanvas"></canvas>
                </div>
                <div class="controls">
                    <button class="btn" onclick="playAnimation()">▶ Play</button>
                    <button class="btn" onclick="pauseAnimation()">⏸ Pause</button>
                    <button class="btn" onclick="resetAnimation()">⏹ Reset</button>
                    <button class="btn btn-secondary" onclick="changeView()">🔄 Change View</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let videos = [];
        let trainingData = [];
        let animationFrame = 0;
        let isPlaying = false;
        let currentView = 0;
        let robot = null;
        
        // Initialize canvas
        const canvas = document.getElementById('robotCanvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            drawRobot();
        }
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Upload handling
        document.getElementById('uploadZone').addEventListener('click', () => {
            document.getElementById('videoInput').click();
        });
        
        document.getElementById('videoInput').addEventListener('change', async (e) => {
            const files = e.target.files;
            for (let file of files) {
                await uploadVideo(file);
            }
            e.target.value = '';
        });
        
        async function uploadVideo(file) {
            showAlert('Uploading ' + file.name + '...', 'info');
            
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const result = await pywebview.api.upload_video(e.target.result);
                    if (result.success) {
                        videos.push(result.video);
                        showAlert('Video uploaded successfully!', 'success');
                        updateVideoList();
                        updateStats();
                    } else {
                        showAlert('Upload failed: ' + result.error, 'error');
                    }
                } catch (error) {
                    showAlert('Upload error: ' + error, 'error');
                }
            };
            reader.readAsDataURL(file);
        }
        
        async function processVideo(videoId) {
            const video = videos.find(v => v.id === videoId);
            if (!video) return;
            
            video.status = 'processing';
            updateVideoList();
            showAlert('Processing video...', 'info');
            
            try {
                const result = await pywebview.api.process_video(videoId);
                if (result.success) {
                    video.status = 'processed';
                    trainingData.push(result.data);
                    showAlert('Video processed successfully!', 'success');
                    updateVideoList();
                    updateStats();
                    
                    // Initialize robot with first keypoints
                    if (trainingData.length === 1) {
                        initRobot(result.data);
                    }
                } else {
                    video.status = 'uploaded';
                    showAlert('Processing failed: ' + result.error, 'error');
                    updateVideoList();
                }
            } catch (error) {
                video.status = 'uploaded';
                showAlert('Processing error: ' + error, 'error');
                updateVideoList();
            }
        }
        
        function updateVideoList() {
            const list = document.getElementById('videoList');
            if (videos.length === 0) {
                list.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">No videos uploaded yet</div>';
                return;
            }
            
            list.innerHTML = videos.map(video => `
                <div class="video-item">
                    <div class="video-info">
                        <div class="video-name">${video.filename}</div>
                        <span class="video-status status-${video.status}">${video.status}</span>
                    </div>
                    <div>
                        ${video.status === 'uploaded' ? 
                            `<button class="btn" onclick="processVideo(${video.id})">Process</button>` :
                            video.status === 'processing' ?
                            `<button class="btn" disabled><span class="loading"></span></button>` :
                            `<span style="color: #28a745; font-weight: 600;">✓ Ready</span>`
                        }
                    </div>
                </div>
            `).join('');
        }
        
        function updateStats() {
            document.getElementById('statVideos').textContent = videos.length;
            const totalFrames = trainingData.reduce((sum, data) => sum + data.frames, 0);
            document.getElementById('statFrames').textContent = totalFrames;
            const totalKeypoints = totalFrames * 17; // 17 keypoints per frame
            document.getElementById('statKeypoints').textContent = totalKeypoints.toLocaleString();
        }
        
        function showAlert(message, type) {
            const container = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type === 'error' ? 'error' : 'success'}`;
            alert.textContent = message;
            container.innerHTML = '';
            container.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
        
        async function exportData(format) {
            try {
                const result = await pywebview.api.export_training_data(format);
                if (result.success) {
                    showAlert(`Data exported to: ${result.file}`, 'success');
                } else {
                    showAlert('Export failed: ' + result.error, 'error');
                }
            } catch (error) {
                showAlert('Export error: ' + error, 'error');
            }
        }
        
        // Robot visualization
        function initRobot(data) {
            robot = data;
            animationFrame = 0;
            drawRobot();
        }
        
        function drawRobot() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (!robot || !robot.keypoints || robot.keypoints.length === 0) {
                // Draw placeholder
                ctx.fillStyle = '#667eea';
                ctx.font = '20px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('Process a video to see robot animation', canvas.width / 2, canvas.height / 2);
                return;
            }
            
            const frame = robot.keypoints[animationFrame % robot.keypoints.length];
            const scale = Math.min(canvas.width, canvas.height) * 0.8;
            const offsetX = canvas.width / 2;
            const offsetY = canvas.height / 2;
            
            // Draw skeleton connections
            const connections = [
                ['nose', 'left_eye'], ['nose', 'right_eye'],
                ['left_eye', 'left_ear'], ['right_eye', 'right_ear'],
                ['nose', 'left_shoulder'], ['nose', 'right_shoulder'],
                ['left_shoulder', 'right_shoulder'],
                ['left_shoulder', 'left_elbow'], ['left_elbow', 'left_wrist'],
                ['right_shoulder', 'right_elbow'], ['right_elbow', 'right_wrist'],
                ['left_shoulder', 'left_hip'], ['right_shoulder', 'right_hip'],
                ['left_hip', 'right_hip'],
                ['left_hip', 'left_knee'], ['left_knee', 'left_ankle'],
                ['right_hip', 'right_knee'], ['right_knee', 'right_ankle']
            ];
            
            // Draw connections
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 4;
            connections.forEach(([start, end]) => {
                if (frame[start] && frame[end]) {
                    const startPos = frame[start];
                    const endPos = frame[end];
                    ctx.beginPath();
                    ctx.moveTo(
                        offsetX + (startPos.x - 0.5) * scale,
                        offsetY + (startPos.y - 0.5) * scale
                    );
                    ctx.lineTo(
                        offsetX + (endPos.x - 0.5) * scale,
                        offsetY + (endPos.y - 0.5) * scale
                    );
                    ctx.stroke();
                }
            });
            
            // Draw keypoints
            Object.entries(frame).forEach(([name, pos]) => {
                const x = offsetX + (pos.x - 0.5) * scale;
                const y = offsetY + (pos.y - 0.5) * scale;
                
                ctx.fillStyle = pos.confidence > 0.9 ? '#38ef7d' : '#ffd700';
                ctx.beginPath();
                ctx.arc(x, y, 6, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
            });
            
            // Draw frame info
            ctx.fillStyle = '#fff';
            ctx.font = '16px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(`Frame: ${animationFrame + 1}/${robot.keypoints.length}`, 20, 30);
        }
        
        function playAnimation() {
            if (!robot) return;
            isPlaying = true;
            animate();
        }
        
        function pauseAnimation() {
            isPlaying = false;
        }
        
        function resetAnimation() {
            animationFrame = 0;
            isPlaying = false;
            drawRobot();
        }
        
        function changeView() {
            currentView = (currentView + 1) % 3;
            drawRobot();
        }
        
        function animate() {
            if (!isPlaying) return;
            
            animationFrame = (animationFrame + 1) % robot.keypoints.length;
            drawRobot();
            
            setTimeout(() => {
                requestAnimationFrame(animate);
            }, 1000 / 30); // 30 FPS
        }
        
        // Initial draw
        drawRobot();
    </script>
</body>
</html>
    """


def main():
    api = RobotTrainingAPI()
    
    window = webview.create_window(
        'Gaming to Robot Training Data',
        html=create_html(),
        js_api=api,
        width=1400,
        height=900,
        resizable=True,
        background_color='#667eea'
    )
    
    webview.start()


if __name__ == '__main__':
    main()
