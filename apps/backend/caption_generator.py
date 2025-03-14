import openai
import os
from typing import List, Optional
from flask import request, jsonify

class CaptionGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = self.api_key

    def generate_captions(self, video_type: str, num_captions: int = 3) -> List[str]:
        """
        Generate engaging TikTok overlay captions for a video.
        
        Args:
            video_type (str): Type of video to generate captions for
            num_captions (int): Number of captions to generate (default: 3)
            
        Returns:
            List[str]: List of generated captions
        """
        prompt = f"""Generate {num_captions} highly engaging TikTok overlay captions for a {video_type} video.
Keep each caption under 10 words, short, snappy, no hashtags or emojis, and attention-grabbing.
Use **current TikTok slang, humor, or viral phrases**.
- Make them feel **relatable, funny, or emotionally engaging**.
- Incorporate **hooks, rhetorical questions, or call-to-actions (CTAs)** to boost engagement.
- If relevant, include text formatting to enhance readability.
- Format the response as a **numbered list**, with each caption on a new line.
- Only include the captions no extra explanations, disclaimers, or formatting notes.
        """

        try:
            # Use the appropriate OpenAI client based on the installed version
            try:
                # For newer versions of the OpenAI library
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a creative assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                captions_text = response.choices[0].message.content.strip()
            except AttributeError:
                # For older versions of the OpenAI library
                response = openai.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a creative assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                captions_text = response['choices'][0]['message']['content'].strip()

            # Split by newlines and clean up numbering
            captions = [
                line.split(". ", 1)[1] if ". " in line else line
                for line in captions_text.split("\n")
                if line.strip()
            ]

            return captions

        except Exception as e:
            # Throw the error instead of returning an empty list
            raise Exception(f"Error generating captions: {str(e)}")

    def save_captions_to_file(self, captions: List[str], output_file: str = "captions.txt") -> Optional[str]:
        """
        Save generated captions to a file.
        
        Args:
            captions (List[str]): List of captions to save
            output_file (str): Path to output file
            
        Returns:
            Optional[str]: Path to saved file or None if error occurs
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for i, caption in enumerate(captions, 1):
                    f.write(f"{i}. {caption}\n")
            return output_file
        except Exception as e:
            raise Exception(f"Error saving captions: {str(e)}")

    def generate_captions_from_prompt(self, prompt: str, num_captions: int = 3) -> List[str]:
        """
        Generate captions based on a prompt string.
        
        Args:
            prompt (str): The prompt to generate captions for
            num_captions (int): Number of captions to generate (default: 3)
            
        Returns:
            List[str]: List of generated captions
        """
        if not prompt:
            raise ValueError("Prompt is required")
        
        return self.generate_captions(prompt, num_captions)
