import openai
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. AI service will not function properly.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
        
    def completion(self, html_content: str, url: str, display_name: str) -> str:
        """
        Convert HTML content to Markdown using AI completion.
        
        Args:
            html_content: The full HTML content to convert
            url: The source URL of the content
            display_name: The display name for the content
            
        Returns:
            Converted Markdown content
        """
        
        if not self.client:
            # Fallback when no API key is available
            logger.warning("OpenAI client not initialized. Returning fallback content.")
            return f"""# {display_name}

**Source:** {url}

*Note: AI conversion is not available due to missing OpenAI API key. Please set OPENAI_API_KEY environment variable.*

## Original Content
The HTML content was successfully collected but could not be converted to Markdown without an OpenAI API key.

To enable AI conversion:
1. Obtain an OpenAI API key from https://platform.openai.com/api-keys
2. Set the environment variable: `export OPENAI_API_KEY="your-key-here"`
3. Restart the server
"""
        
        system_prompt = """You are an expert at converting web page HTML content to clean, well-formatted Markdown.

Your task is to:
1. Extract the main content from the HTML, ignoring navigation, ads, sidebars, and other non-essential elements
2. Convert the content to clean, readable Markdown format
3. Preserve important structure like headings, lists, links, and code blocks
4. Remove HTML noise like script tags, style tags, and excessive whitespace
5. Maintain the logical flow and hierarchy of the content
6. Include the page title as the main heading if appropriate

Focus on the core content that would be valuable for documentation or reference purposes."""

        user_prompt = f"""Please convert the following HTML content to Markdown:

Source URL: {url}
Display Name: {display_name}

HTML Content:
{html_content}

Return only the clean Markdown content, no additional commentary."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            markdown_content = response.choices[0].message.content
            logger.info(f"Successfully converted HTML to Markdown for {display_name}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")


# Global instance
ai_service = AIService()