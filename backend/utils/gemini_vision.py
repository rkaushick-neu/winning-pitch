import os
import base64
import io
from openai import OpenAI
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiVisionClient:
    def __init__(self):
        """Initialize the Gemini Vision client using OpenRouter."""
        self.api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPEN_ROUTER_API_KEY environment variable is required")
        
        # Initialize OpenAI client for OpenRouter
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    def caption_image(self, image_base64: str, prompt: str = None) -> Optional[str]:
        """
        Send a base64 image to Gemini Vision via OpenRouter and get a caption.
        
        Args:
            image_base64: Base64 encoded image string (with or without data URL prefix)
            prompt: Optional custom prompt for captioning
            
        Returns:
            Caption text or None if failed
        """
        try:
            # Clean the base64 string (remove data URL prefix if present)
            # if image_base64.startswith("data:image/"):
            #     image_base64 = image_base64.split(",")[1]
            
            # Default prompt for image captioning
            if not prompt:
                prompt = "Describe this image in detail. Focus on the content, text, charts, diagrams, or any visual elements that would be important for understanding the context."
            
            # # Decode base64 image to bytes
            # image_bytes = base64.b64decode(image_base64)
            
            # # Construct messages with binary image data
            # messages = [
            #     {
            #         "role": "user",
            #         "content": [
            #             {
            #                 "type": "text",
            #                 "text": prompt
            #             },
            #             {
            #                 "type": "image",
            #                 "image": image_bytes
            #             }
            #         ]
            #     }
            # ]

            # Ensure image is formatted as base64 data URL
            # image_data_url = f"data:image/jpeg;base64,{image_base64}"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        }
                    ]
                }
            ]
            
            # Make the API call to Gemini Vision via OpenRouter
            response = self.client.chat.completions.create(
                model="google/gemini-2.5-flash-image-preview",
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            caption = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated caption: {caption[:100]}...")
            return caption
            
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return None
    
    def batch_caption_images(self, image_data_list: list) -> dict:
        """
        Process multiple images and return captions.
        
        Args:
            image_data_list: List of dicts with 'id' and 'image_base64' keys
            
        Returns:
            Dict mapping image IDs to captions
        """
        results = {}
        
        for image_data in image_data_list:
            image_id = image_data.get('id')
            image_base64 = image_data.get('image_base64')
            
            if not image_id or not image_base64:
                logger.warning(f"Skipping image with missing data: {image_data}")
                continue
            
            caption = self.caption_image(image_base64)
            if caption:
                results[image_id] = caption
            else:
                logger.warning(f"Failed to generate caption for image: {image_id}")
                results[image_id] = f"[Image caption failed for {image_id}]"
        
        return results

# Convenience function for direct usage
def get_image_caption(image_base64: str, prompt: str = None) -> Optional[str]:
    """
    Convenience function to get a single image caption.
    
    Args:
        image_base64: Base64 encoded image string
        prompt: Optional custom prompt
        
    Returns:
        Caption text or None if failed
    """
    try:
        client = GeminiVisionClient()
        return client.caption_image(image_base64, prompt)
    except Exception as e:
        logger.error(f"Error initializing Gemini Vision client: {str(e)}")
        return None
