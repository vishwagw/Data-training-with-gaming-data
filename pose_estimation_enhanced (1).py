import webview
import os
import json
import base64
from pathlib import Path
import threading
import time

# HTML/CSS/JS for the web interface
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaming Pose Estimator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .windows-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .window {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .window-title {
            font-size: 1.3em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9ff;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        
        .upload-area.drag-over {
            border-color: #764ba2;
            background: #e8ebff;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 4em;
            margin-bottom: 15px;
        }
        
        .upload-text {
            font-size: 1.1em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .file-input {
            display: none;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .video-preview {
            margin-top: 20px;
            display: none;
        }
        
        .video-preview video {
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .video-info {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9ff;
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        .video-info p {
            margin: 5px 0;
            color: #666;
        }
        
        .detection-display {
            min-height: 350px;
            background: #f8f9ff;
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .detection-canvas {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: none;
            background: #000;
        }
        
        .processing-indicator {
            text-align: center;
            display: none;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status-message {
            margin-top: 15px;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.9em;
            display: none;
        }
        
        .status-message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-message.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .controls {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .empty-state {
            color: #999;
            font-size: 1em;
            text-align: center;
        }
        
        .keypoint-legend {
            margin-top: 15px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            font-size: 0.85em;
            display: none;
        }
        
        .legend-item {
            display: inline-block;
            margin: 5px 10px;
        }
        
        .legend-color {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .frame-info {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 0.85em;
            display: none;
        }
        
        @media (max-width: 1400px) {
            .windows-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Gaming Video Pose Estimator</h1>
            <p>Extract and visualize character movements and poses from gaming footage</p>
        </div>
        
        <div class="windows-container">
            <!-- Video Upload Window -->
            <div class="window">
                <h2 class="window-title">📹 Video Input</h2>
                
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">🎬</div>
                    <p class="upload-text">Drag & drop your gaming video here</p>
                    <p class="upload-text">or</p>
                    <button class="btn" onclick="document.getElementById('fileInput').click()">
                        Browse Files
                    </button>
                    <input type="file" id="fileInput" class="file-input" accept="video/*">
                </div>
                
                <div class="video-preview" id="videoPreview">
                    <video id="videoPlayer" controls></video>
                    <div class="video-info" id="videoInfo"></div>
                </div>
                
                <div class="controls">
                    <button class="btn" id="processBtn" disabled onclick="processVideo()">
                        🚀 Extract Poses
                    </button>
                    <button class="btn" id="resetBtn" style="background: #6c757d;" onclick="resetAll()">
                        🔄 Reset
                    </button>
                </div>
                
                <div class="status-message" id="statusMessage"></div>
            </div>
            
            <!-- Pose Overlay Detection Window -->
            <div class="window">
                <h2 class="window-title">👤 Pose Detection (Video Overlay)</h2>
                
                <div class="detection-display" id="overlayDisplay">
                    <div class="empty-state">
                        <p>Pose detection will appear here</p>
                        <p style="font-size: 0.9em; margin-top: 10px;">Shows detected pose overlaid on video frame</p>
                    </div>
                    <div class="processing-indicator" id="overlayProcessing">
                        <div class="spinner"></div>
                        <p>Processing video frames...</p>
                    </div>
                    <div class="frame-info" id="overlayFrameInfo">Frame: 0/0</div>
                    <canvas id="overlayCanvas" class="detection-canvas"></canvas>
                </div>
                
                <div class="keypoint-legend" id="overlayLegend">
                    <strong>Keypoints:</strong>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #ff0000;"></span>
                        Head
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #00ff00;"></span>
                        Torso
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #0000ff;"></span>
                        Arms
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #ffff00;"></span>
                        Legs
                    </div>
                </div>
            </div>
            
            <!-- Skeleton Extraction Window -->
            <div class="window">
                <h2 class="window-title">🦴 Skeleton Extraction (Keypoints Only)</h2>
                
                <div class="detection-display" id="skeletonDisplay">
                    <div class="empty-state">
                        <p>Extracted skeleton will appear here</p>
                        <p style="font-size: 0.9em; margin-top: 10px;">Shows only the pose keypoints and connections</p>
                    </div>
                    <div class="processing-indicator" id="skeletonProcessing">
                        <div class="spinner"></div>
                        <p>Extracting skeleton...</p>
                    </div>
                    <div class="frame-info" id="skeletonFrameInfo">Frame: 0/0</div>
                    <canvas id="skeletonCanvas" class="detection-canvas"></canvas>
                </div>
                
                <div class="keypoint-legend" id="skeletonLegend" style="display: none;">
                    <strong>Confidence:</strong>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #00ff00;"></span>
                        High (&gt;0.8)
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #ffaa00;"></span>
                        Medium (0.5-0.8)
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #ff0000;"></span>
                        Low (&lt;0.5)
                    </div>
                </div>
            </div>
            
            <!-- Analysis Summary Window -->
            <div class="window">
                <h2 class="window-title">📊 Analysis Summary</h2>
                
                <div class="detection-display" id="summaryDisplay" style="min-height: 350px;">
                    <div class="empty-state">
                        <p>Pose analysis data will appear here</p>
                        <p style="font-size: 0.9em; margin-top: 10px;">Statistics and detected movements</p>
                    </div>
                    <div id="summaryContent" style="width: 100%; display: none; text-align: left;">
                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <h3 style="color: #667eea; margin-bottom: 10px;">Detection Statistics</h3>
                            <div id="statsContent"></div>
                        </div>
                        <div style="background: white; padding: 15px; border-radius: 8px;">
                            <h3 style="color: #667eea; margin-bottom: 10px;">Detected Keypoints</h3>
                            <div id="keypointsContent" style="max-height: 200px; overflow-y: auto; font-size: 0.9em;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentVideoFile = null;
        let currentPoseData = null;
        let animationFrameId = null;
        let currentFrame = 0;
        
        // Drag and drop functionality
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('drag-over');
            }, false);
        });
        
        uploadArea.addEventListener('drop', handleDrop, false);
        fileInput.addEventListener('change', handleFileSelect, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        }
        
        function handleFileSelect(e) {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        }
        
        function handleFile(file) {
            if (!file.type.startsWith('video/')) {
                showStatus('Please select a valid video file', 'error');
                return;
            }
            
            currentVideoFile = file;
            const videoPlayer = document.getElementById('videoPlayer');
            const videoPreview = document.getElementById('videoPreview');
            const videoInfo = document.getElementById('videoInfo');
            const processBtn = document.getElementById('processBtn');
            
            const url = URL.createObjectURL(file);
            videoPlayer.src = url;
            videoPreview.style.display = 'block';
            
            videoPlayer.addEventListener('loadedmetadata', () => {
                const duration = Math.round(videoPlayer.duration);
                const size = (file.size / (1024 * 1024)).toFixed(2);
                
                videoInfo.innerHTML = `
                    <p><strong>Filename:</strong> ${file.name}</p>
                    <p><strong>Duration:</strong> ${duration} seconds</p>
                    <p><strong>Size:</strong> ${size} MB</p>
                    <p><strong>Resolution:</strong> ${videoPlayer.videoWidth}x${videoPlayer.videoHeight}</p>
                `;
            });
            
            processBtn.disabled = false;
            showStatus('Video loaded successfully! Click "Extract Poses" to begin.', 'success');
        }
        
        async function processVideo() {
            if (!currentVideoFile) {
                showStatus('Please select a video first', 'error');
                return;
            }
            
            const overlayProcessing = document.getElementById('overlayProcessing');
            const skeletonProcessing = document.getElementById('skeletonProcessing');
            const processBtn = document.getElementById('processBtn');
            
            // Hide empty states
            document.querySelectorAll('.empty-state').forEach(el => el.style.display = 'none');
            
            // Show processing indicators
            overlayProcessing.style.display = 'block';
            skeletonProcessing.style.display = 'block';
            processBtn.disabled = true;
            
            showStatus('Processing video and extracting poses...', 'info');
            
            try {
                const result = await pywebview.api.process_video(currentVideoFile.name);
                
                if (result.success) {
                    currentPoseData = result;
                    displayPoseResults(result);
                    showStatus('Pose extraction completed successfully!', 'success');
                } else {
                    throw new Error(result.error || 'Processing failed');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                console.error('Processing error:', error);
            } finally {
                overlayProcessing.style.display = 'none';
                skeletonProcessing.style.display = 'none';
                processBtn.disabled = false;
            }
        }
        
        function displayPoseResults(result) {
            // Show canvases and legends
            document.getElementById('overlayCanvas').style.display = 'block';
            document.getElementById('skeletonCanvas').style.display = 'block';
            document.getElementById('overlayLegend').style.display = 'block';
            document.getElementById('skeletonLegend').style.display = 'block';
            document.getElementById('overlayFrameInfo').style.display = 'block';
            document.getElementById('skeletonFrameInfo').style.display = 'block';
            
            // Draw overlay detection (pose on video frame)
            drawPoseOverlay(result);
            
            // Draw skeleton extraction (keypoints only)
            drawSkeletonOnly(result);
            
            // Display summary
            displaySummary(result);
            
            // Animate through frames
            animateDetection(result);
        }
        
        function drawPoseOverlay(result) {
            const canvas = document.getElementById('overlayCanvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = 640;
            canvas.height = 480;
            
            // Simulate video frame background
            const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            gradient.addColorStop(0, '#1a1a2e');
            gradient.addColorStop(1, '#16213e');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Add grid pattern to simulate video
            ctx.strokeStyle = 'rgba(255,255,255,0.05)';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 40) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }
            for (let i = 0; i < canvas.height; i += 40) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }
            
            // Draw pose overlay
            drawPoseKeypoints(ctx, result.pose_data, true);
        }
        
        function drawSkeletonOnly(result) {
            const canvas = document.getElementById('skeletonCanvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = 640;
            canvas.height = 480;
            
            // Clean white background
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Add subtle grid
            ctx.strokeStyle = 'rgba(102,126,234,0.1)';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 50) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }
            for (let i = 0; i < canvas.height; i += 50) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }
            
            // Draw skeleton only
            drawPoseKeypoints(ctx, result.pose_data, false);
        }
        
        function drawPoseKeypoints(ctx, poseData, isOverlay) {
            const keypoints = poseData.keypoints;
            const connections = poseData.skeleton_connections;
            
            // Draw connections first
            ctx.lineWidth = 3;
            connections.forEach(([start, end]) => {
                const startPoint = keypoints.find(kp => kp.name === start);
                const endPoint = keypoints.find(kp => kp.name === end);
                
                if (startPoint && endPoint) {
                    ctx.strokeStyle = isOverlay ? 'rgba(102,126,234,0.8)' : '#667eea';
                    ctx.beginPath();
                    ctx.moveTo(startPoint.x, startPoint.y);
                    ctx.lineTo(endPoint.x, endPoint.y);
                    ctx.stroke();
                }
            });
            
            // Draw keypoints
            keypoints.forEach(kp => {
                // Color based on confidence
                let color;
                if (kp.confidence > 0.8) {
                    color = '#00ff00';
                } else if (kp.confidence > 0.5) {
                    color = '#ffaa00';
                } else {
                    color = '#ff0000';
                }
                
                // Outer circle (glow effect for overlay)
                if (isOverlay) {
                    ctx.fillStyle = color + '40';
                    ctx.beginPath();
                    ctx.arc(kp.x, kp.y, 12, 0, 2 * Math.PI);
                    ctx.fill();
                }
                
                // Inner circle
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(kp.x, kp.y, 6, 0, 2 * Math.PI);
                ctx.fill();
                
                // Label
                ctx.fillStyle = isOverlay ? 'white' : '#333';
                ctx.font = '10px Arial';
                ctx.fillText(kp.name.replace('_', ' '), kp.x + 10, kp.y - 10);
            });
        }
        
        function displaySummary(result) {
            const summaryContent = document.getElementById('summaryContent');
            const statsContent = document.getElementById('statsContent');
            const keypointsContent = document.getElementById('keypointsContent');
            
            document.querySelector('#summaryDisplay .empty-state').style.display = 'none';
            summaryContent.style.display = 'block';
            
            // Statistics
            const avgConfidence = (result.pose_data.keypoints.reduce((sum, kp) => sum + kp.confidence, 0) / 
                                  result.pose_data.keypoints.length * 100).toFixed(1);
            
            statsContent.innerHTML = `
                <p><strong>Frames Processed:</strong> ${result.frames_processed}</p>
                <p><strong>Keypoints Detected:</strong> ${result.pose_data.keypoints.length}</p>
                <p><strong>Average Confidence:</strong> ${avgConfidence}%</p>
                <p><strong>Skeleton Connections:</strong> ${result.pose_data.skeleton_connections.length}</p>
            `;
            
            // Keypoints list
            let keypointsHTML = '<table style="width: 100%; border-collapse: collapse;">';
            keypointsHTML += '<tr style="background: #f8f9ff;"><th style="padding: 5px; text-align: left;">Keypoint</th><th style="padding: 5px;">Position</th><th style="padding: 5px;">Confidence</th></tr>';
            
            result.pose_data.keypoints.forEach(kp => {
                const confidenceColor = kp.confidence > 0.8 ? '#00aa00' : kp.confidence > 0.5 ? '#ff8800' : '#cc0000';
                keypointsHTML += `
                    <tr>
                        <td style="padding: 5px;">${kp.name.replace('_', ' ')}</td>
                        <td style="padding: 5px; text-align: center;">(${kp.x}, ${kp.y})</td>
                        <td style="padding: 5px; text-align: center; color: ${confidenceColor}; font-weight: bold;">
                            ${(kp.confidence * 100).toFixed(0)}%
                        </td>
                    </tr>
                `;
            });
            
            keypointsHTML += '</table>';
            keypointsContent.innerHTML = keypointsHTML;
        }
        
        function animateDetection(result) {
            // Simple animation to simulate frame-by-frame detection
            let frame = 0;
            const totalFrames = result.frames_processed;
            
            const animate = () => {
                frame = (frame + 1) % totalFrames;
                
                document.getElementById('overlayFrameInfo').textContent = `Frame: ${frame}/${totalFrames}`;
                document.getElementById('skeletonFrameInfo').textContent = `Frame: ${frame}/${totalFrames}`;
                
                animationFrameId = setTimeout(animate, 100);
            };
            
            animate();
        }
        
        function showStatus(message, type) {
            const statusMessage = document.getElementById('statusMessage');
            statusMessage.textContent = message;
            statusMessage.className = `status-message ${type}`;
            statusMessage.style.display = 'block';
            
            if (type === 'success' || type === 'error') {
                setTimeout(() => {
                    statusMessage.style.display = 'none';
                }, 5000);
            }
        }
        
        function resetAll() {
            currentVideoFile = null;
            currentPoseData = null;
            
            if (animationFrameId) {
                clearTimeout(animationFrameId);
            }
            
            document.getElementById('videoPreview').style.display = 'none';
            document.getElementById('videoPlayer').src = '';
            document.getElementById('processBtn').disabled = true;
            
            document.getElementById('overlayCanvas').style.display = 'none';
            document.getElementById('skeletonCanvas').style.display = 'none';
            document.getElementById('overlayLegend').style.display = 'none';
            document.getElementById('skeletonLegend').style.display = 'none';
            document.getElementById('overlayFrameInfo').style.display = 'none';
            document.getElementById('skeletonFrameInfo').style.display = 'none';
            document.getElementById('summaryContent').style.display = 'none';
            
            document.querySelectorAll('.empty-state').forEach(el => el.style.display = 'block');
            
            document.getElementById('statusMessage').style.display = 'none';
            
            fileInput.value = '';
        }
    </script>
</body>
</html>
"""


class API:
    """Backend API for the pose estimation application"""
    
    def __init__(self):
        self.video_path = None
        
    def process_video(self, filename):
        """
        Process video and extract poses
        In a real implementation, this would use MediaPipe or OpenPose
        """
        try:
            # Simulate processing
            time.sleep(2)
            
            # Mock pose data with realistic human pose keypoints
            pose_data = {
                "keypoints": [
                    {"name": "nose", "x": 320, "y": 140, "confidence": 0.95},
                    {"name": "left_eye", "x": 310, "y": 130, "confidence": 0.93},
                    {"name": "right_eye", "x": 330, "y": 130, "confidence": 0.94},
                    {"name": "left_ear", "x": 300, "y": 135, "confidence": 0.89},
                    {"name": "right_ear", "x": 340, "y": 135, "confidence": 0.90},
                    {"name": "left_shoulder", "x": 280, "y": 200, "confidence": 0.92},
                    {"name": "right_shoulder", "x": 360, "y": 200, "confidence": 0.91},
                    {"name": "left_elbow", "x": 260, "y": 260, "confidence": 0.88},
                    {"name": "right_elbow", "x": 380, "y": 260, "confidence": 0.87},
                    {"name": "left_wrist", "x": 250, "y": 310, "confidence": 0.85},
                    {"name": "right_wrist", "x": 390, "y": 310, "confidence": 0.84},
                    {"name": "left_hip", "x": 290, "y": 310, "confidence": 0.90},
                    {"name": "right_hip", "x": 350, "y": 310, "confidence": 0.89},
                    {"name": "left_knee", "x": 285, "y": 380, "confidence": 0.86},
                    {"name": "right_knee", "x": 355, "y": 380, "confidence": 0.85},
                    {"name": "left_ankle", "x": 280, "y": 440, "confidence": 0.83},
                    {"name": "right_ankle", "x": 360, "y": 440, "confidence": 0.82},
                ],
                "skeleton_connections": [
                    # Head connections
                    ["nose", "left_eye"],
                    ["nose", "right_eye"],
                    ["left_eye", "left_ear"],
                    ["right_eye", "right_ear"],
                    # Upper body
                    ["nose", "left_shoulder"],
                    ["nose", "right_shoulder"],
                    ["left_shoulder", "right_shoulder"],
                    ["left_shoulder", "left_elbow"],
                    ["right_shoulder", "right_elbow"],
                    ["left_elbow", "left_wrist"],
                    ["right_elbow", "right_wrist"],
                    # Torso
                    ["left_shoulder", "left_hip"],
                    ["right_shoulder", "right_hip"],
                    ["left_hip", "right_hip"],
                    # Lower body
                    ["left_hip", "left_knee"],
                    ["right_hip", "right_knee"],
                    ["left_knee", "left_ankle"],
                    ["right_knee", "right_ankle"]
                ]
            }
            
            return {
                "success": True,
                "frames_processed": 150,
                "pose_data": pose_data,
                "message": "Pose extraction completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_window():
    """Create and configure the webview window"""
    api = API()
    
    window = webview.create_window(
        'Gaming Pose Estimator',
        html=HTML_CONTENT,
        js_api=api,
        width=1600,
        height=1000,
        resizable=True,
        background_color='#667eea'
    )
    
    return window


if __name__ == '__main__':
    # Create the window
    window = create_window()
    
    # Start the application
    webview.start(debug=True)