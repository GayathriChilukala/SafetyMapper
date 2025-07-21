# 🛡️ SafetyMapper - Community Safety Platform

A comprehensive community safety platform that combines real-time incident reporting, AI-powered safety analysis, interactive mapping, and intelligent route planning to help communities stay safe.

## 📽️ Video Demonstration

**🎬 2-Minute Demo Video**: [SafetyMapper: AI-Powered Community Safety Platform | Google Maps Platform Awards 2024](https://youtu.be/ygM2QJgfWHI?si=eirBiKkQPn0fCizX)


🌐 **Live Demo**: [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/)

> ⚠️ **Deployment Notice**: The live demo may become temporarily inaccessible as our Google Cloud Platform subscription is ending soon. Apologize for any inconvenience. The complete source code is available for local deployment, and we're working on securing funding for continued hosting. Please see the [Quick Start](#-quick-start) section for local installation instructions.

![SafetyMapper](https://img.shields.io/badge/SafetyMapper-Community%20Safety%20Platform-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Firestore%20%7C%20Maps%20%7C%20Gemini-orange)
![AI](https://img.shields.io/badge/AI-Gemini%20Pro%20%7C%20Vertex%20AI-purple)

## 💡 Project Inspiration

SafetyMapper was born from a real community need witnessed during late-night walks in urban areas. The inspiration came from three key observations:

### 🌃 **Personal Safety Challenges**
Walking home from work in downtown areas revealed a critical gap: the lack of real-time, community-driven safety information. Existing safety apps were either outdated, incomplete, or didn't leverage modern AI capabilities to provide intelligent safety guidance.

### 📱 **Technology Opportunity**
While mapping technology had advanced significantly with Google Maps Platform, safety applications hadn't kept pace with modern AI capabilities. There was a clear opportunity to combine:
- **Real-time community reporting** with **AI-powered analysis**
- **Google Maps Platform's comprehensive APIs** with **Vertex AI Safety**
- **Individual safety needs** with **community intelligence**

### 🏘️ **Community Impact Vision**
The vision was to create a platform where communities could share safety information in real-time, get AI-powered safety advice based on actual local data, plan routes with safety as a primary consideration, and build stronger, more connected neighborhoods through shared safety awareness.

## 📚 Project History

SafetyMapper evolved from a simple concept to a comprehensive safety platform through focused development and community feedback.

### **Foundation & Core Development**
The project began with basic incident reporting using Google Maps JavaScript API. Early user feedback emphasized the need for intelligent safety advice, leading to the integration of Google Gemini AI for contextual safety assistance.

### **AI Integration Breakthrough**
The major breakthrough came with implementing Vertex AI Safety for content moderation, creating the first community safety platform with enterprise-grade AI safety filtering. This allowed for professional-quality interactions while maintaining community openness.

### **Comprehensive Maps Integration**
Expanding to utilize 9 different Google Maps Platform APIs created a comprehensive safety ecosystem - from basic mapping to advanced route planning with safety analysis, police station discovery, and incident visualization.

### **Production Deployment**
Successfully deploying on Google Cloud Platform with real users reporting incidents and using the AI assistant validated the platform's practical value and enterprise readiness.

## 🗺️ Google Maps Platform Integration

SafetyMapper demonstrates comprehensive use of Google Maps Platform, showcasing the platform's versatility for community safety applications:

### **Core Mapping & Interaction (4 APIs)**
- **Maps JavaScript API**: Interactive map display with custom styling, real-time incident markers, user interactions, and custom info windows
- **Places API**: Location autocomplete, nearby police stations/hospitals discovery, place validation and ratings
- **Directions API**: Multi-modal route calculation with real-time optimization and safety-aware routing
- **Geocoding API**: Address standardization, coordinate conversion, and geographic validation

### **Visualization & Analysis (2 APIs)**
- **Visualization Library**: Crime density heatmaps with weighted incident visualization and dynamic overlays
- **Geometry Library**: Distance calculations, route segment analysis, and proximity computations for safety scoring

### **Innovation in Maps Usage**
- **Safety-First Route Planning**: Routes dynamically scored based on incident proximity and safety resource availability
- **Community Intelligence Integration**: Crowdsourced safety data seamlessly integrated with official mapping data
- **Multi-Modal Safety Considerations**: Different safety algorithms for walking, driving, transit, and bicycling
- **Real-Time Resource Discovery**: Automatic identification of safety resources (police, hospitals) along planned routes

## 🎓 Key Learnings

### **AI Integration Mastery**
Implementing Vertex AI Safety with Gemini AI taught us to balance AI helpfulness with safety requirements. The key learning was creating multi-layered content filtering that maintains professional standards while allowing natural community safety discussions.

### **Google Cloud Platform Optimization**
Managing 9 simultaneous Google APIs required careful rate limiting, error handling, and performance optimization. We learned to design for both real-time responsiveness and long-term scalability.

### **User Experience Insights**
Safety applications must work perfectly on mobile devices with immediate response times. Users need to trust both the data quality and the AI advice, requiring transparent data sourcing and professional-grade security.

### **Community Safety Dynamics**
Real-world deployment revealed that successful safety platforms need both individual utility (route planning, safety queries) and community value (shared incident reporting, collective intelligence).

## 🌟 Key Differentiators

### **First-of-its-Kind AI Safety Integration**
SafetyMapper is the first community safety platform to integrate Vertex AI Safety with Gemini AI, providing enterprise-grade content moderation with intelligent, context-aware safety advice based on real local data.

### **Most Comprehensive Google Maps Integration**
With 9 Google Maps Platform APIs, SafetyMapper represents the deepest integration of Google's mapping ecosystem in the community safety domain, from basic visualization to advanced predictive routing.

### **Real-Time Community Intelligence**
Unlike static safety apps, SafetyMapper provides live incident reporting with immediate map updates, AI-verified photo uploads, and dynamic safety scoring that adapts to current conditions.

### **Enterprise-Ready Architecture**
Built from day one with enterprise deployment in mind, featuring multi-layered security, audit trails, scalable architecture, and professional-grade performance suitable for city-wide deployment.

### **Production-Proven Platform**
SafetyMapper isn't just a concept - it's a live, working application with real users reporting incidents and receiving AI-powered safety assistance, demonstrating practical value and market readiness.

## 🌟 Features

### 🗺️ Interactive Mapping
- **Real-time incident visualization** with Google Maps integration
- **Multiple view modes**: Incidents, Heatmap, Safety Resources, All Data
- **Location-based incident clustering** and severity color coding
- **Police stations and hospitals overlay** for emergency resources
- **Click-to-select locations** for incident reporting

### 🤖 AI Safety Assistant
- **Powered by Google Gemini Pro** for intelligent safety analysis
- **Vertex AI Safety moderation** with multi-layered content filtering
- **Location-specific safety insights** based on real incident data
- **Professional floating chat interface** with mobile optimization
- **Natural language queries** for safety questions and recommendations

### 📊 Incident Management
- **Real-time incident reporting** with photo upload support
- **Google Cloud Firestore integration** for scalable data storage
- **Multi-severity classification** (Low, Medium, High)
- **Incident type categorization** (Theft, Assault, Harassment, Vandalism, Suspicious, Other)
- **Automatic geocoding** and location validation
- **Photo compression and validation** (max 2MB, JPEG optimization)

### 🛤️ Safe Route Planning
- **Multi-modal route planning** (Walking, Driving, Transit, Bicycling)
- **Incident-based risk analysis** along routes
- **Safety scoring algorithm** with resource proximity calculation
- **Route segment visualization** with color-coded risk levels
- **Persistent route display** across browser tabs
- **Clear route functionality** for easy reset

### 🔒 Advanced Security
- **Vertex AI Safety Moderator** with content filtering
- **Multi-layered safety checks**: Content, Brand, Alignment, Security/Privacy
- **Dangerous content detection** with keyword and AI filtering
- **Professional communication standards** enforcement
- **Privacy protection** for user data

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Google Cloud Platform account
- Google Maps API key
- Google Gemini API key
- Google Cloud Firestore database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/safetymapper.git
   cd safetymapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   
   Edit `main.py` and replace the placeholder API keys:
   ```python
   GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
   GOOGLE_CLOUD_PROJECT = "your_google_cloud_project_id"
   GEMINI_API_KEY = "your_gemini_api_key"
   ```

4. **Set up Google Cloud Firestore**
   - Create a Firestore database in your Google Cloud project
   - Enable the Firestore API
   - Set up authentication (service account or default credentials)

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - **Local**: Open your browser and go to `http://localhost:8000`
   - **Live Demo**: Visit [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/) *(may be temporarily unavailable)*
   - The application will automatically initialize sample data if the database is empty

## 🏗️ Architecture

### Core Components

#### 1. **VertexAISafetyModerator**
- Multi-layered content safety filtering
- Brand safety and alignment checks
- Security and privacy protection
- Fallback to basic filtering if AI unavailable

#### 2. **FirestoreIncidentManager**
- Real-time incident storage and retrieval
- Location-based data analysis
- Automatic timestamp formatting
- Sample data initialization

#### 3. **AI Safety Assistant**
- Google Gemini Pro integration
- Location-specific safety analysis
- Context-aware responses
- Professional chat interface

#### 4. **Route Planning Engine**
- Google Maps Directions API integration
- Incident proximity analysis
- Safety scoring algorithm
- Multi-modal route optimization

### Data Flow

```
User Input → Vertex AI Safety Check → Database Query → AI Analysis → Response
     ↓              ↓                    ↓              ↓           ↓
  Incident     Content Filter      Firestore Data   Gemini AI   Formatted
  Report       Brand Safety        Location Data    Context     Response
```

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/api/ai-chat` | POST | AI Safety Assistant chat |
| `/api/incidents` | GET | Retrieve recent incidents |
| `/api/incidents` | POST | Create new incident report |
| `/api/route` | POST | Plan safe route |
| `/api/safety-resources` | GET | Get police/hospital data |
| `/api/test-photo` | POST | Test photo upload |

### Request Examples

#### Create Incident
```json
POST /api/incidents
{
  "type": "theft",
  "location": "123 Main St, Bethesda, MD",
  "description": "Bike theft near metro station",
  "severity": "medium"
}
```

#### AI Chat
```json
POST /api/ai-chat
{
  "message": "Is it safe to walk downtown at night?"
}
```

#### Route Planning
```json
POST /api/route
{
  "origin": "Bethesda Metro Station",
  "destination": "Downtown Bethesda",
  "travel_mode": "WALKING"
}
```

## 🎨 User Interface

### Main Dashboard
- **Interactive Google Maps** with incident markers
- **Real-time incident reporting** form
- **Recent incidents sidebar** with click-to-highlight
- **Route planning panel** with safety analysis
- **Floating AI chat button** for instant assistance

### View Modes
1. **📍 Incidents**: Individual incident markers
2. **🔥 Heatmap**: Density visualization
3. **🚔 Safety Resources**: Police stations and hospitals
4. **🌟 All Data**: Combined view

### Mobile Responsive
- Optimized for all device sizes
- Touch-friendly interface
- Responsive chat modal
- Mobile-optimized controls

## 🔧 Configuration

### Environment Variables
```bash
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_MAPS_API_KEY=your_maps_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Google Cloud Setup
1. **Enable APIs**:
   - Google Maps JavaScript API
   - Google Maps Directions API
   - Google Maps Places API
   - Google Maps Geocoding API
   - Firestore API
   - **Vertex AI API** (for safety moderation)
   - **Generative AI API** (for Gemini integration)

2. **Set up Firestore**:
   - Create database in native mode
   - Set up security rules
   - Configure indexes if needed

3. **Configure Gemini**:
   - Enable Vertex AI API
   - Set up API key with appropriate permissions
   - Ensure billing is enabled for AI services

4. **Vertex AI Safety Setup**:
   - Enable Vertex AI API in your Google Cloud Console
   - The safety features use Gemini's built-in safety filters
   - No additional API keys needed beyond Gemini API key

## 🚀 Deployment

**Current Deployment**: [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/)

**Deployment Status**: ⚠️ May be temporarily unavailable due to GCP subscription constraints

### Local Deployment
```bash
# Clone and setup
git clone https://github.com/yourusername/safetymapper.git
cd safetymapper
pip install -r requirements.txt

# Configure your API keys in main.py
# Run locally
python main.py
# Access at http://localhost:8000
```

### Production Deployment
```bash
# Deploy to Google App Engine
gcloud app deploy

# Deploy to other platforms
# Docker, Heroku, AWS, etc. supported
```

## 📊 Data Schema

### Incident Structure
```json
{
  "incident_id": "uuid",
  "type": "theft|assault|harassment|vandalism|suspicious|other",
  "location": "formatted_address",
  "latitude": 38.9847,
  "longitude": -77.0947,
  "description": "incident_description",
  "severity": "low|medium|high",
  "created_at": "timestamp",
  "source": "user_report",
  "status": "active",
  "reporter_info": {
    "ip_address": "user_ip",
    "user_agent": "browser_info",
    "report_time": "timestamp"
  }
}
```

## 🔒 Security Features

### Content Moderation
- **Vertex AI Safety filtering** for harmful content
- **Keyword-based detection** for dangerous content
- **Brand safety enforcement** for professional communication
- **Privacy protection** for sensitive information

### Data Protection
- **Input validation** and sanitization
- **Rate limiting** on API endpoints
- **Secure API key management**
- **Firestore security rules**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include error handling
- Write unit tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Platform** for infrastructure and APIs
- **Google Gemini** for AI capabilities
- **Google Maps** for mapping and geolocation
- **Flask** for the web framework
- **Community contributors** for feedback and improvements

## 📸 Screenshots & Documentation

### Application Screenshots
*Note: If the live demo is inaccessible, these screenshots demonstrate the full functionality*

**Live Application**: [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/) *(may be temporarily unavailable)*

**Key Interface Screenshots:**
- Main dashboard with incident map
- <img width="1469" alt="image" src="https://github.com/user-attachments/assets/3aaf75a8-1e4c-41d1-b0da-7c26ab3f6be7" />

- AI Safety Assistant chat interface
- <img width="446" alt="image" src="https://github.com/user-attachments/assets/9a19b657-b44b-4aa1-9088-995015c7acd7" />

- Incident reporting form with photo upload
- <img width="1459" alt="image" src="https://github.com/user-attachments/assets/9cab7ea5-141b-49cd-9599-eca8f73d1350" />

- Route planning with safety analysis
- <img width="1452" alt="image" src="https://github.com/user-attachments/assets/3e62078a-9220-4670-9857-a21a60474c0a" />

- Mobile responsive interface
- <img width="445" alt="image" src="https://github.com/user-attachments/assets/f8976948-4f01-47c4-bc35-df74993d46d2" />

- Vertex AI Safety Screenshots
- Safe User Query
- <img width="377" alt="image" src="https://github.com/user-attachments/assets/fcf333a9-b51e-48eb-8c21-e961711cbd07" />

- Blocked Dangerous Content
- <img width="383" alt="image" src="https://github.com/user-attachments/assets/0a30c9dc-f904-4951-b9b8-5afb52b003ca" />

## 🔄 Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - Added AI Safety Assistant
- **v1.2.0** - Enhanced route planning
- **v1.3.0** - Photo upload support
- **v1.4.0** - Vertex AI Safety integration

---

**Made with ❤️ for safer communities**

*Building the future of AI-powered community safety, one neighborhood at a time.*
