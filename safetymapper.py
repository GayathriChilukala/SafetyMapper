from flask import Flask, render_template_string, request, jsonify
import googlemaps
from datetime import datetime, timedelta
import json
import uuid
from google.cloud import firestore
from google.cloud.exceptions import NotFound
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configuration
GOOGLE_MAPS_API_KEY = "your_api_key"
GOOGLE_CLOUD_PROJECT = "your_project"

# Real Gemini API key
GEMINI_API_KEY = "your_api_key"  # Real Gemini API key

# Initialize clients
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Initialize Gemini
try:
    if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini AI configured successfully")
    else:
        print("⚠️ Gemini API key not configured - using fallback responses")
except Exception as e:
    print(f"❌ Gemini setup failed: {e}")
    print("⚠️ Using fallback responses")

# Initialize Firestore client
try:
    import os
    os.environ['GOOGLE_CLOUD_PROJECT'] = GOOGLE_CLOUD_PROJECT
    db = firestore.Client(project=GOOGLE_CLOUD_PROJECT)
    print(f"✅ Connected to Google Firestore (Project: {GOOGLE_CLOUD_PROJECT})")
except Exception as e:
    print(f"❌ Failed to connect to Firestore: {e}")
    db = None

def log_step(message: str, details: dict = None):
    """Enhanced logging for SafetyMapper workflow"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if details:
        for key, value in details.items():
            print(f"  {key}: {value}")

class FirestoreIncidentManager:
    """Manage incidents in Google Firestore - Production Version"""
    
    def __init__(self):
        self.collection_name = 'incidents'
        self.db = db
    
    def store_incident(self, incident_data):
        """Store incident in Firestore"""
        try:
            if not self.db:
                log_step("❌ Firestore not available")
                return None
            
            incident_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            document_data = {
                'incident_id': incident_id,
                'type': incident_data['type'],
                'location': incident_data['location'],
                'latitude': incident_data['lat'],
                'longitude': incident_data['lng'],
                'description': incident_data['description'],
                'severity': incident_data['severity'],
                'created_at': current_time,
                'source': 'user_report',
                'status': 'active',
                'reporter_info': {
                    'ip_address': incident_data.get('ip_address', ''),
                    'user_agent': incident_data.get('user_agent', ''),
                    'report_time': current_time
                }
            }
            
            # Store in Firestore
            doc_ref = self.db.collection(self.collection_name).document(incident_id)
            doc_ref.set(document_data)
            
            log_step("✅ Incident stored in Firestore", {
                "incident_id": incident_id,
                "type": document_data['type'],
                "location": document_data['location']
            })
            
            return {
                'id': incident_id,
                'type': document_data['type'],
                'location': document_data['location'],
                'lat': document_data['latitude'],
                'lng': document_data['longitude'],
                'description': document_data['description'],
                'severity': document_data['severity'],
                'timestamp': 'Just now',
                'date': current_time.isoformat(),
                'source': 'user_report'
            }
            
        except Exception as e:
            log_step(f"❌ Failed to store incident in Firestore: {e}")
            return None
    
    def get_recent_incidents(self, limit=100, hours=24):
        """Get recent incidents from Firestore - Optimized Query"""
        try:
            if not self.db:
                log_step("❌ Firestore not available")
                return []
            
            # Simple query that works reliably
            incidents_ref = self.db.collection(self.collection_name)
            query = incidents_ref.where('status', '==', 'active').limit(limit * 2)
            
            docs = query.stream()
            incidents = []
            
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    
                    # Handle timestamp
                    created_at = data.get('created_at')
                    if created_at:
                        if hasattr(created_at, 'timestamp'):
                            incident_time = datetime.fromtimestamp(created_at.timestamp())
                        elif isinstance(created_at, datetime):
                            incident_time = created_at
                        else:
                            incident_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00')).replace(tzinfo=None)
                    else:
                        incident_time = datetime.utcnow()
                    
                    # Filter by time range
                    if incident_time >= time_threshold:
                        incident = {
                            'id': data.get('incident_id', doc.id),
                            'type': data.get('type', 'unknown'),
                            'location': data.get('location', 'Unknown'),
                            'lat': float(data.get('latitude', 0)),
                            'lng': float(data.get('longitude', 0)),
                            'description': data.get('description', ''),
                            'severity': data.get('severity', 'low'),
                            'timestamp': self.format_timestamp(incident_time),
                            'date': incident_time.isoformat(),
                            'source': data.get('source', 'unknown')
                        }
                        incidents.append(incident)
                        
                except Exception as e:
                    log_step(f"❌ Error processing document: {e}")
                    continue
            
            # Sort by most recent first
            incidents.sort(key=lambda x: x['date'], reverse=True)
            
            log_step(f"✅ Retrieved {len(incidents)} incidents from Firestore")
            return incidents[:limit]
            
        except Exception as e:
            log_step(f"❌ Failed to retrieve incidents from Firestore: {e}")
            return []
    
    def get_all_incidents(self):
        """Get all active incidents for route analysis"""
        try:
            if not self.db:
                return []
            
            incidents_ref = self.db.collection(self.collection_name)
            query = incidents_ref.where('status', '==', 'active').limit(1000)
            
            docs = query.stream()
            incidents = []
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    incident = {
                        'id': data.get('incident_id', doc.id),
                        'type': data.get('type'),
                        'location': data.get('location'),
                        'lat': data.get('latitude'),
                        'lng': data.get('longitude'),
                        'description': data.get('description'),
                        'severity': data.get('severity'),
                        'timestamp': self.format_timestamp(data.get('created_at')),
                        'date': data.get('created_at').isoformat() if data.get('created_at') else '',
                        'source': data.get('source', 'unknown')
                    }
                    incidents.append(incident)
                except Exception as e:
                    continue
            
            return incidents
            
        except Exception as e:
            log_step(f"❌ Failed to retrieve all incidents: {e}")
            return []
    
    def get_incidents_count(self):
        """Get total incident count"""
        try:
            if not self.db:
                return 0
            
            incidents_ref = self.db.collection(self.collection_name)
            query = incidents_ref.where('status', '==', 'active')
            docs = list(query.stream())
            return len(docs)
            
        except Exception as e:
            log_step(f"❌ Failed to get incident count: {e}")
            return 0
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        if not timestamp:
            return "Unknown"
        
        try:
            if isinstance(timestamp, datetime):
                dt = timestamp
            elif hasattr(timestamp, 'timestamp'):
                dt = datetime.fromtimestamp(timestamp.timestamp())
            else:
                dt = datetime.fromisoformat(str(timestamp))
            
            now = datetime.utcnow()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "Just now"
        except:
            return "Recently"

# Initialize Firestore manager
incident_manager = FirestoreIncidentManager()

def initialize_sample_data():
    """Initialize sample incidents if none exist"""
    try:
        existing_count = incident_manager.get_incidents_count()
        
        if existing_count == 0:
            log_step("📝 Adding sample incidents to Firestore...")
            
            sample_incidents = [
                {
                    "type": "theft",
                    "location": "Downtown Bethesda, MD",
                    "lat": 38.9847,
                    "lng": -77.0947,
                    "description": "Bike theft near metro station",
                    "severity": "medium"
                },
                {
                    "type": "suspicious",
                    "location": "Chevy Chase, MD",
                    "lat": 38.9686,
                    "lng": -77.0872,
                    "description": "Suspicious activity in parking garage",
                    "severity": "low"
                },
                {
                    "type": "vandalism",
                    "location": "Silver Spring, MD",
                    "lat": 38.9912,
                    "lng": -77.0261,
                    "description": "Graffiti on building wall",
                    "severity": "low"
                }
            ]
            
            for sample in sample_incidents:
                incident_manager.store_incident(sample)
            
            log_step("✅ Sample incidents added to Firestore")
        else:
            log_step(f"✅ Found {existing_count} existing incidents in Firestore")
            
    except Exception as e:
        log_step(f"❌ Error initializing sample data: {e}")

@app.route('/')
def home():
    log_step("🏠 SafetyMapper loaded")
    initialize_sample_data()
    
    # Get recent incidents from Firestore
    incidents = incident_manager.get_recent_incidents(limit=50, hours=24*7)  # 7 days for better coverage
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafetyMapper - Community Safety Platform</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡️</text></svg>">
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
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.5rem;
            font-weight: bold;
            color: #4a5568;
        }
        
        .logo-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;
        }
        
        .database-status {
            background: linear-gradient(45deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: #fff;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-secondary {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            border: 1px solid #667eea;
        }
        
        /* Floating Chat Button */
        .chat-fab {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #4CAF50 0%, #45a049 100%);
            border-radius: 50%;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4);
            z-index: 1500;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
            transition: all 0.3s ease;
            animation: pulse-chat 2s infinite;
        }
        
        .chat-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(76, 175, 80, 0.6);
        }
        
        .chat-fab.chat-open {
            background: linear-gradient(45deg, #f44336 0%, #d32f2f 100%);
            box-shadow: 0 4px 20px rgba(244, 67, 54, 0.4);
            animation: none;
        }
        
        @keyframes pulse-chat {
            0% { box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4); }
            50% { box-shadow: 0 4px 30px rgba(76, 175, 80, 0.7); }
            100% { box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4); }
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .chat-badge {
            background: #ff4444;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            top: -5px;
            right: -5px;
            display: none;
            animation: bounce 1s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        .main-container {
            margin-top: 80px;
            padding: 2rem;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 2rem;
            height: calc(100vh - 120px);
        }
        
        .map-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
            position: relative;
        }
        
        #map {
            width: 100%;
            height: 100%;
            min-height: 500px;
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            max-height: calc(100vh - 120px);
            overflow-y: auto;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .panel-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1rem;
            font-weight: 600;
            color: #4a5568;
        }
        
        .panel-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.9rem;
        }
        
        .report-icon { background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 100%); }
        .stats-icon { background: linear-gradient(45deg, #a8edea 0%, #fed6e3 100%); }
        .route-icon { background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%); }
        .ai-icon { background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #4a5568;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .incident-types {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .incident-type {
            padding: 0.5rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s ease;
            background: white;
        }
        
        .incident-type:hover {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
            transform: translateY(-1px);
        }
        
        .incident-type.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            transform: scale(1.02);
        }
        
        .recent-incidents {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .incident-item {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease;
            cursor: pointer;
        }
        
        .incident-item:hover {
            transform: translateX(4px);
            background: rgba(102, 126, 234, 0.1);
        }
        
        .incident-title {
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        
        .incident-details {
            font-size: 0.85rem;
            color: #718096;
        }
        
        .incident-source {
            font-size: 0.75rem;
            color: #4CAF50;
            font-weight: 500;
            margin-top: 0.25rem;
        }
        
        .map-controls {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 100;
            display: flex;
            gap: 10px;
        }
        
        .control-btn {
            background: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .control-btn:hover {
            background: #f7fafc;
            transform: translateY(-1px);
        }
        
        .control-btn.active {
            background: #667eea;
            color: white;
        }
        
        .control-btn.clear-btn {
            background: #dc2626;
            color: white;
            margin-left: 10px;
        }
        
        .control-btn.clear-btn:hover {
            background: #b91c1c;
        }
        
        .success-message {
            background: linear-gradient(45deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            animation: slideDown 0.3s ease;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .route-info {
            background: rgba(102, 126, 234, 0.1);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            border-left: 4px solid #667eea;
            display: none;
        }
        
        .legend {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255,255,255,0.9);
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 0.5rem;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }
        
        /* Chat Modal Styles */
        .chat-modal {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            z-index: 2000;
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: slideUpChat 0.3s ease;
        }
        
        @keyframes slideUpChat {
            from { 
                opacity: 0; 
                transform: translateY(30px) scale(0.9); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }
        
        .chat-modal.closing {
            animation: slideDownChat 0.3s ease;
        }
        
        @keyframes slideDownChat {
            from { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
            to { 
                opacity: 0; 
                transform: translateY(30px) scale(0.9); 
            }
        }
        
        .chat-header {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-title {
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .chat-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: background 0.2s ease;
        }
        
        .chat-close:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .chat-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 1rem;
        }
        
        .chat-messages {
            flex: 1;
            max-height: 300px;
            overflow-y: auto;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #e2e8f0;
        }
        
        .chat-message {
            margin-bottom: 0.75rem;
            padding: 0.75rem;
            border-radius: 12px;
            max-width: 85%;
            line-height: 1.4;
        }
        
        .chat-message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
            border-bottom-right-radius: 4px;
        }
        
        .chat-message.ai {
            background: white;
            color: #333;
            border: 1px solid #e2e8f0;
            margin-right: auto;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .chat-message.ai::before {
            content: "🤖 ";
            font-weight: bold;
        }
        
        .chat-input-container {
            display: flex;
            gap: 0.5rem;
        }
        
        .chat-input {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: border-color 0.3s ease;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .chat-send {
            padding: 0.75rem 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.3s ease;
        }
        
        .chat-send:hover {
            background: #5a67d8;
        }
        
        .chat-send:disabled {
            background: #a0aec0;
            cursor: not-allowed;
        }
        
        .ai-thinking {
            display: none;
            padding: 0.5rem;
            color: #666;
            font-style: italic;
            font-size: 0.9rem;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .main-container {
                padding: 1rem;
            }
            
            .chat-modal {
                width: calc(100vw - 20px);
                height: calc(100vh - 150px);
                bottom: 10px;
                right: 10px;
                border-radius: 12px;
            }
            
            .chat-fab {
                bottom: 20px;
                right: 20px;
                width: 55px;
                height: 55px;
                font-size: 22px;
            }
            
            .nav-buttons {
                flex-wrap: wrap;
                justify-content: center;
            }
        }
        
        @media (max-width: 480px) {
            .chat-modal {
                width: calc(100vw - 10px);
                height: calc(100vh - 120px);
                bottom: 5px;
                right: 5px;
                border-radius: 12px;
            }
            
            .chat-fab {
                bottom: 15px;
                right: 15px;
                width: 50px;
                height: 50px;
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <div class="logo-icon">🛡️</div>
                <span>SafetyMapper</span>
            </div>
            <div class="nav-buttons">
                
                <button class="btn btn-secondary" onclick="showAbout()">About</button>
                <button class="btn btn-primary" onclick="showHelp()">Help</button>
            </div>
        </div>
    </header>

    <!-- Floating Chat Button -->
    <button class="chat-fab" id="chatFab" onclick="toggleChat()">
        🤖
        <div class="chat-badge" id="chatBadge">1</div>
    </button>

    <!-- Chat Modal -->
    <div class="chat-modal" id="chatModal">
        <div class="chat-header">
            <div class="chat-title">
                🤖 AI Safety Assistant
            </div>
            <button class="chat-close" onclick="toggleChat()">✕</button>
        </div>
        <div class="chat-body">
            <div class="chat-messages" id="chatMessages">
                <div class="chat-message ai">
                    Hi! I'm your AI Safety Assistant powered by Google Gemini Pro. I can analyze your area's safety data and provide intelligent insights. Ask me about:
                    <br><br>
                    • "Is it safe to walk downtown at night?"
                    <br>• "What areas should I avoid?"
                    <br>• "Analyze the incident patterns in my area"
                    <br>• "How safe is my planned route?"
                    <br><br>
                    🤖 <strong>Now using real Gemini AI for intelligent responses!</strong>
                </div>
            </div>
            <div class="ai-thinking" id="aiThinking">🤖 Analyzing safety data...</div>
            <div class="chat-input-container">
                <input type="text" class="chat-input" id="chatInput" placeholder="Ask about safety in your area..." onkeypress="handleChatKeyPress(event)">
                <button class="chat-send" id="chatSend" onclick="sendChatMessage()">Send</button>
            </div>
        </div>
    </div>

    <div class="main-container">
        <div class="dashboard">
            <div class="map-container">
                <div class="map-controls">
                    <button class="control-btn active" id="incidentView" onclick="toggleView('incidents')">📍 Incidents</button>
                    <button class="control-btn" id="heatmapView" onclick="toggleView('heatmap')">🔥 Heatmap</button>
                    <button class="control-btn" id="safetyView" onclick="toggleView('safety')">🚔 Safety Resources</button>
                    <button class="control-btn" id="allView" onclick="toggleView('all')">🌟 All Data</button>
                    <button class="control-btn clear-btn" id="clearRoute" onclick="clearRoute()" style="display: none;">🧹 Clear Route</button>
                </div>
                <div id="map"></div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #dc2626;"></div>
                        <span>High Risk</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ea580c;"></div>
                        <span>Medium Risk</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #65a30d;"></div>
                        <span>Low Risk</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #1e40af;"></div>
                        <span>🚔 Police</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #dc2626;"></div>
                        <span>🏥 Hospitals</span>
                    </div>
                </div>
            </div>

            <div class="sidebar">
                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-icon report-icon">📝</div>
                        <span>Report Incident</span>
                    </div>
                    <form id="incidentForm">
                        <div class="form-group">
                            <label>Incident Type</label>
                            <div class="incident-types">
                                <div class="incident-type" data-type="theft">🔓 Theft</div>
                                <div class="incident-type" data-type="assault">⚠️ Assault</div>
                                <div class="incident-type" data-type="harassment">🚫 Harassment</div>
                                <div class="incident-type" data-type="vandalism">💥 Vandalism</div>
                                <div class="incident-type" data-type="suspicious">👀 Suspicious</div>
                                <div class="incident-type" data-type="other">❓ Other</div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="location">Location (Smart Search)</label>
                            <input type="text" id="location" class="form-control" placeholder="Start typing address...">
                        </div>
                        <div class="form-group">
                            <label for="description">Description</label>
                            <textarea id="description" class="form-control" rows="3" placeholder="Describe what happened..."></textarea>
                        </div>
                        <div class="form-group">
                            <label for="severity">Severity</label>
                            <select id="severity" class="form-control">
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%;">Save to Firestore</button>
                    </form>
                    <div id="successMessage" style="display: none;"></div>
                </div>

                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-icon stats-icon">📊</div>
                        <span>Recent Reports</span>
                    </div>
                    <div class="recent-incidents">
                        <div id="recentIncidentsList">
                            <!-- Populated by JavaScript -->
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-icon route-icon">🛤️</div>
                        <span>Route Planner</span>
                    </div>
                    <div class="form-group">
                        <label for="routeFrom">From</label>
                        <input type="text" id="routeFrom" class="form-control" placeholder="Your location">
                    </div>
                    <div class="form-group">
                        <label for="routeTo">To</label>
                        <input type="text" id="routeTo" class="form-control" placeholder="Destination">
                    </div>
                    <div class="form-group">
                        <label for="travelMode">Travel Mode</label>
                        <select id="travelMode" class="form-control">
                            <option value="DRIVING">🚗 Driving</option>
                            <option value="WALKING" selected>🚶 Walking</option>
                            <option value="TRANSIT">🚌 Public Transit</option>
                            <option value="BICYCLING">🚲 Bicycling</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" style="width: 100%;" onclick="planSafeRoute()">Plan Safe Route</button>
                    <div id="routeInfo" class="route-info">
                        <div style="font-weight: 500; margin-bottom: 0.5rem;">Route Safety Analysis</div>
                        <div style="font-size: 0.9rem; color: #718096;">
                            <div>🛡️ Safety Score: <span id="routeSafetyScore">N/A</span></div>
                            <div>⏱️ Duration: <span id="routeDuration">N/A</span></div>
                            <div>📏 Distance: <span id="routeDistance">N/A</span></div>
                            <div>🚗 Travel Mode: <span id="routeTravelMode">N/A</span></div>
                            <div>📍 Safe Points: <span id="safePoints">N/A</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let map;
        let markers = [];
        let safetyMarkers = [];
        let routePolylines = [];
        let heatmap;
        let directionsService;
        let directionsRenderer;
        let currentView = 'incidents';
        let selectedIncidentType = '';
        let selectedLocation = null;
        let autocompleteObjects = {};
        let currentRoute = null;
        let currentRouteSegments = null;
        let chatHistory = [];
        let isChatOpen = false;

        // Load incidents from Firestore
        const incidents = {{ incidents|tojson }};
        console.log(`🔥 Loaded ${incidents.length} incidents from Firestore`);

        function initMap() {
            console.log('🗺️ SafetyMapper with Firestore + AI initialized');
            
            try {
                map = new google.maps.Map(document.getElementById('map'), {
                    zoom: 11,
                    center: { lat: 38.9847, lng: -77.0947 },
                    styles: [
                        {
                            featureType: 'all',
                            elementType: 'geometry.fill',
                            stylers: [{ weight: '2.00' }]
                        },
                        {
                            featureType: 'all',
                            elementType: 'geometry.stroke',
                            stylers: [{ color: '#9c9c9c' }]
                        }
                    ]
                });

                directionsService = new google.maps.DirectionsService();
                directionsRenderer = new google.maps.DirectionsRenderer({
                    draggable: true
                });
                directionsRenderer.setMap(map);

                map.addListener('click', function(event) {
                    selectLocation(event.latLng);
                });

                map.addListener('idle', function() {
                    if (currentView === 'safety' || currentView === 'all') {
                        loadSafetyResources();
                    }
                });

                initializeAutocomplete();
                showIncidents();
                updateRecentIncidentsList();
                
                console.log('🎉 SafetyMapper with AI ready!')

            } catch (error) {
                console.error('❌ SafetyMapper initialization failed:', error);
            }
        }

        // Chat Functions
        function toggleChat() {
            const modal = document.getElementById('chatModal');
            const fab = document.getElementById('chatFab');
            const badge = document.getElementById('chatBadge');
            
            if (isChatOpen) {
                // Close chat
                modal.classList.add('closing');
                fab.classList.remove('chat-open');
                fab.innerHTML = '🤖<div class="chat-badge" id="chatBadge" style="display: none;">1</div>';
                setTimeout(() => {
                    modal.style.display = 'none';
                    modal.classList.remove('closing');
                }, 300);
                isChatOpen = false;
            } else {
                // Open chat
                modal.style.display = 'flex';
                fab.classList.add('chat-open');
                fab.innerHTML = '✕<div class="chat-badge" id="chatBadge" style="display: none;">1</div>';
                isChatOpen = true;
                // Hide notification badge when chat is opened
                badge.style.display = 'none';
                
                // Focus on input
                setTimeout(() => {
                    document.getElementById('chatInput').focus();
                }, 100);
            }
        }

        function handleChatKeyPress(event) {
            if (event.key === 'Enter') {
                sendChatMessage();
            }
        }

        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addChatMessage(message, 'user');
            input.value = '';
            
            // Disable input while processing
            const sendBtn = document.getElementById('chatSend');
            const aiThinking = document.getElementById('aiThinking');
            
            sendBtn.disabled = true;
            aiThinking.style.display = 'block';
            
            try {
                // Get AI response
                const response = await getAIResponse(message);
                
                // Add AI response to chat
                addChatMessage(response, 'ai');
                
            } catch (error) {
                console.error('AI response error:', error);
                addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
            } finally {
                sendBtn.disabled = false;
                aiThinking.style.display = 'none';
                
                // Scroll to bottom
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }

        function addChatMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            messageDiv.innerHTML = message;
            chatMessages.appendChild(messageDiv);
            
            // Store in chat history
            chatHistory.push({ message, sender, timestamp: new Date() });
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        async function getAIResponse(userMessage) {
            try {
                const response = await fetch('/api/ai-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message: userMessage
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    return data.response;
                } else {
                    console.error('AI API error:', data.error);
                    return "I'm having trouble right now. Please try again in a moment.";
                }
                
            } catch (error) {
                console.error('AI request failed:', error);
                return "I'm having trouble connecting. Please check your internet connection and try again.";
            }
        }

        function initializeAutocomplete() {
            const inputs = ['location', 'routeFrom', 'routeTo'];
            
            inputs.forEach(inputId => {
                try {
                    const input = document.getElementById(inputId);
                    if (input) {
                        const autocomplete = new google.maps.places.Autocomplete(input, {
                            componentRestrictions: {country: 'us'},
                            fields: ['place_id', 'formatted_address', 'geometry', 'name']
                        });
                        
                        autocompleteObjects[inputId] = autocomplete;
                        
                        autocomplete.addListener('place_changed', function() {
                            const place = autocomplete.getPlace();
                            if (place.geometry && inputId === 'location') {
                                selectedLocation = place.geometry.location;
                            }
                        });
                    }
                } catch (error) {
                    console.error(`❌ Failed to setup autocomplete for ${inputId}:`, error);
                }
            });
        }

        function selectLocation(latLng) {
            selectedLocation = latLng;
            
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ location: latLng }, function(results, status) {
                if (status === 'OK' && results[0]) {
                    document.getElementById('location').value = results[0].formatted_address;
                }
            });

            toggleView(currentView);
            
            const marker = new google.maps.Marker({
                position: latLng,
                map: map,
                icon: {
                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                        <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="16" cy="16" r="12" fill="#667eea" stroke="white" stroke-width="3"/>
                            <text x="16" y="20" text-anchor="middle" fill="white" font-size="14">📍</text>
                        </svg>
                    `),
                    scaledSize: new google.maps.Size(32, 32)
                },
                animation: google.maps.Animation.DROP
            });
            
            markers.push(marker);
        }

        async function loadSafetyResources() {
            const center = map.getCenter();
            const zoom = map.getZoom();
            
            if (zoom < 12) {
                clearSafetyMarkers();
                return;
            }
            
            try {
                const response = await fetch(`/api/safety-resources?lat=${center.lat()}&lng=${center.lng()}&zoom=${zoom}`);
                const data = await response.json();
                
                if (response.ok) {
                    clearSafetyMarkers();
                    displaySafetyResources(data.police_stations, data.hospitals);
                }
            } catch (error) {
                console.error('❌ Error loading safety resources:', error);
            }
        }

        function displaySafetyResources(policeStations, hospitals) {
            policeStations.forEach(station => {
                const marker = new google.maps.Marker({
                    position: { lat: station.lat, lng: station.lng },
                    map: map,
                    icon: {
                        url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
                            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="12" cy="12" r="10" fill="#1e40af" stroke="white" stroke-width="2"/>
                                <text x="12" y="16" text-anchor="middle" fill="white" font-size="10">🚔</text>
                            </svg>
                        `)}`,
                        scaledSize: new google.maps.Size(24, 24)
                    },
                    title: station.name,
                    zIndex: 1000
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 8px;">
                            <h4 style="margin: 0 0 4px 0; color: #1e40af;">🚔 ${station.name}</h4>
                            <p style="margin: 0; font-size: 0.9em; color: #666;">${station.address}</p>
                        </div>
                    `
                });

                marker.addListener('click', () => {
                    infoWindow.open(map, marker);
                });
                
                safetyMarkers.push(marker);
            });
            
            hospitals.forEach(hospital => {
                const marker = new google.maps.Marker({
                    position: { lat: hospital.lat, lng: hospital.lng },
                    map: map,
                    icon: {
                        url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
                            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="12" cy="12" r="10" fill="#dc2626" stroke="white" stroke-width="2"/>
                                <text x="12" y="16" text-anchor="middle" fill="white" font-size="10">🏥</text>
                            </svg>
                        `)}`,
                        scaledSize: new google.maps.Size(24, 24)
                    },
                    title: hospital.name,
                    zIndex: 1000
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 8px;">
                            <h4 style="margin: 0 0 4px 0; color: #dc2626;">🏥 ${hospital.name}</h4>
                            <p style="margin: 0; font-size: 0.9em; color: #666;">${hospital.address}</p>
                        </div>
                    `
                });

                marker.addListener('click', () => {
                    infoWindow.open(map, marker);
                });
                
                safetyMarkers.push(marker);
            });
        }

        function clearSafetyMarkers() {
            safetyMarkers.forEach(marker => marker.setMap(null));
            safetyMarkers = [];
        }

        function clearRoutePolylines() {
            routePolylines.forEach(polyline => polyline.setMap(null));
            routePolylines = [];
        }

        function clearMarkers() {
            markers.forEach(marker => marker.setMap(null));
            markers = [];
            if (heatmap) {
                heatmap.setMap(null);
                heatmap = null;
            }
        }

        function showIncidents() {
            clearMarkers();
            
            console.log(`📍 Displaying ${incidents.length} incidents from Firestore`);
            
            incidents.forEach(incident => {
                const color = getSeverityColor(incident.severity);
                const icon = getIncidentIcon(incident.type);
                
                const marker = new google.maps.Marker({
                    position: { lat: incident.lat, lng: incident.lng },
                    map: map,
                    icon: {
                        url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
                            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="12" cy="12" r="10" fill="${color}" stroke="white" stroke-width="2"/>
                                <text x="12" y="16" text-anchor="middle" fill="white" font-size="12">${icon}</text>
                            </svg>
                        `)}`,
                        scaledSize: new google.maps.Size(24, 24)
                    }
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px; min-width: 200px;">
                            <h3 style="margin: 0 0 10px 0; color: #333;">${incident.type.charAt(0).toUpperCase() + incident.type.slice(1)}</h3>
                            <p style="margin: 5px 0; color: #666;">${incident.description}</p>
                            <p style="margin: 5px 0; font-size: 0.9em; color: #888;">
                                <strong>Location:</strong> ${incident.location}<br>
                                <strong>Severity:</strong> ${incident.severity}<br>
                                <strong>Time:</strong> ${incident.timestamp}<br>
                                <strong>Source:</strong> <span style="color: #4CAF50;">${incident.source}</span>
                            </p>
                        </div>
                    `
                });

                marker.addListener('click', () => {
                    infoWindow.open(map, marker);
                });
                
                markers.push(marker);
            });
        }

        function showHeatmap() {
            if (currentView !== 'all') {
                clearMarkers();
            }
            
            const heatmapData = incidents.map(incident => ({
                location: new google.maps.LatLng(incident.lat, incident.lng),
                weight: incident.severity === 'high' ? 3 : incident.severity === 'medium' ? 2 : 1
            }));

            heatmap = new google.maps.visualization.HeatmapLayer({
                data: heatmapData,
                dissipating: false,
                radius: 50
            });
            
            heatmap.setMap(map);
        }

        function getSeverityColor(severity) {
            switch(severity) {
                case 'high': return '#dc2626';
                case 'medium': return '#ea580c';
                case 'low': return '#65a30d';
                default: return '#6b7280';
            }
        }

        function getIncidentIcon(type) {
            switch(type) {
                case 'theft': return '🔓';
                case 'assault': return '⚠️';
                case 'harassment': return '🚫';
                case 'vandalism': return '💥';
                case 'suspicious': return '👀';
                default: return '❓';
            }
        }

        function toggleView(view) {
            currentView = view;
            
            document.querySelectorAll('.control-btn').forEach(btn => btn.classList.remove('active'));
            
            let buttonId;
            switch(view) {
                case 'incidents':
                    buttonId = 'incidentView';
                    break;
                case 'heatmap':
                    buttonId = 'heatmapView';
                    break;
                case 'safety':
                    buttonId = 'safetyView';
                    break;
                case 'all':
                    buttonId = 'allView';
                    break;
            }
            
            document.getElementById(buttonId).classList.add('active');
            
            clearMarkers();
            clearSafetyMarkers();
            clearRoutePolylines();
            
            switch(view) {
                case 'incidents':
                    showIncidents();
                    break;
                case 'heatmap':
                    showHeatmap();
                    break;
                case 'safety':
                    loadSafetyResources();
                    break;
                case 'all':
                    showIncidents();
                    showHeatmap();
                    loadSafetyResources();
                    break;
            }
            
            if (currentRoute && currentRouteSegments) {
                showRoute();
            }
        }

        function showRoute() {
            clearRoutePolylines();
            
            if (currentRouteSegments && currentRouteSegments.length > 0) {
                displayRouteWithIncidents(currentRouteSegments);
            }
        }

        function clearRoute() {
            currentRoute = null;
            currentRouteSegments = null;
            clearRoutePolylines();
            document.getElementById('routeInfo').style.display = 'none';
            document.getElementById('clearRoute').style.display = 'none';
            
            document.getElementById('routeFrom').value = '';
            document.getElementById('routeTo').value = '';
        }

        async function planSafeRoute() {
            const from = document.getElementById('routeFrom').value;
            const to = document.getElementById('routeTo').value;
            const travelMode = document.getElementById('travelMode').value;
            
            if (!from || !to) {
                alert('Please enter both start and end locations');
                return;
            }
            
            try {
                const response = await fetch('/api/route', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        origin: from, 
                        destination: to,
                        travel_mode: travelMode
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    currentRoute = data;
                    currentRouteSegments = data.route_segments;
                    
                    showRoute();
                    
                    document.getElementById('routeSafetyScore').textContent = data.safety_score;
                    document.getElementById('routeDuration').textContent = data.duration;
                    document.getElementById('routeDistance').textContent = data.distance;
                    document.getElementById('routeTravelMode').textContent = getTravelModeText(data.travel_mode);
                    document.getElementById('safePoints').textContent = data.safe_points;
                    document.getElementById('routeInfo').style.display = 'block';
                    
                    document.getElementById('clearRoute').style.display = 'block';
                    
                    console.log('✅ Route planned successfully and will persist across tabs');
                } else {
                    alert('Error planning route: ' + data.error);
                }
            } catch (error) {
                console.error('❌ Network error:', error);
                alert('Network error. Please try again.');
            }
        }

        function displayRouteWithIncidents(routeSegments) {
            routeSegments.forEach(segment => {
                const pathCoordinates = google.maps.geometry.encoding.decodePath(segment.encoded_path);
                
                let strokeColor, strokeWeight;
                
                switch(segment.safety_level) {
                    case 'high_risk':
                        strokeColor = '#dc2626';
                        strokeWeight = 8;
                        break;
                    case 'medium_risk':
                        strokeColor = '#ea580c';
                        strokeWeight = 6;
                        break;
                    case 'low_risk':
                        strokeColor = '#65a30d';
                        strokeWeight = 4;
                        break;
                    default:
                        strokeColor = '#2563eb';
                        strokeWeight = 4;
                }
                
                const routePolyline = new google.maps.Polyline({
                    path: pathCoordinates,
                    geodesic: true,
                    strokeColor: strokeColor,
                    strokeOpacity: 0.8,
                    strokeWeight: strokeWeight
                });
                
                routePolyline.setMap(map);
                routePolylines.push(routePolyline);
                
                routePolyline.addListener('click', (event) => {
                    const infoWindow = new google.maps.InfoWindow({
                        content: `
                            <div style="padding: 8px;">
                                <h4 style="margin: 0 0 5px 0;">Route Segment</h4>
                                <p style="margin: 2px 0; font-size: 0.9em;">
                                    <strong>Safety Level:</strong> ${segment.safety_level.replace('_', ' ').toUpperCase()}<br>
                                    <strong>Incidents Nearby:</strong> ${segment.incident_count}<br>
                                    <strong>Distance:</strong> ${segment.distance}
                                </p>
                            </div>
                        `,
                        position: event.latLng
                    });
                    infoWindow.open(map);
                });
            });
            
            if (routeSegments.length > 0) {
                const bounds = new google.maps.LatLngBounds();
                routeSegments.forEach(segment => {
                    const path = google.maps.geometry.encoding.decodePath(segment.encoded_path);
                    path.forEach(point => bounds.extend(point));
                });
                map.fitBounds(bounds);
            }
        }

        function getTravelModeText(mode) {
            const modeTexts = {
                'DRIVING': '🚗 Driving',
                'WALKING': '🚶 Walking',
                'TRANSIT': '🚌 Public Transit',
                'BICYCLING': '🚲 Bicycling'
            };
            return modeTexts[mode] || mode;
        }

        function updateRecentIncidentsList() {
            const recentList = document.getElementById('recentIncidentsList');
            recentList.innerHTML = incidents.slice(0, 5).map(incident => `
                <div class="incident-item" onclick="highlightIncident('${incident.id}')">
                    <div class="incident-title">${incident.type.charAt(0).toUpperCase() + incident.type.slice(1)}</div>
                    <div class="incident-details">${incident.location} • ${incident.timestamp}</div>
                    <div class="incident-source">🔥 ${incident.source}</div>
                </div>
            `).join('');
        }

        function highlightIncident(incidentId) {
            const incident = incidents.find(i => i.id === incidentId);
            if (incident) {
                map.setCenter({ lat: incident.lat, lng: incident.lng });
                map.setZoom(15);
            }
        }

        // Incident form handling
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.incident-type').forEach(type => {
                type.addEventListener('click', function() {
                    document.querySelectorAll('.incident-type').forEach(t => t.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedIncidentType = this.dataset.type;
                });
            });

            document.getElementById('incidentForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                if (!selectedIncidentType) {
                    alert('Please select an incident type');
                    return;
                }
                
                const location = document.getElementById('location').value;
                if (!location) {
                    alert('Please enter a location');
                    return;
                }
                
                const description = document.getElementById('description').value;
                const severity = document.getElementById('severity').value;
                
                const incidentData = {
                    type: selectedIncidentType,
                    location: location,
                    description: description,
                    severity: severity
                };
                
                try {
                    const response = await fetch('/api/incidents', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(incidentData)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        console.log('✅ Incident saved to Firestore!');
                        
                        incidents.unshift(data);
                        
                        const successDiv = document.getElementById('successMessage');
                        successDiv.innerHTML = `
                            <div class="success-message">
                                ✅ Incident saved to Firestore! Thank you for helping keep our community safe.
                            </div>
                        `;
                        successDiv.style.display = 'block';
                        
                        this.reset();
                        selectedIncidentType = '';
                        selectedLocation = null;
                        document.querySelectorAll('.incident-type').forEach(t => t.classList.remove('selected'));
                        
                        if (currentView === 'incidents') {
                            showIncidents();
                        }
                        
                        updateRecentIncidentsList();
                        
                        setTimeout(() => {
                            successDiv.style.display = 'none';
                        }, 5000);
                    } else {
                        console.error('❌ Error saving to Firestore:', data.error);
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    console.error('❌ Network error:', error);
                    alert('Network error. Please try again.');
                }
            });
        });

        function showAbout() {
            alert(`🛡️ SafetyMapper - Community Safety Platform

SafetyMapper helps communities stay safe through:

✅ Real-time incident reporting with Google Firestore storage
✅ Live police stations and hospitals display  
✅ Multi-modal safe route planning
✅ Incident-based route visualization
✅ Multiple view modes including comprehensive "All Data" view
✅ AI Safety Assistant powered by Google Gemini for intelligent guidance
✅ Cloud database with real-time synchronization

🤖 AI-Powered Chat Features:
• Natural language safety queries
• Pattern analysis and insights  
• Personalized safety recommendations
• Contextual route suggestions
• Professional floating chat interface

🔥 Powered by Google Cloud Firestore for reliable, scalable data storage.

Together, we can make our neighborhoods safer! 🌟`);
        }

        function showHelp() {
            alert(`🆘 How to use SafetyMapper:

📝 REPORT INCIDENTS:
• Select incident type and location
• All reports automatically saved to Firestore
• Real-time synchronization across users

🗺️ VIEW MODES:
• 📍 Incidents: See incident markers on map
• 🔥 Heatmap: Visualize incident density  
• 🚔 Safety Resources: See police stations & hospitals
• 🌟 All Data: See incident markers + heatmap + safety resources

🛤️ ROUTE PLANNING:
• Plan route once, view in any tab
• Enter start and end locations
• Choose travel mode (driving, walking, transit, cycling)
• Route appears in ALL tabs until cleared
• 🧹 Clear Route button to remove route

🤖 AI SAFETY ASSISTANT:
• Click the floating "🤖" button (bottom-right corner)
• Ask natural language questions about safety
• Get structured responses with local data analysis
• Receive personalized safety recommendations powered by Google Gemini
• Clean, professional chat interface
• Mobile-optimized for all devices

💡 All data is stored securely in Google Cloud Firestore!`);
        }
    </script>

    <script async defer 
            src="https://maps.googleapis.com/maps/api/js?key={{ api_key }}&libraries=places,visualization,geometry&callback=initMap">
    </script>
</body>
</html>
    ''', incidents=incidents, api_key=GOOGLE_MAPS_API_KEY)

# API Routes (rest of the code remains the same)
@app.route('/api/safety-resources', methods=['GET'])
def get_safety_resources():
    """Get police stations and hospitals for current map view"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        zoom = int(request.args.get('zoom', 12))
        
        radius = 5000 if zoom < 11 else 3000 if zoom < 13 else 2000 if zoom < 15 else 1000
        
        police_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            type='police'
        )
        
        hospital_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            type='hospital'
        )
        
        police_stations = []
        for place in police_result.get('results', [])[:10]:
            station = {
                'name': place.get('name', 'Police Station'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'address': place.get('vicinity', 'Unknown'),
                'rating': place.get('rating'),
                'place_id': place.get('place_id')
            }
            police_stations.append(station)
        
        hospitals = []
        for place in hospital_result.get('results', [])[:10]:
            hospital = {
                'name': place.get('name', 'Hospital'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'address': place.get('vicinity', 'Unknown'),
                'rating': place.get('rating'),
                'place_id': place.get('place_id')
            }
            hospitals.append(hospital)
        
        return jsonify({
            'police_stations': police_stations,
            'hospitals': hospitals,
            'total_resources': len(police_stations) + len(hospitals),
            'search_radius': radius
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get recent incidents from Firestore"""
    try:
        hours = request.args.get('hours', 24*7, type=int)  # Default 7 days
        limit = request.args.get('limit', 100, type=int)
        
        incidents = incident_manager.get_recent_incidents(hours=hours, limit=limit)
        return jsonify(incidents)
        
    except Exception as e:
        log_step(f"❌ Error getting incidents: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/incidents', methods=['POST'])
def create_incident():
    """Create a new incident report and store in Firestore"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['type', 'location', 'description', 'severity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Geocode the location
        geocode_result = gmaps.geocode(data['location'])
        
        if not geocode_result:
            return jsonify({"error": "Location not found"}), 400
        
        location = geocode_result[0]['geometry']['location']
        formatted_address = geocode_result[0]['formatted_address']
        
        # Prepare incident data for Firestore
        incident_data = {
            "type": data['type'],
            "location": formatted_address,
            "lat": location['lat'],
            "lng": location['lng'],
            "description": data['description'],
            "severity": data['severity'],
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', '')
        }
        
        # Store in Firestore
        stored_incident = incident_manager.store_incident(incident_data)
        
        if stored_incident:
            return jsonify(stored_incident), 201
        else:
            return jsonify({"error": "Failed to store incident"}), 500
            
    except Exception as e:
        log_step(f"❌ Error processing incident report: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """AI Safety Assistant endpoint using Gemini"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get recent incidents for context
        recent_incidents = incident_manager.get_recent_incidents(limit=20, hours=24*7)
        
        # Create rich context for Gemini
        context = {
            "total_incidents": len(recent_incidents),
            "incident_summary": {},
            "locations": [],
            "recent_activity": []
        }
        
        # Analyze incidents for context
        if recent_incidents:
            # Group by type
            for incident in recent_incidents:
                incident_type = incident.get('type', 'unknown')
                if incident_type not in context["incident_summary"]:
                    context["incident_summary"][incident_type] = 0
                context["incident_summary"][incident_type] += 1
                
                # Add locations
                location = incident.get('location', '')
                if location and location not in context["locations"]:
                    context["locations"].append(location)
                
                # Add recent activity (last 3)
                if len(context["recent_activity"]) < 3:
                    context["recent_activity"].append({
                        "type": incident.get('type'),
                        "location": incident.get('location'),
                        "severity": incident.get('severity'),
                        "description": incident.get('description', '')[:100]
                    })
        
        # Check if Gemini is configured
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            return jsonify({"response": get_structured_fallback_response(user_message, context)})
        
        # Use real Gemini API
        response = get_gemini_response(user_message, context)
        return jsonify({"response": response})
        
    except Exception as e:
        log_step(f"❌ AI Chat error: {e}")
        return jsonify({"response": "I'm having trouble right now. Please try again in a moment."}), 500

def get_gemini_response(user_message, context):
    """Get response from Gemini AI model - trying latest models first"""
    # Try newest models first, fallback to older ones
    model_names = [
        'gemini-2.0-flash-exp',      # Latest experimental
        'gemini-1.5-pro-002',       # Latest stable pro
        'gemini-1.5-flash-002',     # Latest stable flash
        'gemini-1.5-pro',           # Standard pro
        'gemini-1.5-flash'          # Standard flash
    ]
    
    for model_name in model_names:
        try:
            log_step(f"🤖 Attempting Gemini AI response with model: {model_name}")
            
            # Configure model settings
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1500,  # Reduced for more concise responses
            }
            
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            # Enhanced prompt for better formatted responses
            enhanced_prompt = f"""You are SafetyMapper AI Assistant. Provide helpful, well-formatted safety information.

USER QUESTION: "{user_message}"

LOCAL SAFETY DATA (Bethesda/Silver Spring/Chevy Chase area):
- Total incidents: {context['total_incidents']}
- Types: {context['incident_summary']}
- Recent locations: {context['locations'][:3]}

RESPONSE GUIDELINES:
1. Keep responses concise and well-structured
2. Use clear headings and bullet points
3. Separate local data analysis from general advice
4. Provide actionable safety recommendations
5. If question is about areas outside local data, clearly state that and provide general guidance

Format your response with clear sections like:
📊 LOCAL DATA ANALYSIS (if relevant)
🛡️ SAFETY RECOMMENDATIONS  
💡 GENERAL TIPS

Be helpful, professional, and safety-focused."""

            response = model.generate_content(enhanced_prompt)
            
            if response and response.text:
                log_step(f"✅ Gemini AI response received successfully using {model_name}")
                # Format the response nicely
                formatted_response = format_ai_response(response.text, context, user_message)
                return formatted_response
            else:
                log_step(f"❌ Gemini returned empty response for {model_name}")
                continue
                
        except Exception as e:
            log_step(f"❌ Gemini API error with {model_name}: {e}")
            continue
    
    # If all models fail, use fallback
    log_step("❌ All Gemini models failed, using fallback")
    return get_structured_fallback_response(user_message, context)

def format_ai_response(response_text, context, user_message):
    """Format AI response for better readability"""
    
    # Create header based on local data availability
    if context['total_incidents'] > 0:
        header = f"""<div style="background: #e8f4fd; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #2196F3;">
        <strong>📊 LOCAL SAFETY DATA</strong><br>
        <small>Based on {context['total_incidents']} recent incidents in Bethesda/Silver Spring/Chevy Chase area</small>
        </div>"""
    else:
        header = f"""<div style="background: #e8f5e8; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #4CAF50;">
        <strong>✅ LOCAL AREA STATUS</strong><br>
        <small>No recent incidents reported in your local area</small>
        </div>"""
    
    # Clean up the response text
    clean_response = response_text.replace('**', '<strong>').replace('**', '</strong>')
    clean_response = clean_response.replace('*', '•')
    
    # Add proper line breaks for better formatting
    clean_response = clean_response.replace('\n\n', '<br><br>')
    clean_response = clean_response.replace('\n', '<br>')
    
    return header + clean_response

def get_structured_fallback_response(user_message, context):
    """Structured fallback response when Gemini is not available"""
    message = user_message.lower()
    
    # Create header
    if context['total_incidents'] > 0:
        header = f"""<div style="background: #e8f4fd; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #2196F3;">
        <strong>📊 LOCAL SAFETY DATA</strong><br>
        <small>Based on {context['total_incidents']} recent incidents in your area</small>
        </div>"""
    else:
        header = f"""<div style="background: #e8f5e8; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #4CAF50;">
        <strong>✅ LOCAL AREA STATUS</strong><br>
        <small>No recent incidents reported in your area</small>
        </div>"""
    
    if 'safe' in message and ('walk' in message or 'night' in message):
        if context['total_incidents'] == 0:
            response = """<strong>🌙 NIGHT SAFETY ASSESSMENT</strong><br><br>
            Your local area shows <strong>no recent incident reports</strong>, which is encouraging for night safety.<br><br>
            <strong>🛡️ RECOMMENDED PRECAUTIONS:</strong><br>
            • Stay on well-lit main streets<br>
            • Walk with confidence and awareness<br>
            • Keep phone charged and accessible<br>
            • Trust your instincts about surroundings<br><br>
            <strong>💡 TIP:</strong> Continue monitoring SafetyMapper for real-time updates."""
        else:
            high_risk = sum(1 for inc in context.get('recent_activity', []) if inc.get('severity') == 'high')
            response = f"""<strong>🌙 NIGHT SAFETY ASSESSMENT</strong><br><br>
            Found <strong>{context['total_incidents']} recent incidents</strong> in your area{', including ' + str(high_risk) + ' high-severity' if high_risk > 0 else ''}.<br><br>
            <strong>⚠️ AREAS TO WATCH:</strong><br>
            • {', '.join(context['locations'][:3]) if context['locations'] else 'Check incident markers on map'}<br><br>
            <strong>🛡️ SAFETY RECOMMENDATIONS:</strong><br>
            • Use main streets with good lighting<br>
            • Consider rideshare for longer distances<br>
            • Stay alert and walk confidently<br>
            • Use route planner for safer paths"""
    
    elif 'incident' in message or 'recent' in message:
        if context['total_incidents'] == 0:
            response = """<strong>📊 RECENT ACTIVITY</strong><br><br>
            <strong>Good news!</strong> No recent incidents reported in your area.<br><br>
            <strong>🛡️ THIS SUGGESTS:</strong><br>
            • Low crime activity<br>
            • Effective safety measures<br>
            • Good community vigilance<br><br>
            <strong>💡 NEXT STEPS:</strong> Continue normal safety precautions and report any concerns."""
        else:
            incident_types = [f"{count} {type}" for type, count in context['incident_summary'].items()]
            response = f"""<strong>📊 RECENT ACTIVITY SUMMARY</strong><br><br>
            <strong>Total incidents:</strong> {context['total_incidents']}<br>
            <strong>Types:</strong> {', '.join(incident_types)}<br><br>
            <strong>📍 RECENT INCIDENTS:</strong><br>
            {'<br>'.join([f"• {inc['type'].title()} in {inc['location']} ({inc['severity']} severity)" for inc in context['recent_activity']])}
            <br><br><strong>💡 TIP:</strong> View map to see incident locations and patterns."""
    
    else:
        response = f"""<strong>🤖 SAFETYMAPPER ASSISTANT</strong><br><br>
        I'm here to help with safety questions! Currently tracking <strong>{context['total_incidents']} incidents</strong> in your area.<br><br>
        <strong>💬 TRY ASKING:</strong><br>
        • "Is it safe to walk at night?"<br>
        • "What recent incidents happened?"<br>
        • "What areas should I avoid?"<br>
        • "Analyze safety patterns"<br><br>
        <strong>🛡️ PERSONALIZED ADVICE:</strong> I'll use real incident data to provide safety recommendations.<br><br>
        <small>⚠️ <strong>Note:</strong> For enhanced AI capabilities, Gemini API integration provides more detailed analysis.</small>"""
    
    return header + response

@app.route('/api/route', methods=['POST'])
def plan_route():
    """Plan a safe route using incidents from Firestore"""
    try:
        data = request.json
        origin = data.get('origin')
        destination = data.get('destination')
        travel_mode = data.get('travel_mode', 'WALKING')
        
        if not origin or not destination:
            return jsonify({"error": "Origin and destination are required"}), 400
        
        # Get geocoded locations
        from_geocode = gmaps.geocode(origin)
        to_geocode = gmaps.geocode(destination)
        
        if not from_geocode or not to_geocode:
            return jsonify({"error": "Could not geocode locations"}), 400
        
        from_location = from_geocode[0]['geometry']['location']
        to_location = to_geocode[0]['geometry']['location']
        
        # Calculate route
        mode_mapping = {
            'DRIVING': 'driving',
            'WALKING': 'walking', 
            'TRANSIT': 'transit',
            'BICYCLING': 'bicycling'
        }
        
        google_mode = mode_mapping.get(travel_mode, 'walking')
        
        route_params = {
            'origin': from_location,
            'destination': to_location,
            'mode': google_mode
        }
        
        if travel_mode == 'DRIVING':
            route_params['avoid'] = ["tolls"]
        elif travel_mode in ['WALKING', 'BICYCLING']:
            route_params['avoid'] = ["highways", "tolls"]
        elif travel_mode == 'TRANSIT':
            route_params['departure_time'] = datetime.now()
        
        directions_result = gmaps.directions(**route_params)
        
        if not directions_result:
            return jsonify({"error": f"No {travel_mode.lower()} route found"}), 400
        
        route = directions_result[0]
        leg = route['legs'][0]
        duration = leg['duration']['text']
        distance = leg['distance']['text']
        
        # Get all incidents from Firestore for route analysis
        all_incidents = incident_manager.get_all_incidents()
        
        # Analyze route segments against Firestore incidents
        route_segments = analyze_route_segments(route, all_incidents)
        
        # Find safety resources
        midpoint_lat = (from_location['lat'] + to_location['lat']) / 2
        midpoint_lng = (from_location['lng'] + to_location['lng']) / 2
        search_radius = get_search_radius_by_mode(travel_mode)
        
        police_result = gmaps.places_nearby(
            location=(midpoint_lat, midpoint_lng),
            radius=search_radius,
            type='police'
        )
        police_stations = police_result.get('results', [])
        
        hospital_result = gmaps.places_nearby(
            location=(midpoint_lat, midpoint_lng),
            radius=search_radius,
            type='hospital'
        )
        hospitals = hospital_result.get('results', [])
        
        gas_stations = []
        if travel_mode == 'DRIVING':
            gas_result = gmaps.places_nearby(
                location=(midpoint_lat, midpoint_lng),
                radius=search_radius,
                type='gas_station'
            )
            gas_stations = gas_result.get('results', [])
        
        # Calculate safety score
        safety_score = calculate_safety_score_by_mode(
            police_stations, hospitals, gas_stations, distance, travel_mode
        )
        
        # Prepare response
        safe_points_text = f"{len(police_stations)} police stations, {len(hospitals)} hospitals"
        if gas_stations:
            safe_points_text += f", {len(gas_stations)} gas stations"
        
        route_info = {
            'safety_score': f"{safety_score}/10",
            'duration': duration,
            'distance': distance,
            'travel_mode': travel_mode,
            'safe_points': safe_points_text,
            'route_segments': route_segments,
            'incidents_analyzed': len(all_incidents)
        }
        
        return jsonify(route_info)
        
    except Exception as e:
        log_step(f"❌ Route planning failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_route_segments(route, incidents):
    """Analyze route segments using incidents from Firestore"""
    route_segments = []
    steps = route['legs'][0]['steps']
    
    for i, step in enumerate(steps):
        start_lat = step['start_location']['lat']
        start_lng = step['start_location']['lng']
        end_lat = step['end_location']['lat']
        end_lng = step['end_location']['lng']
        
        incidents_near_segment = count_incidents_near_route_segment(
            start_lat, start_lng, end_lat, end_lng, incidents, radius_miles=0.5
        )
        
        severe_incidents = count_severe_incidents_near_segment(
            start_lat, start_lng, end_lat, end_lng, incidents, radius_miles=0.3
        )
        
        if severe_incidents > 0 or incidents_near_segment >= 3:
            safety_level = 'high_risk'
        elif incidents_near_segment >= 1:
            safety_level = 'medium_risk'
        else:
            safety_level = 'safe'
        
        segment = {
            'segment_id': i,
            'encoded_path': step['polyline']['points'],
            'distance': step['distance']['text'],
            'duration': step['duration']['text'],
            'incident_count': incidents_near_segment,
            'severe_incidents': severe_incidents,
            'safety_level': safety_level
        }
        
        route_segments.append(segment)
    
    return route_segments

def count_incidents_near_route_segment(start_lat, start_lng, end_lat, end_lng, incidents, radius_miles=0.5):
    """Count incidents near a route segment"""
    count = 0
    
    for incident in incidents:
        incident_lat = incident.get('lat')
        incident_lng = incident.get('lng')
        
        if incident_lat and incident_lng:
            start_distance = calculate_distance(start_lat, start_lng, incident_lat, incident_lng)
            end_distance = calculate_distance(end_lat, end_lng, incident_lat, incident_lng)
            
            if start_distance <= radius_miles or end_distance <= radius_miles:
                count += 1
    
    return count

def count_severe_incidents_near_segment(start_lat, start_lng, end_lat, end_lng, incidents, radius_miles=0.3):
    """Count severe incidents near a route segment"""
    count = 0
    
    for incident in incidents:
        if incident.get('severity') == 'high':
            incident_lat = incident.get('lat')
            incident_lng = incident.get('lng')
            
            if incident_lat and incident_lng:
                start_distance = calculate_distance(start_lat, start_lng, incident_lat, incident_lng)
                end_distance = calculate_distance(end_lat, end_lng, incident_lat, incident_lng)
                
                if start_distance <= radius_miles or end_distance <= radius_miles:
                    count += 1
    
    return count

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in miles"""
    import math
    
    lat_diff = abs(lat1 - lat2)
    lng_diff = abs(lng1 - lng2)
    
    distance = math.sqrt((lat_diff * 69) ** 2 + (lng_diff * 54.6) ** 2)
    return distance

def get_search_radius_by_mode(travel_mode):
    """Get search radius based on travel mode"""
    radius_mapping = {
        'DRIVING': 5000,
        'WALKING': 1000,
        'TRANSIT': 2000,
        'BICYCLING': 2000
    }
    return radius_mapping.get(travel_mode, 2000)

def calculate_safety_score_by_mode(police_stations, hospitals, gas_stations, distance, travel_mode):
    """Calculate safety score based on travel mode"""
    base_scores = {
        'DRIVING': 6.0,
        'WALKING': 4.0,
        'TRANSIT': 5.0,
        'BICYCLING': 4.5
    }
    
    base_score = base_scores.get(travel_mode, 5.0)
    
    if travel_mode == 'DRIVING':
        police_bonus = min(len(police_stations) * 0.3, 1.5)
        hospital_bonus = min(len(hospitals) * 0.2, 1.0)
        gas_bonus = min(len(gas_stations) * 0.2, 1.0)
    elif travel_mode == 'WALKING':
        police_bonus = min(len(police_stations) * 0.7, 3.0)
        hospital_bonus = min(len(hospitals) * 0.5, 2.0)
        gas_bonus = 0
    elif travel_mode == 'TRANSIT':
        police_bonus = min(len(police_stations) * 0.5, 2.0)
        hospital_bonus = min(len(hospitals) * 0.3, 1.5)
        gas_bonus = 0
    else:  # BICYCLING
        police_bonus = min(len(police_stations) * 0.6, 2.5)
        hospital_bonus = min(len(hospitals) * 0.4, 1.5)
        gas_bonus = 0
    
    try:
        distance_value = float(distance.split()[0])
        distance_unit = distance.split()[1] if len(distance.split()) > 1 else 'mi'
        
        if distance_unit.lower().startswith('km'):
            distance_miles = distance_value * 0.621371
        else:
            distance_miles = distance_value
        
        if travel_mode == 'DRIVING':
            distance_penalty = min(distance_miles / 20.0, 1.0)
        elif travel_mode == 'WALKING':
            distance_penalty = min(distance_miles / 2.0, 2.0)
        elif travel_mode == 'TRANSIT':
            distance_penalty = min(distance_miles / 10.0, 1.5)
        else:  # BICYCLING
            distance_penalty = min(distance_miles / 5.0, 1.5)
            
    except:
        distance_penalty = 0.5
    
    final_score = base_score + police_bonus + hospital_bonus + gas_bonus - distance_penalty
    final_score = max(min(final_score, 10.0), 1.0)
    
    return round(final_score, 1)

if __name__ == '__main__':
    print("🚀 Starting SafetyMapper with Google Firestore + Real Gemini AI")
    print("🔥 Production Version - All Issues Resolved")
    print("🤖 AI Safety Assistant - Real Gemini Integration ✅ CONFIGURED")
    print("💬 Professional Chat Interface - Round Floating Button Design")
    print("🗺️ Visit http://localhost:8000 for SafetyMapper")
    print("📊 Features:")
    print("  ✅ Real-time incident reporting")
    print("  ✅ Google Firestore integration")
    print("  ✅ Interactive mapping with Google Maps")
    print("  ✅ Safe route planning with source/destination")
    print("  ✅ Police station & hospital overlay")
    print("  ✅ Incident heatmap visualization")
    print("  ✅ Multi-tab view system (Incidents/Heatmap/Safety/All)")
    print("  ✅ Real Gemini AI Safety Assistant with professional floating chat")
    print("  ✅ Structured AI responses with local data analysis")
    print("  ✅ Round floating action button like customer support")
    print()
    print("🎉 Ready to use real Google Gemini AI with enhanced professional chat!")
    app.run(debug=True, host='0.0.0.0', port=8000)