"""Service for interacting with Google Gemini API"""
import os
import json
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GeminiService:
    """Service class for Google Gemini API interactions"""
    
    def __init__(self):
        """Initialize Gemini service with API key"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        # Available models: gemini-pro, gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set in environment variables")
        else:
            logger.info(f"Initialized Gemini service with model: {self.model_name}")
    
    def call_gemini(self, prompt: str, is_json: bool = True) -> Optional[Any]:
        """Call Google Gemini API with a prompt
        
        Args:
            prompt: The prompt to send to Gemini
            is_json: Whether to parse the response as JSON (default: True)
            
        Returns:
            Parsed JSON response if is_json=True, otherwise raw text response
            Returns None if API call fails
        """
        if not self.api_key:
            logger.error("GEMINI_API_KEY not configured")
            return None
        
        try:
            # Prepare request payload
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            # Add JSON response format if needed
            if is_json:
                payload["generationConfig"] = {
                    "response_mime_type": "application/json"
                }
            
            # Make API request
            url = f"{self.base_url}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            logger.info(f"Making request to Gemini API (model: {self.model_name}, is_json={is_json})")
            logger.debug(f"Request URL: {self.base_url.split('?')[0]}")  # Log without API key
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Check response status
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Gemini API returned status {response.status_code}")
                logger.error(f"Error details: {error_text}")
                
                # Try to parse error for more details
                try:
                    error_json = response.json()
                    if 'error' in error_json:
                        error_msg = error_json['error'].get('message', 'Unknown error')
                        logger.error(f"API Error: {error_msg}")
                except:
                    pass
                
                return None
            
            # Parse response
            response_data = response.json()
            
            # Extract text from response
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                candidate = response_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text_content = candidate['content']['parts'][0].get('text', '')
                    
                    if is_json:
                        # Try to parse as JSON
                        try:
                            # Remove markdown code blocks if present
                            text_content = text_content.strip()
                            if text_content.startswith('```json'):
                                text_content = text_content[7:]
                            if text_content.startswith('```'):
                                text_content = text_content[3:]
                            if text_content.endswith('```'):
                                text_content = text_content[:-3]
                            text_content = text_content.strip()
                            
                            parsed_json = json.loads(text_content)
                            logger.info("Successfully parsed JSON response from Gemini")
                            return parsed_json
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON response: {e}")
                            logger.error(f"Response text: {text_content[:200]}")
                            return None
                    else:
                        # Return raw text
                        return text_content
            
            logger.error("Unexpected response format from Gemini API")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception when calling Gemini API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when calling Gemini API: {str(e)}")
            return None
