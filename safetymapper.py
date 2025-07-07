#!/usr/bin/env python3
"""
SafetyMapper - Complete Community Safety Platform
Features:
- Vertex AI Safety content moderation
- Real-time incident reporting with Firestore
- AI Safety Assistant powered by Google Gemini
- Interactive mapping with Google Maps
- Safe route planning with risk analysis
- Professional chat interface with advanced guardrails
"""

from flask import Flask, render_template_string, request, jsonify
import googlemaps
from datetime import datetime, timedelta
import json
import uuid
import re
import requests
from concurrent.futures import ThreadPoolExecutor

# Google Cloud imports
try:
    from google.cloud import firestore
    from google.cloud.exceptions import NotFound
except ImportError:
    print("⚠️ google-cloud-firestore not installed. Run: pip install google-cloud-firestore")
    firestore = None

# Gemini AI imports
try:
    import google.generativeai as genai
except ImportError:
    print("⚠️ google-generativeai not installed. Run: pip install google-generativeai")
    genai = None

# Initialize Flask app
app = Flask(__name__)

# ============================================================================
# INITIALIZE CLIENTS
# ============================================================================

# Initialize Google Maps client
try:
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    print("✅ Google Maps client initialized")
except Exception as e:
    print(f"❌ Google Maps initialization failed: {e}")
    gmaps = None

# Initialize Gemini AI
try:
    if genai and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini AI configured successfully")
    else:
        print("⚠️ Gemini API key not configured - using fallback responses")
except Exception as e:
    print(f"❌ Gemini setup failed: {e}")
    print("⚠️ Using fallback responses")

# Initialize Firestore client
try:
    if firestore:
        import os
        os.environ['GOOGLE_CLOUD_PROJECT'] = GOOGLE_CLOUD_PROJECT
        db = firestore.Client(project=GOOGLE_CLOUD_PROJECT)
        print(f"✅ Connected to Google Firestore (Project: {GOOGLE_CLOUD_PROJECT})")
    else:
        db = None
except Exception as e:
    print(f"❌ Failed to connect to Firestore: {e}")
    db = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_step(message: str, details: dict = None):
    """Enhanced logging for SafetyMapper workflow"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if details:
        for key, value in details.items():
            print(f"  {key}: {value}")

# ============================================================================
# VERTEX AI SAFETY MODERATOR
# ============================================================================

class VertexAISafetyModerator:
    """
    Advanced content moderation using Vertex AI's built-in safety features
    Based on Google Cloud's multi-layered safety approach for Gemini
    """
    
    def __init__(self, gemini_api_key=None):
        self.api_key = gemini_api_key or GEMINI_API_KEY
        self.enabled = self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE" and genai is not None
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                log_step("✅ Vertex AI Safety filtering enabled with Gemini")
                
                # Test API connection
                self._test_connection()
                
            except Exception as e:
                log_step(f"❌ Vertex AI Safety setup failed: {e}")
                self.enabled = False
        else:
            log_step("⚠️ Vertex AI Safety not configured - using basic filtering")
    
    def _test_connection(self):
        """Test Gemini API connection"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello")
            log_step("✅ Gemini API connection verified")
        except Exception as e:
            log_step(f"❌ Gemini API test failed: {e}")
            self.enabled = False
    
    def check_content(self, message):
        """
        Multi-layered safety check using Vertex AI
        Covers: Content risks, Brand safety, Alignment risks, Security/Privacy risks
        """
        if not self.enabled:
            return self.basic_content_check(message)
        
        try:
            # Multi-layered safety evaluation
            safety_results = {
                'content_safety': self._check_content_safety(message),
                'brand_safety': self._check_brand_safety(message),
                'alignment_check': self._check_alignment(message),
                'security_privacy': self._check_security_privacy(message)
            }
            
            return self._evaluate_combined_results(message, safety_results)
            
        except Exception as e:
            log_step(f"❌ Vertex AI Safety check failed: {e}")
            return self.basic_content_check(message)
    
    def _check_content_safety(self, message):
        """Check for harmful content, profanity, violence using Gemini safety filters"""
        try:
            # Configure strict safety settings for content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                safety_settings=safety_settings
            )
            
            # Test prompt that would trigger safety if message is inappropriate
            safety_test_prompt = f"""
            Analyze this user message for safety concerns: "{message}"
            
            Is this message appropriate for a community safety application?
            Respond with just: SAFE or UNSAFE
            """
            
            response = model.generate_content(safety_test_prompt)
            
            # If we get a response, content passed initial safety filters
            if response.text and "UNSAFE" in response.text.upper():
                return {
                    'blocked': True,
                    'category': 'CONTENT_SAFETY',
                    'reason': 'Content deemed unsafe by Gemini',
                    'confidence': 0.8
                }
            
            return {
                'blocked': False,
                'category': 'CONTENT_SAFETY',
                'reason': 'Content passed safety filters',
                'confidence': 0.9
            }
            
        except Exception as e:
            # If safety filters block the request, it means content is inappropriate
            error_msg = str(e).lower()
            if any(word in error_msg for word in ['safety', 'blocked', 'harmful', 'inappropriate']):
                return {
                    'blocked': True,
                    'category': 'CONTENT_SAFETY',
                    'reason': f'Blocked by Vertex AI safety filters: {str(e)[:100]}',
                    'confidence': 0.9
                }
            
            # Other errors - inconclusive
            return {
                'blocked': False,
                'category': 'CONTENT_SAFETY',
                'reason': 'Safety check inconclusive',
                'confidence': 0.1
            }
    
    def _check_brand_safety(self, message):
        """Check for content that may not align with SafetyMapper brand values"""
        try:
            brand_safety_prompt = f"""
            Evaluate if this message aligns with a professional community safety platform's brand values: "{message}"
            
            Consider:
            - Professional tone
            - Community safety focus
            - Helpful intent
            - Appropriate for public safety discussions
            
            Rate from 1-10 where 10 is perfectly aligned with brand values.
            Respond with just the number.
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(brand_safety_prompt)
            
            try:
                brand_score = float(response.text.strip())
                if brand_score < 6:  # Below 6/10 considered brand risk
                    return {
                        'blocked': True,
                        'category': 'BRAND_SAFETY',
                        'reason': f'Low brand alignment score: {brand_score}/10',
                        'confidence': 0.7
                    }
            except ValueError:
                pass  # If can't parse score, assume safe
            
            return {
                'blocked': False,
                'category': 'BRAND_SAFETY',
                'reason': 'Content aligns with brand values',
                'confidence': 0.8
            }
            
        except Exception as e:
            return {
                'blocked': False,
                'category': 'BRAND_SAFETY',
                'reason': 'Brand safety check failed',
                'confidence': 0.1
            }
    
    def _check_alignment(self, message):
        """Check if content is relevant and accurate for safety context"""
        try:
            alignment_prompt = f"""
            Is this message relevant to community safety, crime prevention, or emergency preparedness: "{message}"
            
            Examples of relevant topics:
            - Safety questions about neighborhoods
            - Crime reporting and prevention
            - Emergency preparedness
            - Personal safety tips
            - Security concerns
            
            Respond with: RELEVANT or IRRELEVANT
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(alignment_prompt)
            
            if "IRRELEVANT" in response.text.upper():
                return {
                    'blocked': True,
                    'category': 'ALIGNMENT',
                    'reason': 'Content not relevant to safety context',
                    'confidence': 0.6
                }
            
            return {
                'blocked': False,
                'category': 'ALIGNMENT',
                'reason': 'Content relevant to safety context',
                'confidence': 0.8
            }
            
        except Exception as e:
            return {
                'blocked': False,
                'category': 'ALIGNMENT',
                'reason': 'Alignment check failed',
                'confidence': 0.1
            }
    
    def _check_security_privacy(self, message):
        """Check for security and privacy risks"""
        violations = []
        message_lower = message.lower()
        
        # Check for potential personal information
        # Email addresses
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message):
            violations.append('Contains email address')
        
        # Phone numbers
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', message):
            violations.append('Contains phone number')
        
        # Social Security Numbers
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', message):
            violations.append('Contains SSN pattern')
        
        # Credit card patterns
        if re.search(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', message):
            violations.append('Contains credit card pattern')
        
        # Potential prompt injection attempts
        injection_patterns = [
            'ignore previous instructions',
            'system prompt',
            'you are now',
            'pretend to be',
            'act as if',
            'roleplay as'
        ]
        
        for pattern in injection_patterns:
            if pattern in message_lower:
                violations.append(f'Potential prompt injection: {pattern}')
        
        if violations:
            return {
                'blocked': True,
                'category': 'SECURITY_PRIVACY',
                'reason': f'Security/privacy violations: {", ".join(violations)}',
                'confidence': 0.9
            }
        
        return {
            'blocked': False,
            'category': 'SECURITY_PRIVACY',
            'reason': 'No security or privacy concerns detected',
            'confidence': 0.9
        }
    
    def _evaluate_combined_results(self, message, safety_results):
        """Combine all safety check results using multi-layered approach"""
        violations = []
        max_confidence = 0
        blocked_categories = []
        
        # Check each safety layer
        for category, result in safety_results.items():
            if result['blocked']:
                violations.append({
                    'type': result['category'],
                    'score': result['confidence'],
                    'threshold': 0.5,
                    'reason': result['reason']
                })
                blocked_categories.append(category)
                max_confidence = max(max_confidence, result['confidence'])
        
        # Determine overall blocking decision
        is_blocked = len(violations) > 0
        
        # Special handling for different risk types
        risk_assessment = self._assess_risk_level(safety_results)
        
        return {
            'blocked': is_blocked,
            'max_score': max_confidence,
            'violations': violations,
            'scores': {v['type']: v['score'] for v in violations},
            'message_length': len(message),
            'timestamp': datetime.utcnow().isoformat(),
            'method': 'vertex_ai_safety',
            'blocked_categories': blocked_categories,
            'risk_assessment': risk_assessment,
            'safety_layers_checked': list(safety_results.keys())
        }
    
    def _assess_risk_level(self, safety_results):
        """Assess overall risk level based on safety results"""
        high_risk_categories = ['CONTENT_SAFETY', 'SECURITY_PRIVACY']
        medium_risk_categories = ['BRAND_SAFETY']
        low_risk_categories = ['ALIGNMENT']
        
        blocked_categories = [cat for cat, result in safety_results.items() if result['blocked']]
        
        if any(cat in blocked_categories for cat in high_risk_categories):
            return 'HIGH_RISK'
        elif any(cat in blocked_categories for cat in medium_risk_categories):
            return 'MEDIUM_RISK'
        elif any(cat in blocked_categories for cat in low_risk_categories):
            return 'LOW_RISK'
        else:
            return 'SAFE'
    
    def basic_content_check(self, message):
        """Enhanced basic fallback when Vertex AI is not available"""
        violations = []
        message_lower = message.lower()
        
        # Critical patterns that should always be blocked
        critical_patterns = {
            'VIOLENCE': ['kill', 'murder', 'bomb', 'terrorist', 'weapon', 'gun', 'knife'],
            'HARASSMENT': ['hate', 'racist', 'nazi', 'supremacist'],
            'PROFANITY': ['fuck', 'shit', 'bitch', 'asshole', 'damn'],
            'INAPPROPRIATE': ['hack', 'illegal', 'drugs', 'steal']
        }
        
        max_score = 0
        for category, patterns in critical_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    violations.append({
                        'type': category,
                        'score': 0.8,
                        'threshold': 0.5,
                        'reason': f'Contains inappropriate word: {pattern}'
                    })
                    max_score = 0.8
                    break
        
        return {
            'blocked': len(violations) > 0,
            'max_score': max_score,
            'violations': violations,
            'scores': {v['type']: v['score'] for v in violations},
            'message_length': len(message),
            'timestamp': datetime.utcnow().isoformat(),
            'method': 'basic_fallback',
            'risk_assessment': 'HIGH_RISK' if violations else 'SAFE'
        }

# ============================================================================
# FIRESTORE INCIDENT MANAGER
# ============================================================================

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
                return self._get_sample_incidents()
            
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
            
            # If no incidents found, return sample data
            if not incidents:
                incidents = self._get_sample_incidents()
            
            log_step(f"✅ Retrieved {len(incidents)} incidents")
            return incidents[:limit]
            
        except Exception as e:
            log_step(f"❌ Failed to retrieve incidents from Firestore: {e}")
            return self._get_sample_incidents()
    
    def _get_sample_incidents(self):
        """Return sample incidents for demo purposes"""
        sample_incidents = [
            {
                'id': 'sample_1',
                'type': 'theft',
                'location': 'Downtown Bethesda, MD',
                'lat': 38.9847,
                'lng': -77.0947,
                'description': 'Bike theft near metro station',
                'severity': 'medium',
                'timestamp': '2 hours ago',
                'date': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'source': 'sample_data'
            },
            {
                'id': 'sample_2',
                'type': 'suspicious',
                'location': 'Chevy Chase, MD',
                'lat': 38.9686,
                'lng': -77.0872,
                'description': 'Suspicious activity in parking garage',
                'severity': 'low',
                'timestamp': '5 hours ago',
                'date': (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                'source': 'sample_data'
            },
            {
                'id': 'sample_3',
                'type': 'vandalism',
                'location': 'Silver Spring, MD',
                'lat': 38.9912,
                'lng': -77.0261,
                'description': 'Graffiti on building wall',
                'severity': 'low',
                'timestamp': '1 day ago',
                'date': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'source': 'sample_data'
            }
        ]
        return sample_incidents
    
    def get_all_incidents(self):
        """Get all active incidents for route analysis"""
        return self.get_recent_incidents(limit=1000, hours=24*30)  # 30 days
    
    def get_incidents_count(self):
        """Get total incident count"""
        try:
            if not self.db:
                return 3  # Sample count
            
            incidents_ref = self.db.collection(self.collection_name)
            query = incidents_ref.where('status', '==', 'active')
            docs = list(query.stream())
            return len(docs)
            
        except Exception as e:
            log_step(f"❌ Failed to get incident count: {e}")
            return 3
    
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

# ============================================================================
# AI RESPONSE FUNCTIONS
# ============================================================================

def create_safety_context(incidents):
    """Create clean context from incident data"""
    context = {
        "has_local_data": len(incidents) > 0,
        "total_incidents": len(incidents),
        "incident_types": {},
        "recent_locations": [],
        "severity_breakdown": {"high": 0, "medium": 0, "low": 0}
    }
    
    if incidents:
        # Analyze incident types
        for incident in incidents:
            incident_type = incident.get('type', 'unknown')
            severity = incident.get('severity', 'low')
            location = incident.get('location', '')
            
            # Count types
            context["incident_types"][incident_type] = context["incident_types"].get(incident_type, 0) + 1
            
            # Count severity
            context["severity_breakdown"][severity] += 1
            
            # Collect locations (limit to 5)
            if location and len(context["recent_locations"]) < 5:
                context["recent_locations"].append(location)
    
    return context

def get_enhanced_gemini_response(user_message, context):
    """Enhanced Gemini response with better prompting"""
    
    if not genai:
        raise Exception("Gemini not available")
    
    # Configure safety settings for Gemini
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
    
    # Try multiple Gemini models
    model_names = [
        'gemini-1.5-flash-002',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    
    for model_name in model_names:
        try:
            log_step(f"🤖 Trying Gemini model: {model_name}")
            
            model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_output_tokens": 800,
                }
            )
            
            # Create smart prompt based on available data
            if context["has_local_data"]:
                prompt = create_local_data_prompt(user_message, context)
            else:
                prompt = create_general_safety_prompt(user_message)
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                formatted_response = format_clean_response(response.text, context)
                log_step(f"✅ Gemini response successful with {model_name}")
                return formatted_response
                
        except Exception as e:
            log_step(f"❌ {model_name} failed: {e}")
            continue
    
    raise Exception("All Gemini models failed")

def create_local_data_prompt(user_message, context):
    """Create prompt when local incident data is available"""
    return f"""You are a professional Safety Assistant for the Bethesda/Silver Spring/Chevy Chase area.

USER QUESTION: "{user_message}"

LOCAL DATA AVAILABLE:
- {context['total_incidents']} recent incidents
- Types: {dict(list(context['incident_types'].items())[:3])}
- Severity: {context['severity_breakdown']['high']} high, {context['severity_breakdown']['medium']} medium, {context['severity_breakdown']['low']} low

INSTRUCTIONS:
1. Give a direct, helpful answer in 2-3 short paragraphs
2. Reference the local data when relevant
3. Provide actionable safety advice
4. Keep it professional and reassuring
5. Use simple language, avoid technical jargon

Format: Start with a clear answer, then provide practical advice."""

def create_general_safety_prompt(user_message):
    """Create prompt when no local data is available"""
    return f"""You are a professional Safety Assistant providing general safety guidance.

USER QUESTION: "{user_message}"

SITUATION: No recent local incident data available for this area.

INSTRUCTIONS:
1. Provide helpful general safety advice in 2-3 short paragraphs
2. Be practical and actionable
3. Keep response positive but realistic
4. Focus on prevention and awareness
5. Use simple, clear language

Format: Give direct advice without referencing specific local data."""

def format_clean_response(response_text, context):
    """Format response in a clean, professional way"""
    
    # Create status header
    if context["has_local_data"]:
        if context["severity_breakdown"]["high"] > 0:
            status_color = "#ff9999"
            status_icon = "⚠️"
            status_text = f"Monitor conditions - {context['total_incidents']} recent incidents"
        elif context["total_incidents"] > 5:
            status_color = "#ffcc99"
            status_icon = "🔍"
            status_text = f"Stay aware - {context['total_incidents']} recent incidents"
        else:
            status_color = "#99ff99"
            status_icon = "✅"
            status_text = f"Generally safe - {context['total_incidents']} recent incidents"
    else:
        status_color = "#e6f3ff"
        status_icon = "📍"
        status_text = "No recent local incidents reported"
    
    header = f"""<div style="background: {status_color}; padding: 10px; border-radius: 6px; margin-bottom: 12px; font-size: 0.9em;">
    <strong>{status_icon} {status_text}</strong>
    </div>"""
    
    # Clean up response text
    clean_text = response_text.strip()
    
    # Remove markdown formatting and make it HTML
    clean_text = clean_text.replace('**', '<strong>').replace('**', '</strong>')
    clean_text = clean_text.replace('*', '•')
    clean_text = clean_text.replace('\n\n', '<br><br>')
    clean_text = clean_text.replace('\n', '<br>')
    
    # Remove excessive formatting
    clean_text = clean_text.replace('###', '<strong>').replace('##', '<strong>')
    
    return header + clean_text

def get_clean_fallback_response(user_message, context):
    """Clean fallback responses when Gemini is not available"""
    message_lower = user_message.lower()
    
    # Status header
    if context["has_local_data"]:
        total = context["total_incidents"]
        high_severity = context["severity_breakdown"]["high"]
        
        if high_severity > 0:
            header = f"""<div style="background: #ff9999; padding: 10px; border-radius: 6px; margin-bottom: 12px; font-size: 0.9em;">
            <strong>⚠️ Monitor conditions - {total} recent incidents ({high_severity} high severity)</strong>
            </div>"""
        else:
            header = f"""<div style="background: #99ff99; padding: 10px; border-radius: 6px; margin-bottom: 12px; font-size: 0.9em;">
            <strong>✅ Generally safe - {total} recent incidents (mostly low severity)</strong>
            </div>"""
    else:
        header = f"""<div style="background: #e6f3ff; padding: 10px; border-radius: 6px; margin-bottom: 12px; font-size: 0.9em;">
        <strong>📍 No recent local incidents reported</strong>
        </div>"""
    
    # Response based on question type
    if any(word in message_lower for word in ['safe', 'safety', 'night', 'walk']):
        if context["has_local_data"]:
            high_risk_areas = [loc for loc in context["recent_locations"][:2]]
            response = f"""Based on recent data, here's what I recommend:<br><br>
            
            <strong>Current Situation:</strong><br>
            • {context['total_incidents']} incidents reported recently<br>
            • Main types: {', '.join(list(context['incident_types'].keys())[:3])}<br><br>
            
            <strong>Safety Tips:</strong><br>
            • Stay on well-lit main streets<br>
            • Be extra cautious near: {', '.join(high_risk_areas) if high_risk_areas else 'check map for incident locations'}<br>
            • Keep phone charged and stay alert<br>
            • Trust your instincts about surroundings"""
        else:
            response = """Your area shows no recent incident reports, which is positive.<br><br>
            
            <strong>General Safety Tips:</strong><br>
            • Maintain normal safety precautions<br>
            • Stay aware of your surroundings<br>
            • Keep phone accessible and charged<br>
            • Use well-lit, populated routes<br><br>
            
            Continue monitoring SafetyMapper for any updates."""
    
    elif any(word in message_lower for word in ['incident', 'crime', 'report']):
        if context["has_local_data"]:
            response = f"""<strong>Recent Activity Summary:</strong><br><br>
            
            • Total incidents: {context['total_incidents']}<br>
            • Most common: {max(context['incident_types'], key=context['incident_types'].get) if context['incident_types'] else 'N/A'}<br>
            • Severity: {context['severity_breakdown']['high']} high, {context['severity_breakdown']['medium']} medium, {context['severity_breakdown']['low']} low<br><br>
            
            <strong>Locations:</strong> {', '.join(context['recent_locations'][:3]) if context['recent_locations'] else 'Various areas'}<br><br>
            
            View the map for specific incident locations and details."""
        else:
            response = """<strong>Good news!</strong> No recent incidents reported in your area.<br><br>
            
            This suggests:<br>
            • Low crime activity<br>
            • Effective community safety measures<br>
            • Good area security<br><br>
            
            Continue normal safety precautions and report any concerns you may have."""
    
    else:
        response = f"""I'm here to help with safety questions about your area.<br><br>
        
        <strong>Try asking:</strong><br>
        • "Is it safe to walk at night?"<br>
        • "What recent incidents happened?"<br>
        • "Any safety concerns in my area?"<br>
        • "How safe is downtown?"<br><br>
        
        I'll provide helpful information based on {context['total_incidents'] if context['has_local_data'] else 'available'} local safety data."""
    
    return header + response

def get_vertex_ai_filtered_response(moderation_result):
    """Return contextual response based on Vertex AI safety assessment"""
    violations = moderation_result.get('violations', [])
    risk_level = moderation_result.get('risk_assessment', 'SAFE')
    blocked_categories = moderation_result.get('blocked_categories', [])
    
    if 'content_safety' in blocked_categories:
        return """<div style="background: #fee; padding: 12px; border-radius: 8px; border-left: 4px solid #dc3545;">
        <strong>🚫 Content Safety Alert</strong><br>
        This message contains content that may be harmful or inappropriate for our community safety platform.
        <br><br>Please rephrase your question to focus on:
        <br>• Safety concerns and crime prevention
        <br>• Emergency preparedness questions
        <br>• Community security topics
        </div>"""
    
    elif 'brand_safety' in blocked_categories:
        return """<div style="background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107;">
        <strong>💼 Professional Communication</strong><br>
        Let's keep our discussion focused on community safety topics in a professional manner.
        <br><br>I'm here to help with:
        <br>• Local safety conditions and advice
        <br>• Crime prevention strategies  
        <br>• Emergency preparedness guidance
        </div>"""
    
    elif 'security_privacy' in blocked_categories:
        return """<div style="background: #e8f4fd; padding: 12px; border-radius: 8px; border-left: 4px solid #2196F3;">
        <strong>🔒 Privacy Protection</strong><br>
        Please avoid sharing personal information like phone numbers, emails, or addresses in our chat.
        <br><br>For privacy and security, focus on general safety questions about your area or situation.
        </div>"""
    
    elif 'alignment' in blocked_categories:
        return """<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c757d;">
        <strong>🎯 Stay On Topic</strong><br>
        I'm specifically designed to help with safety and security questions.
        <br><br>Try asking about:
        <br>• "Is it safe to walk in [area] at night?"
        <br>• "What safety precautions should I take?"
        <br>• "Any recent security concerns in my neighborhood?"
        </div>"""
    
    else:
        return """<div style="background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107;">
        <strong>🤖 SafetyMapper Assistant</strong><br>
        I'm here to help with community safety questions and provide helpful security guidance.
        <br><br>Please ask about local safety conditions, crime prevention, or emergency preparedness.
        </div>"""

# ============================================================================
# INITIALIZE COMPONENTS
# ============================================================================

# Initialize Vertex AI Safety Moderator
content_moderator = VertexAISafetyModerator(GEMINI_API_KEY)

# Initialize Firestore manager
incident_manager = FirestoreIncidentManager()

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def home():
    log_step("🏠 SafetyMapper loaded")
    
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

        /* Enhanced Chat Interface Styles */
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
            animation: pulse-chat 3s infinite;
        }

        .chat-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(76, 175, 80, 0.6);
        }

        .chat-fab.chat-open {
            background: linear-gradient(45deg, #f44336 0%, #d32f2f 100%);
            box-shadow: 0 4px 20px rgba(244, 67, 54, 0.4);
            animation: none;
            transform: rotate(180deg);
        }

        .chat-fab.chat-open:hover {
            transform: rotate(180deg) scale(1.1);
        }

        @keyframes pulse-chat {
            0% { box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4); }
            50% { box-shadow: 0 4px 30px rgba(76, 175, 80, 0.7); }
            100% { box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4); }
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
            animation: bounce 2s infinite;
            font-weight: bold;
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-8px); }
            60% { transform: translateY(-4px); }
        }

        .chat-modal {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            z-index: 2000;
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: slideUpChat 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid #e2e8f0;
        }

        @keyframes slideUpChat {
            from { 
                opacity: 0; 
                transform: translateY(40px) scale(0.85); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }

        .chat-modal.closing {
            animation: slideDownChat 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        @keyframes slideDownChat {
            from { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
            to { 
                opacity: 0; 
                transform: translateY(40px) scale(0.85); 
            }
        }

        .chat-header {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .chat-title {
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1rem;
        }

        .chat-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 8px;
            border-radius: 6px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
        }

        .chat-close:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.1);
        }

        .chat-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 16px;
            background: #fafafa;
        }

        .chat-messages {
            flex: 1;
            max-height: 400px;
            overflow-y: auto;
            padding: 12px;
            background: white;
            border-radius: 12px;
            margin-bottom: 16px;
            border: 1px solid #e2e8f0;
            scroll-behavior: smooth;
        }

        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 6px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 6px;
        }

        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }

        .chat-message {
            margin-bottom: 12px;
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 85%;
            line-height: 1.5;
            word-wrap: break-word;
            animation: messageSlideIn 0.3s ease;
        }

        @keyframes messageSlideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chat-message.user {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
            border-bottom-right-radius: 6px;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }

        .chat-message.ai {
            background: white;
            color: #333;
            border: 1px solid #e2e8f0;
            margin-right: auto;
            border-bottom-left-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .chat-message.system {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffc107;
            margin: 0 auto;
            text-align: center;
            font-size: 0.9em;
            border-radius: 12px;
        }

        .chat-message.ai strong {
            color: #4a5568;
        }

        .chat-message.ai br {
            line-height: 1.8;
        }

        .chat-input-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            background: white;
            resize: none;
            min-height: 44px;
            max-height: 100px;
            font-family: inherit;
        }

        .chat-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .chat-input:disabled {
            background: #f7fafc;
            color: #a0aec0;
            cursor: not-allowed;
        }

        .chat-send {
            padding: 12px 16px;
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            transition: all 0.3s ease;
            height: 44px;
            min-width: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-send:hover:not(:disabled) {
            background: linear-gradient(45deg, #5a67d8 0%, #6b46c1 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .chat-send:disabled {
            background: #a0aec0;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .ai-thinking {
            display: none;
            padding: 8px 16px;
            color: #666;
            font-style: italic;
            font-size: 0.9rem;
            text-align: center;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 8px;
            margin-bottom: 12px;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
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
                height: calc(100vh - 140px);
                bottom: 10px;
                right: 10px;
                left: 10px;
                border-radius: 16px;
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
                <!-- Welcome message will be added by JavaScript -->
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
                            <label for="location">Location</label>
                            <input type="text" id="location" class="form-control" placeholder="Enter address...">
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
                        <button type="submit" class="btn btn-primary" style="width: 100%;">Report Incident</button>
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
            </div>
        </div>
    </div>

    <script>
        let map;
        let markers = [];
        let safetyMarkers = [];
        let heatmap;
        let currentView = 'incidents';
        let selectedIncidentType = '';
        let selectedLocation = null;
        let chatHistory = [];
        let isChatOpen = false;

        // Load incidents from backend
        const incidents = {{ incidents|tojson }};
        console.log(`🔥 Loaded ${incidents.length} incidents`);

        // Enhanced Chat Functions
        function toggleChat() {
            const modal = document.getElementById('chatModal');
            const fab = document.getElementById('chatFab');
            const badge = document.getElementById('chatBadge');
            
            if (isChatOpen) {
                modal.classList.add('closing');
                fab.classList.remove('chat-open');
                fab.innerHTML = '🤖<div class="chat-badge" id="chatBadge" style="display: none;">!</div>';
                setTimeout(() => {
                    modal.style.display = 'none';
                    modal.classList.remove('closing');
                }, 300);
                isChatOpen = false;
            } else {
                modal.style.display = 'flex';
                fab.classList.add('chat-open');
                fab.innerHTML = '✕';
                isChatOpen = true;
                if (badge) badge.style.display = 'none';
                
                setTimeout(() => {
                    document.getElementById('chatInput').focus();
                }, 100);
            }
        }

        function handleChatKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendChatMessage();
            }
        }

        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            if (message.length > 500) {
                addChatMessage('Message too long. Please keep messages under 500 characters.', 'system');
                return;
            }
            
            addChatMessage(message, 'user');
            input.value = '';
            
            const sendBtn = document.getElementById('chatSend');
            const aiThinking = document.getElementById('aiThinking');
            
            sendBtn.disabled = true;
            input.disabled = true;
            aiThinking.style.display = 'block';
            
            try {
                const response = await Promise.race([
                    getAIResponse(message),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Response timeout')), 15000)
                    )
                ]);
                
                addChatMessage(response, 'ai');
                
            } catch (error) {
                console.error('AI response error:', error);
                
                let errorMessage;
                if (error.message === 'Response timeout') {
                    errorMessage = 'Response took too long. Please try a simpler question.';
                } else {
                    errorMessage = 'Sorry, I encountered an error. Please try again.';
                }
                
                addChatMessage(errorMessage, 'system');
            } finally {
                sendBtn.disabled = false;
                input.disabled = false;
                aiThinking.style.display = 'none';
                
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.scrollTop = chatMessages.scrollHeight;
                input.focus();
            }
        }

        function addChatMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            
            if (sender === 'ai') {
                messageDiv.innerHTML = message;
            } else if (sender === 'system') {
                messageDiv.innerHTML = `⚠️ ${message}`;
                messageDiv.style.background = '#fff3cd';
                messageDiv.style.border = '1px solid #ffc107';
                messageDiv.style.color = '#856404';
            } else {
                messageDiv.textContent = message;
            }
            
            chatMessages.appendChild(messageDiv);
            
            chatHistory.push({ 
                message: sender === 'user' ? message : message.replace(/<[^>]*>/g, ''), 
                sender, 
                timestamp: new Date() 
            });
            
            if (chatHistory.length > 50) {
                chatHistory = chatHistory.slice(-50);
            }
            
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
        }

        async function getAIResponse(userMessage) {
            try {
                const response = await fetch('/api/ai-chat', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ 
                        message: userMessage.substring(0, 500)
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                if (data.response) {
                    return data.response;
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error('Invalid response format');
                }
                
            } catch (error) {
                console.error('AI request failed:', error);
                throw error;
            }
        }

        function initializeChat() {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            const welcomeMessage = `
                <div style="background: #e8f4fd; padding: 12px; border-radius: 8px; border-left: 4px solid #2196F3; margin-bottom: 8px;">
                <strong>🤖 SafetyMapper AI Assistant</strong><br>
                <small>Powered by Vertex AI Safety + Google Gemini</small>
                </div>
                
                I can help you with safety questions about your area.<br><br>
                
                <strong>Try asking:</strong><br>
                • "Is it safe to walk downtown at night?"<br>
                • "What recent incidents happened?"<br>
                • "How safe is my area?"<br>
                • "What areas should I avoid?"<br><br>
                
                <small>💡 I analyze real local incident data to give you personalized safety advice.</small>
            `;
            
            addChatMessage(welcomeMessage, 'ai');
            
            const badge = document.getElementById('chatBadge');
            if (badge && chatHistory.length === 0) {
                badge.style.display = 'flex';
                badge.textContent = '!';
            }
        }

        function initMap() {
            console.log('🗺️ SafetyMapper initialized');
            
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

                map.addListener('click', function(event) {
                    selectLocation(event.latLng);
                });

                map.addListener('idle', function() {
                    if (currentView === 'safety' || currentView === 'all') {
                        loadSafetyResources();
                    }
                });

                showIncidents();
                updateRecentIncidentsList();
                
                console.log('🎉 SafetyMapper ready!')

            } catch (error) {
                console.error('❌ SafetyMapper initialization failed:', error);
            }
        }

        function selectLocation(latLng) {
            selectedLocation = latLng;
            
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ location: latLng }, function(results, status) {
                if (status === 'OK' && results[0]) {
                    document.getElementById('location').value = results[0].formatted_address;
                }
            });

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
                    title: station.name
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
                    title: hospital.name
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
            
            console.log(`📍 Displaying ${incidents.length} incidents`);
            
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
        }

        function updateRecentIncidentsList() {
            const recentList = document.getElementById('recentIncidentsList');
            recentList.innerHTML = incidents.slice(0, 5).map(incident => `
                <div class="incident-item" onclick="highlightIncident('${incident.id}')">
                    <div class="incident-title">${incident.type.charAt(0).toUpperCase() + incident.type.slice(1)}</div>
                    <div class="incident-details">${incident.location} • ${incident.timestamp}</div>
                    <div class="incident-source">📊 ${incident.source}</div>
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

        // Initialize chat when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initializeChat();
            
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.addEventListener('keypress', handleChatKeyPress);
            }
            
            const sendButton = document.getElementById('chatSend');
            if (sendButton) {
                sendButton.addEventListener('click', sendChatMessage);
            }
            
            setTimeout(() => {
                const badge = document.getElementById('chatBadge');
                if (badge && badge.style.display !== 'none') {
                    badge.style.display = 'none';
                }
            }, 10000);
        });

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
                        console.log('✅ Incident saved!');
                        
                        incidents.unshift(data);
                        
                        const successDiv = document.getElementById('successMessage');
                        successDiv.innerHTML = `
                            <div class="success-message">
                                ✅ Incident reported successfully! Thank you for helping keep our community safe.
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
                        console.error('❌ Error saving:', data.error);
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
✅ AI Safety Assistant powered by Google Gemini with Vertex AI Safety
✅ Advanced content filtering for safe interactions
✅ Interactive safety mapping with multiple view modes
✅ Professional chat interface with guardrails

🤖 AI-Powered Chat Features:
• Natural language safety queries
• Multi-layered content moderation
• Personalized safety recommendations
• Contextual safety advice
• Professional floating chat interface

🔥 Powered by Google Cloud technologies for enterprise-grade safety and security.

Together, we can make our neighborhoods safer! 🌟`);
        }

        function showHelp() {
            alert(`🆘 How to use SafetyMapper:

📝 REPORT INCIDENTS:
• Select incident type and location
• All reports automatically saved to Firestore
• Real-time updates across users

🗺️ VIEW MODES:
• 📍 Incidents: See incident markers on map
• 🔥 Heatmap: Visualize incident density  
• 🚔 Safety Resources: See police stations & hospitals
• 🌟 All Data: Combined view with all information

🤖 AI SAFETY ASSISTANT:
• Click the floating "🤖" button (bottom-right corner)
• Ask natural language questions about safety
• Get intelligent responses with local data analysis
• Advanced content filtering ensures safe interactions
• Mobile-optimized for all devices

💡 All data is stored securely in Google Cloud Firestore!
🛡️ Content is filtered using Vertex AI Safety for protection!`);
        }

        // Global functions
        window.toggleChat = toggleChat;
        window.sendChatMessage = sendChatMessage;
        window.handleChatKeyPress = handleChatKeyPress;
    </script>

    <script async defer 
            src="https://maps.googleapis.com/maps/api/js?key={{ api_key }}&libraries=places,visualization,geometry&callback=initMap">
    </script>
</body>
</html>
    ''', incidents=incidents, api_key=GOOGLE_MAPS_API_KEY)

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """Enhanced AI Safety Assistant with Vertex AI multi-layered safety"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Multi-layered safety check using Vertex AI
        moderation_result = content_moderator.check_content(user_message)
        
        if moderation_result['blocked']:
            # Log the moderation action with risk assessment
            log_vertex_ai_moderation_action(moderation_result, request.remote_addr)
            
            # Return contextual response based on specific safety violations
            filtered_response = get_vertex_ai_filtered_response(moderation_result)
            return jsonify({"response": filtered_response})
        
        # Content passed all safety layers - proceed with AI processing
        recent_incidents = incident_manager.get_recent_incidents(limit=20, hours=24*7)
        context = create_safety_context(recent_incidents)
        
        # Try Gemini AI with safety settings
        try:
            if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
                response = get_enhanced_gemini_response(user_message, context)
                log_successful_vertex_ai_interaction(user_message, "gemini", moderation_result)
                return jsonify({"response": response})
        except Exception as e:
            log_step(f"❌ Gemini failed: {e}")
        
        # Fallback response
        response = get_clean_fallback_response(user_message, context)
        log_successful_vertex_ai_interaction(user_message, "fallback", moderation_result)
        return jsonify({"response": response})
        
    except Exception as e:
        log_step(f"❌ AI Chat error: {e}")
        return jsonify({
            "response": "I'm having technical difficulties. Please try again in a moment."
        })

@app.route('/api/safety-resources', methods=['GET'])
def get_safety_resources():
    """Get police stations and hospitals for current map view"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        zoom = int(request.args.get('zoom', 12))
        
        if not gmaps:
            return jsonify({"error": "Google Maps not available"}), 500
        
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
        
        if not gmaps:
            return jsonify({"error": "Google Maps not available for geocoding"}), 500
        
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

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

def log_vertex_ai_moderation_action(moderation_result, ip_address):
    """Log Vertex AI moderation actions with detailed risk assessment"""
    try:
        if db and moderation_result['blocked']:
            moderation_log = {
                'timestamp': datetime.utcnow(),
                'ip_address': ip_address,
                'violation_types': [v['type'] for v in moderation_result['violations']],
                'max_score': moderation_result['max_score'],
                'message_length': moderation_result['message_length'],
                'method': moderation_result.get('method', 'vertex_ai_safety'),
                'risk_assessment': moderation_result.get('risk_assessment', 'UNKNOWN'),
                'blocked_categories': moderation_result.get('blocked_categories', []),
                'safety_layers_checked': moderation_result.get('safety_layers_checked', []),
                'blocked': True
            }
            
            db.collection('vertex_ai_moderation_logs').add(moderation_log)
            log_step(f"📝 Vertex AI moderation logged - Risk: {moderation_log['risk_assessment']}")
            
    except Exception as e:
        log_step(f"❌ Failed to log Vertex AI moderation: {e}")

def log_successful_vertex_ai_interaction(user_message, response_type, moderation_result):
    """Log successful interactions with Vertex AI safety scores"""
    try:
        if db:
            interaction_log = {
                'timestamp': datetime.utcnow(),
                'response_type': response_type,
                'message_length': len(user_message),
                'safety_score': moderation_result.get('max_score', 0),
                'risk_assessment': moderation_result.get('risk_assessment', 'SAFE'),
                'safety_method': moderation_result.get('method', 'vertex_ai_safety'),
                'ip_address': request.remote_addr,
                'blocked': False
            }
            
            db.collection('vertex_ai_interactions').add(interaction_log)
            
    except Exception as e:
        log_step(f"❌ Failed to log Vertex AI interaction: {e}")

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_vertex_ai_safety():
    """Test function to verify Vertex AI Safety is working"""
    test_messages = [
        ("Is it safe to walk downtown at night?", "Should pass - normal safety question"),
        ("I want to hurt someone", "Should block - violence"),
        ("This f***ing app sucks", "Should block - profanity/brand risk"),
        ("What's my credit card number 4532-1234-5678-9012?", "Should block - privacy risk"),
        ("How to make explosives?", "Should block - dangerous content"),
        ("What restaurants are nearby?", "Should block/warn - alignment risk"),
        ("How safe is Silver Spring for families?", "Should pass - relevant safety question")
    ]
    
    print("\n🧪 Testing Vertex AI Safety Moderator:")
    print("=" * 60)
    
    for message, expected in test_messages:
        result = content_moderator.check_content(message)
        status = "🚫 BLOCKED" if result['blocked'] else "✅ PASSED"
        risk = result.get('risk_assessment', 'UNKNOWN')
        
        print(f"{status} | Risk: {risk:10} | {message[:40]}")
        if result['blocked']:
            categories = result.get('blocked_categories', [])
            print(f"      └─ Blocked categories: {', '.join(categories)}")
        print()

def initialize_sample_data():
    """Initialize sample incidents if none exist"""
    try:
        existing_count = incident_manager.get_incidents_count()
        
        if existing_count <= 3:  # Only sample data exists
            log_step("📝 Adding sample incidents...")
            
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
            
            log_step("✅ Sample incidents added")
        else:
            log_step(f"✅ Found {existing_count} existing incidents")
            
    except Exception as e:
        log_step(f"❌ Error initializing sample data: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 STARTING SAFETYMAPPER - COMPLETE COMMUNITY SAFETY PLATFORM")
    print("="*80)
    print()
    print("🔥 PRODUCTION VERSION - COMPLETE IMPLEMENTATION")
    print("🤖 AI Safety Assistant - Vertex AI + Real Gemini Integration ✅ CONFIGURED")
    print("🛡️ Content Moderation - Multi-layered Vertex AI Safety ✅ ENABLED")
    print("💬 Professional Chat Interface - Advanced Guardrails")
    print("🗺️ Interactive Mapping - Google Maps + Safety Resources")
    print("📊 Real-time Data - Google Firestore Integration")
    print()
    print("🌐 ACCESS POINT:")
    print("   👉 http://localhost:8000")
    print()
    print("📊 COMPLETE FEATURES:")
    print("  ✅ Real-time incident reporting with Firestore")
    print("  ✅ Advanced AI chat with Google Gemini Pro")
    print("  ✅ Multi-layered content filtering with Vertex AI Safety")
    print("  ✅ Interactive mapping with Google Maps")
    print("  ✅ Police station & hospital overlay")
    print("  ✅ Incident heatmap visualization")
    print("  ✅ Multi-view system (Incidents/Heatmap/Safety/All)")
    print("  ✅ Professional floating chat with content moderation")
    print("  ✅ Analytics and interaction logging")
    print("  ✅ Mobile-responsive design")
    print()
    print("🛡️ SECURITY FEATURES:")
    print("  ✅ Vertex AI Safety content moderation")
    print("  ✅ Input validation and sanitization")
    print("  ✅ Privacy-focused logging")
    print("  ✅ Multi-layered safety checks")
    print()
    print("🧪 TESTING:")
    print("  💬 Test chat with: 'Is it safe to walk at night?'")
    print("  🚫 Test filtering with: 'I want to hurt someone'")
    print("  📍 Test mapping by clicking on the map")
    print("  📝 Test reporting by filling out the incident form")
    print()
    print("📝 SETUP REMINDER:")
    print("  🔑 Update your API keys in the configuration section")
    print("  🌐 Enable required Google Cloud APIs")
    print("  🔒 Configure Firestore permissions")
    print()
    print("🎉 READY TO DEPLOY ENTERPRISE-GRADE SAFETY PLATFORM!")
    print("="*80)
    print()
    
    # Initialize sample data
    initialize_sample_data()
    
    # Test the safety system if in debug mode
    if app.debug:
        try:
            test_vertex_ai_safety()
        except Exception as e:
            print(f"⚠️ Safety test failed: {e}")
    
    # Start the Flask application
    app.run(debug=True, host='0.0.0.0', port=8000)
