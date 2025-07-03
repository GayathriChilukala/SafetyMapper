# 🛡️ SafetyMapper - Community Safety Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Ready-blue.svg)](https://cloud.google.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **SafetyMapper** is a real-time community safety platform that helps users report incidents, plan safe routes, and access AI-powered safety insights. Built with Flask, Google Cloud Firestore, and Google Gemini AI.

## 🌟 Features

### 🗺️ **Interactive Safety Mapping**
- **Real-time incident reporting** with Google Maps integration
- **Multiple view modes**: Incidents, Heatmap, Safety Resources, All Data
- **Live police stations and hospitals** overlay
- **Incident visualization** with severity-based color coding

### 🛤️ **Smart Route Planning**
- **Multi-modal route planning** (driving, walking, transit, cycling)
- **Safety-based route analysis** using incident data
- **Route persistence** across all map views
- **Color-coded route segments** based on safety levels

### 🤖 **AI Safety Assistant**
- **Google Gemini AI integration** for intelligent safety insights
- **Professional floating chat interface** with round action button
- **Structured responses** separating local data from general advice
- **Natural language queries** about neighborhood safety
- **Pattern analysis** and personalized recommendations

### ☁️ **Cloud-Native Architecture**
- **Google Cloud Firestore** for real-time data synchronization
- **Production-ready** Google App Engine deployment
- **Scalable infrastructure** with automatic scaling
- **Secure API key management** and environment configuration

## 🖼️ Screenshots
### 🗺️ Interactive Safety Map

*Interactive map with real-time incident markers and safety resources*
<img src="https://github.com/user-attachments/assets/895f6764-e456-42e1-ae50-f715833197b8" width="600" alt="Main Dashboard">


> **Features shown:** Live incident markers, map controls, safety resource overlays, and real-time data synchronization

### 💬 AI Safety Assistant  
*Intelligent chatbot powered by Google Gemini AI*
<img src="https://github.com/user-attachments/assets/a5e8e1e0-6f71-4cae-b308-afd2f1c3b5ae" width="500" alt="Chat Interface">


> **Features shown:** Natural language safety queries, contextual responses, and floating chat interface

### 🛤️ Smart Route Planning
*Safety-optimized routing with incident analysis*
<img src="https://github.com/user-attachments/assets/7dc34476-2f55-415f-a927-1d23f4a3dfc7" width="600" alt="Route Planning">


> **Features shown:** Multi-modal routing, safety scoring, incident-aware path optimization

### 📱 Mobile Responsive Design
*Fully responsive interface for mobile devices*
<img src="https://github.com/user-attachments/assets/ce29b761-8665-4d50-aa46-e1de1ebf6a07" width="300" alt="Mobile View">


## 🛠️ Tech Stack

### **Backend**
- **Flask** - Python web framework
- **Google Cloud Firestore** - NoSQL database
- **Google Maps API** - Mapping and geocoding
- **Google Places API** - Location services
- **Google Gemini AI** - Intelligent chat assistant

### **Frontend**
- **Vanilla JavaScript** - Interactive functionality
- **Google Maps JavaScript API** - Map visualization
- **Responsive CSS** - Mobile-first design
- **Modern UI/UX** - Professional chat interface

### **Infrastructure**
- **Google App Engine** - Serverless deployment
- **Google Cloud APIs** - Integrated services
- **Automatic scaling** - Handle traffic spikes
- **Global CDN** - Fast worldwide access

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Google Cloud account with billing enabled
- Google Maps API key
- Google Gemini API key

### **Local Development**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/safetymapper.git
   cd safetymapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_MAPS_API_KEY=your_maps_api_key" > .env
   echo "GOOGLE_CLOUD_PROJECT=your_project_id" >> .env
   echo "GEMINI_API_KEY=your_gemini_api_key" >> .env
   ```

4. **Initialize Firestore**
   ```bash
   # Set up Google Cloud SDK
   gcloud init
   gcloud firestore databases create --region=us-central1
   ```

5. **Run locally**
   ```bash
   python safetymapper.py
   ```

6. **Open in browser**
   ```
   http://localhost:8000
   ```

## ☁️ Deployment to Google Cloud

### **One-Click Deployment**

1. **Set up Google Cloud project**
   ```bash
   gcloud projects create safetymapper-[your-name]
   gcloud config set project safetymapper-[your-name]
   gcloud app create --region=us-central1
   ```

2. **Enable required APIs**
   ```bash
   gcloud services enable appengine.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable maps-backend.googleapis.com
   ```

3. **Update configuration**
   - Edit `app.yaml` with your API keys
   - Update `GOOGLE_CLOUD_PROJECT` in environment variables

4. **Deploy**
   ```bash
   gcloud app deploy
   gcloud app browse
   ```

### **Detailed Deployment Guide**
See our comprehensive [Deployment Guide](docs/DEPLOYMENT.md) for advanced configuration options.

## 📱 Usage

### **Reporting Incidents**
1. Click on the map to select a location
2. Choose incident type (theft, assault, suspicious activity, etc.)
3. Add description and severity level
4. Submit to Firestore database

### **Planning Safe Routes**
1. Enter start and destination locations
2. Select travel mode (driving, walking, transit, cycling)
3. View color-coded route segments based on incident data
4. Route persists across all map view modes

### **AI Safety Assistant**
1. Click the floating 🤖 button (bottom-right)
2. Ask natural language questions about safety
3. Get structured responses with local data analysis
4. Receive personalized safety recommendations

### **Map View Modes**
- **📍 Incidents**: Individual incident markers
- **🔥 Heatmap**: Incident density visualization
- **🚔 Safety Resources**: Police stations and hospitals
- **🌟 All Data**: Combined view with all information

## 🔧 Configuration

### **Environment Variables**
```bash
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_CLOUD_PROJECT=your_firestore_project_id
GEMINI_API_KEY=your_gemini_api_key
```

### **API Keys Required**
1. **Google Maps API**: [Get API Key](https://console.cloud.google.com/apis/credentials)
   - Enable: Maps JavaScript API, Places API, Geocoding API
2. **Google Gemini AI**: [Get API Key](https://aistudio.google.com/app/apikey)
3. **Google Cloud Project**: [Create Project](https://console.cloud.google.com/)

### **Firestore Configuration**
```bash
# Initialize Firestore in your Google Cloud project
gcloud firestore databases create --region=us-central1
```

## 📊 API Endpoints

### **Incidents**
```bash
GET  /api/incidents          # Get recent incidents
POST /api/incidents          # Create new incident
```

### **Safety Resources**
```bash
GET  /api/safety-resources   # Get nearby police/hospitals
```

### **Route Planning**
```bash
POST /api/route              # Plan safe route with incident analysis
```

### **AI Chat**
```bash
POST /api/ai-chat            # Chat with Gemini AI assistant
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit: `git commit -am 'Add new feature'`
5. Push: `git push origin feature-name`
6. Create a Pull Request

### **Areas for Contribution**
- 🐛 **Bug fixes** and performance improvements
- 🎨 **UI/UX enhancements** and mobile optimization
- 🤖 **AI features** and chat improvements
- 📊 **Analytics** and reporting features
- 🔒 **Security** enhancements
- 📖 **Documentation** improvements

### **Code Style**
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Include docstrings for functions
- Test your changes locally before submitting

## 📈 Roadmap

### **Version 2.0 - Planned Features**
- [ ] **User authentication** and personal safety profiles
- [ ] **Community moderation** system for incident reports
- [ ] **Mobile app** (React Native or Flutter)
- [ ] **Real-time notifications** for nearby incidents
- [ ] **Emergency contacts** integration
- [ ] **Offline mode** capability
- [ ] **Advanced analytics** dashboard
- [ ] **Multi-language support**

### **Version 1.5 - Current Development**
- [ ] **Enhanced AI responses** with more context
- [ ] **Incident categories** filtering
- [ ] **User-generated safety tips**
- [ ] **Export functionality** for route data

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 SafetyMapper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

- **Google Cloud Platform** for hosting and database services
- **Google Maps API** for mapping functionality
- **Google Gemini AI** for intelligent chat features
- **Flask community** for the excellent web framework
- **Open source contributors** and safety advocacy communities

Made with ❤️ for community safety

