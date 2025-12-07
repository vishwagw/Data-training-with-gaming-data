import webview
import json
import os

# HTML content for the application
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robot Movement Analyzer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            height: 100vh;
        }
        
        .sidebar {
            width: 320px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        #canvas-container {
            flex: 1;
            position: relative;
        }
        
        .controls {
            background: rgba(0, 0, 0, 0.5);
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .section h3 {
            font-size: 16px;
            margin-bottom: 10px;
            color: #ffd700;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-row:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            font-size: 13px;
            opacity: 0.8;
        }
        
        .stat-value {
            font-weight: 600;
            color: #ffd700;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        input[type="range"] {
            width: 100%;
            margin: 10px 0;
        }
        
        .speed-control {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .speed-label {
            font-size: 13px;
            min-width: 80px;
        }
        
        #frame-info {
            flex: 1;
            text-align: center;
            font-size: 14px;
            font-weight: 600;
        }
        
        .joint-list {
            max-height: 200px;
            overflow-y: auto;
            font-size: 12px;
        }
        
        .joint-item {
            padding: 5px;
            margin: 3px 0;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .confidence-high { color: #4ade80; }
        .confidence-medium { color: #fbbf24; }
        .confidence-low { color: #f87171; }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>🤖 Robot Analyzer</h1>
            
            <div class="section">
                <h3>📊 Animation Info</h3>
                <div class="stat-row">
                    <span class="stat-label">Total Frames:</span>
                    <span class="stat-value" id="total-frames">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">FPS:</span>
                    <span class="stat-value" id="fps">30</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Duration:</span>
                    <span class="stat-value" id="duration">0s</span>
                </div>
            </div>
            
            <div class="section">
                <h3>🎯 Current Keypoints</h3>
                <div class="joint-list" id="joint-list">
                    <div class="joint-item">Loading...</div>
                </div>
            </div>
            
            <div class="section">
                <h3>📈 Movement Stats</h3>
                <div class="stat-row">
                    <span class="stat-label">Avg Confidence:</span>
                    <span class="stat-value" id="avg-confidence">0%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Total Distance:</span>
                    <span class="stat-value" id="total-distance">0</span>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div id="canvas-container"></div>
            
            <div class="controls">
                <button id="play-btn">▶️ Play</button>
                <button id="pause-btn" disabled>⏸️ Pause</button>
                <button id="reset-btn">🔄 Reset</button>
                
                <div id="frame-info">Frame: 0 / 0</div>
                
                <div class="speed-control">
                    <span class="speed-label">Speed: <span id="speed-value">1.0</span>x</span>
                    <input type="range" id="speed-slider" min="0.1" max="3" step="0.1" value="1">
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Keypoints data (will be injected)
        const KEYPOINTS_DATA = __KEYPOINTS_DATA__;
        
        // Three.js scene setup
        let scene, camera, renderer, skeleton, animationId;
        let isPlaying = false;
        let currentFrame = 0;
        let playbackSpeed = 1.0;
        
        const jointConnections = [
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
        
        function init() {
            const container = document.getElementById('canvas-container');
            
            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);
            
            // Camera
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0.5, 2);
            camera.lookAt(0, 0.5, 0);
            
            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);
            
            // Lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 10, 5);
            scene.add(directionalLight);
            
            // Grid
            const gridHelper = new THREE.GridHelper(5, 10, 0x444444, 0x222222);
            scene.add(gridHelper);
            
            // Create skeleton
            createSkeleton();
            
            // Update stats
            updateStats();
            
            // Event listeners
            document.getElementById('play-btn').addEventListener('click', play);
            document.getElementById('pause-btn').addEventListener('click', pause);
            document.getElementById('reset-btn').addEventListener('click', reset);
            document.getElementById('speed-slider').addEventListener('input', (e) => {
                playbackSpeed = parseFloat(e.target.value);
                document.getElementById('speed-value').textContent = playbackSpeed.toFixed(1);
            });
            
            window.addEventListener('resize', onWindowResize);
            
            // Start render loop
            animate();
            
            // Update first frame
            updateSkeleton(0);
        }
        
        function createSkeleton() {
            skeleton = new THREE.Group();
            
            // Create joints (spheres)
            const jointGeometry = new THREE.SphereGeometry(0.02, 16, 16);
            const jointMaterial = new THREE.MeshPhongMaterial({ color: 0xff6b6b });
            
            KEYPOINTS_DATA.keypoints[0] && Object.keys(KEYPOINTS_DATA.keypoints[0]).forEach(jointName => {
                const joint = new THREE.Mesh(jointGeometry, jointMaterial.clone());
                joint.name = jointName;
                skeleton.add(joint);
            });
            
            // Create bones (lines)
            jointConnections.forEach(([start, end]) => {
                const geometry = new THREE.BufferGeometry();
                const material = new THREE.LineBasicMaterial({ color: 0x4ecdc4, linewidth: 2 });
                const line = new THREE.Line(geometry, material);
                line.name = `bone_${start}_${end}`;
                skeleton.add(line);
            });
            
            scene.add(skeleton);
        }
        
        function updateSkeleton(frame) {
            if (!KEYPOINTS_DATA.keypoints[frame]) return;
            
            const keypoints = KEYPOINTS_DATA.keypoints[frame];
            
            // Update joint positions
            Object.keys(keypoints).forEach(jointName => {
                const joint = skeleton.getObjectByName(jointName);
                if (joint && keypoints[jointName]) {
                    const kp = keypoints[jointName];
                    joint.position.set(
                        (kp.x - 0.5) * 2,
                        (1 - kp.y) * 2 - 0.5,
                        (kp.z - 0.6) * 2
                    );
                    
                    // Color by confidence
                    const color = kp.confidence > 0.9 ? 0x4ade80 :
                                 kp.confidence > 0.7 ? 0xfbbf24 : 0xf87171;
                    joint.material.color.setHex(color);
                }
            });
            
            // Update bones
            jointConnections.forEach(([start, end]) => {
                const bone = skeleton.getObjectByName(`bone_${start}_${end}`);
                const startJoint = skeleton.getObjectByName(start);
                const endJoint = skeleton.getObjectByName(end);
                
                if (bone && startJoint && endJoint) {
                    const positions = new Float32Array([
                        startJoint.position.x, startJoint.position.y, startJoint.position.z,
                        endJoint.position.x, endJoint.position.y, endJoint.position.z
                    ]);
                    bone.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                }
            });
            
            // Update UI
            updateJointList(keypoints);
            document.getElementById('frame-info').textContent = 
                `Frame: ${frame + 1} / ${KEYPOINTS_DATA.keypoints.length}`;
        }
        
        function updateJointList(keypoints) {
            const listElement = document.getElementById('joint-list');
            let html = '';
            
            Object.keys(keypoints).forEach(name => {
                const kp = keypoints[name];
                const confClass = kp.confidence > 0.9 ? 'confidence-high' :
                                 kp.confidence > 0.7 ? 'confidence-medium' : 'confidence-low';
                html += `<div class="joint-item">
                    <strong>${name}:</strong> 
                    <span class="${confClass}">${(kp.confidence * 100).toFixed(1)}%</span>
                </div>`;
            });
            
            listElement.innerHTML = html;
        }
        
        function updateStats() {
            document.getElementById('total-frames').textContent = KEYPOINTS_DATA.keypoints.length;
            document.getElementById('fps').textContent = KEYPOINTS_DATA.fps;
            document.getElementById('duration').textContent = 
                (KEYPOINTS_DATA.keypoints.length / KEYPOINTS_DATA.fps).toFixed(1) + 's';
            
            // Calculate average confidence
            let totalConf = 0, count = 0;
            KEYPOINTS_DATA.keypoints.forEach(frame => {
                Object.values(frame).forEach(kp => {
                    totalConf += kp.confidence;
                    count++;
                });
            });
            document.getElementById('avg-confidence').textContent = 
                ((totalConf / count) * 100).toFixed(1) + '%';
        }
        
        function play() {
            isPlaying = true;
            document.getElementById('play-btn').disabled = true;
            document.getElementById('pause-btn').disabled = false;
        }
        
        function pause() {
            isPlaying = false;
            document.getElementById('play-btn').disabled = false;
            document.getElementById('pause-btn').disabled = true;
        }
        
        function reset() {
            currentFrame = 0;
            updateSkeleton(0);
            pause();
        }
        
        let lastTime = 0;
        function animate(time = 0) {
            animationId = requestAnimationFrame(animate);
            
            const deltaTime = time - lastTime;
            
            if (isPlaying && deltaTime > (1000 / (KEYPOINTS_DATA.fps * playbackSpeed))) {
                currentFrame = (currentFrame + 1) % KEYPOINTS_DATA.keypoints.length;
                updateSkeleton(currentFrame);
                lastTime = time;
            }
            
            // Rotate camera slightly for better view
            skeleton.rotation.y += 0.002;
            
            renderer.render(scene, camera);
        }
        
        function onWindowResize() {
            const container = document.getElementById('canvas-container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    </script>
</body>
</html>
"""

class API:
    def __init__(self):
        # Load keypoints data from the provided file
        self.keypoints_data = {
            "video_id": 1,
            "frames": 150,
            "fps": 30,
            "keypoints": []  # Will be loaded from file
        }
    
    def load_keypoints(self, filepath):
        """Load keypoints from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.keypoints_data = data
                return True
        except Exception as e:
            print(f"Error loading keypoints: {e}")
            return False

def create_app():
    """Create and configure the PyWebView application"""
    api = API()
    
    # Load keypoints data (you can modify the path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keypoints_file = os.path.join(script_dir, 'keypoints_1.json')
    
    # If file doesn't exist, use sample data
    if not os.path.exists(keypoints_file):
        print("Keypoints file not found, using sample data...")
        # Use the first few frames from your data as sample
        api.keypoints_data = {
            "video_id": 1,
            "frames": 150,
            "fps": 30,
            "keypoints": [
                {"nose": {"x": 0.5, "y": 0.7196, "z": 0.5993, "confidence": 0.9213}, 
                 "left_eye": {"x": 0.5168, "y": 0.8166, "z": 0.6040, "confidence": 0.9390}}
                # Add more sample data as needed
            ]
        }
    else:
        api.load_keypoints(keypoints_file)
    
    # Inject keypoints data into HTML
    html_with_data = HTML_CONTENT.replace(
        '__KEYPOINTS_DATA__',
        json.dumps(api.keypoints_data)
    )
    
    # Create window
    window = webview.create_window(
        'Robot Movement Analyzer',
        html=html_with_data,
        width=1400,
        height=900,
        resizable=True,
        background_color='#1a1a2e'
    )
    
    return window

if __name__ == '__main__':
    window = create_app()
    webview.start(debug=True)
