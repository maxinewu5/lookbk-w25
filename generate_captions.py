import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_captions(video_type: str, output_file="captions.txt"):
    prompt = f"""Generate 15 highly engaging TikTok overlay captions for a {video_type} video.
Keep each caption under 10 words, short, snappy, no hashtags or emojis, and attention-grabbing.
Use **current TikTok slang, humor, or viral phrases**.
- Make them feel **relatable, funny, or emotionally engaging**.
- Incorporate **hooks, rhetorical questions, or call-to-actions (CTAs)** to boost engagement.
- If relevant, include text formatting to enhance readability.
- Format the response as a **numbered list**, with each caption on a new line.
- Only include the captions no extra explanations, disclaimers, or formatting notes.
    """

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # Or "gpt-3.5-turbo" if needed
        messages=[{"role": "system", "content": "You are a creative assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )

    captions = response.choices[0].message.content.strip()

    if captions:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(captions)
        print(f"Captions saved to {output_file}")
    else:
        print("Error: No captions generated.")

# Run script
video_type = input("Enter video type: ")
generate_captions(video_type)