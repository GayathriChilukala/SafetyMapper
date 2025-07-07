# 🛡️ SafetyMapper - Community Safety Platform

<div align="center">

![SafetyMapper Logo](https://img.shields.io/badge/SafetyMapper-Community%20Safety-blue?style=for-the-badge&logo=shield&logoColor=white)

**Complete Community Safety Platform with AI-Powered Assistance**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Enabled-orange?style=flat-square&logo=googlecloud)](https://cloud.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[🚀 Quick Start](#-quick-start) • [📋 Features](#-features) • [⚙️ Setup](#%EF%B8%8F-setup) • [🔧 Configuration](#-configuration) • [📖 API Documentation](#-api-documentation)

</div>

---

## 📋 Features

### 🤖 **AI-Powered Safety Assistant**
- **Advanced Chat Interface** with Google Gemini Pro
- **Multi-layered Content Moderation** using Vertex AI Safety
- **Natural Language Safety Queries** with contextual responses
- **Real-time Incident Analysis** for personalized advice

### 🗺️ **Interactive Safety Mapping**
- **Real-time Incident Visualization** with multiple view modes
- **Safety Resource Overlay** (police stations, hospitals)
- **Incident Heatmap** for risk density analysis
- **Multi-modal Route Planning** (driving, walking, transit, cycling)
- **Safety-aware Route Analysis** with incident correlation

### 📊 **Incident Reporting System**
- **Real-time Reporting** with Google Firestore integration
- **Photo Upload Support** with automatic compression
- **Geocoding & Address Validation** via Google Maps
- **Severity Classification** and categorization
- **Community-driven Data** collection

### 🛡️ **Enterprise Security**
- **Vertex AI Safety Filtering** for all user interactions
- **Privacy-focused Design** with data protection
- **Input Validation** and sanitization
- **Professional Content Guidelines** enforcement

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Platform account
- Google Maps API access
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/safetymapper.git
cd safetymapper

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

**🌐 Access:** Open `http://localhost:8000` in your browser

---

## ⚙️ Setup

### 1. **Google Cloud Setup**

#### Enable Required APIs:
```bash
gcloud services enable maps-backend.googleapis.com
gcloud services enable places-backend.googleapis.com
gcloud services enable geocoding-backend.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

#### Create Service Account:
```bash
gcloud iam service-accounts create safetymapper-service
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:safetymapper-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/firestore.user"
```

### 2. **API Keys Required**

| Service | Key Type | Purpose |
|---------|----------|---------|
| Google Maps | API Key | Mapping, geocoding, places |
| Google Cloud | Project ID | Firestore database |
| Gemini AI | API Key | AI chat assistant |

### 3. **Dependencies**

```bash
pip install flask
pip install google-cloud-firestore
pip install google-generativeai
pip install googlemaps
pip install requests
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file or update `main.py` directly:

```python
# Google API Configuration
GOOGLE_MAPS_API_KEY = "your_maps_api_key_here"
GOOGLE_CLOUD_PROJECT = "your_project_id_here" 
GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional: Custom Configuration
DEBUG_MODE = True
PORT = 8000
HOST = "0.0.0.0"
```

### Firestore Setup

1. **Create Firestore Database:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to Firestore
   - Create database in "Native Mode"
   - Choose your preferred region

2. **Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /incidents/{document} {
      allow read, write: if true; // Adjust based on your security needs
    }
  }
}
```

---

## 📖 API Documentation

### Chat Endpoint
```http
POST /api/ai-chat
Content-Type: application/json

{
  "message": "Is it safe to walk downtown at night?"
}
```

### Incident Reporting
```http
POST /api/incidents
Content-Type: application/json

{
  "type": "theft",
  "location": "123 Main St, City, State",
  "description": "Bike stolen from rack",
  "severity": "medium",
  "has_photo": false
}
```

### Route Planning
```http
POST /api/route
Content-Type: application/json

{
  "origin": "Start Address",
  "destination": "End Address", 
  "travel_mode": "WALKING"
}
```

### Safety Resources
```http
GET /api/safety-resources?lat=38.9847&lng=-77.0947&zoom=12
```

---

## 🎯 Usage Examples

### 💬 **AI Chat Examples**
```
✅ "Is it safe to walk in downtown at night?"
✅ "What recent incidents happened in my area?"
✅ "How safe is the Silver Spring area?"
✅ "What areas should I avoid?"

🚫 Inappropriate content is automatically filtered
```

### 📍 **Map Interactions**
- **Click anywhere** on the map to select incident location
- **Toggle views:** Incidents → Heatmap → Safety Resources → All
- **Route planning:** Enter start/end points for safety analysis

### 📊 **Incident Reporting**
1. Select incident type (theft, assault, harassment, etc.)
2. Click map location or enter address
3. Add description and severity level
4. Optional: Upload photo (auto-compressed)
5. Submit → Real-time Firestore storage

---

## 🚀 Deployment

### Local Development
```bash
python main.py
# Access: http://localhost:8000
```

### Production Deployment

#### Google Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/safetymapper

# Deploy
gcloud run deploy safetymapper \
  --image gcr.io/YOUR_PROJECT_ID/safetymapper \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Heroku
```bash
# Create Procfile
echo "web: python main.py" > Procfile

# Deploy
heroku create your-safetymapper-app
git push heroku main
```

---

## 🧪 Testing

### Manual Testing
```bash
# Test safety filtering
curl -X POST http://localhost:8000/api/ai-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is downtown safe at night?"}'

# Test incident reporting  
curl -X POST http://localhost:8000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "type": "theft",
    "location": "123 Main St",
    "description": "Test incident",
    "severity": "low"
  }'
```

### Built-in Safety Tests
The application includes automated safety testing that runs on startup in debug mode.

---

## 🔒 Security & Privacy

### Data Protection
- **No Personal Information Storage** - IP addresses logged for security only
- **Photo Compression** - Automatic image optimization before storage
- **Content Filtering** - Multi-layered AI safety checks
- **Secure APIs** - Input validation and sanitization

### Content Moderation
- **Vertex AI Safety** - Google's enterprise-grade content filtering
- **Multi-category Filtering** - Violence, harassment, inappropriate content
- **Real-time Analysis** - Every message processed before response
- **Professional Guidelines** - Maintains community-appropriate interactions

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Ensure security best practices

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Common Issues

**❌ "Google Maps not loading"**
```bash
# Check API key permissions
# Ensure Maps JavaScript API is enabled
# Verify billing is set up
```

**❌ "Firestore connection failed"**
```bash
# Verify project ID is correct
# Check service account permissions
# Ensure Firestore is enabled
```

**❌ "AI chat not responding"**
```bash
# Verify Gemini API key
# Check API quotas
# Review safety filter logs
```

### Getting Help
- 📧 **Email:** support@safetymapper.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/safetymapper/issues)
- 📖 **Documentation:** [Wiki](https://github.com/yourusername/safetymapper/wiki)

---

## 🎉 Acknowledgments

- **Google Cloud Platform** for enterprise infrastructure
- **Google Gemini** for AI-powered assistance  
- **Google Maps** for mapping and geocoding services
- **Vertex AI** for content safety and moderation
- **Open Source Community** for inspiration and tools

---

<div align="center">

**Made with ❤️ for Community Safety**

[⭐ Star this repo](https://github.com/yourusername/safetymapper) • [🐛 Report Bug](https://github.com/yourusername/safetymapper/issues) • [✨ Request Feature](https://github.com/yourusername/safetymapper/issues)

</div>
