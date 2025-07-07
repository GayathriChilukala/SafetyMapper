# 🛡️ SafetyMapper - Community Safety Platform

A comprehensive community safety platform that combines real-time incident reporting, AI-powered safety analysis, interactive mapping, and intelligent route planning to help communities stay safe.

🌐 **Live Demo**: [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/)

![SafetyMapper](https://img.shields.io/badge/SafetyMapper-Community%20Safety%20Platform-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Firestore%20%7C%20Maps%20%7C%20Gemini-orange)
![AI](https://img.shields.io/badge/AI-Gemini%20Pro%20%7C%20Vertex%20AI-purple)

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
   - **Live Demo**: Visit [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/)
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

**Current Deployment**: Successfully deployed at [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/)

**Deployment Status**: ✅ Live and operational

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
*[Add screenshots here to showcase the application interface]*

**Live Application**: [https://ancient-watch-460222-n5.uc.r.appspot.com/](https://ancient-watch-460222-n5.uc.r.appspot.com/)

**Recommended screenshots to include:**
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


### Demo Videos
*[Add demo videos here to show application functionality]*


## 🔄 Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - Added AI Safety Assistant
- **v1.2.0** - Enhanced route planning
- **v1.3.0** - Photo upload support
- **v1.4.0** - Vertex AI Safety integration

---

**Made with ❤️ for safer communities**

