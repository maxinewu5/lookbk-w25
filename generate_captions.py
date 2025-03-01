import ollama

def generate_captions(video_type: str, output_file="captions.txt"):
    prompt = f"""Generate 15 engaging TikTok captions for a {video_type} video.
    - Keep each caption **under 10 words**.
    - Use **trendy phrases, humor, or emojis**.
    - Make them feel **fun and relatable**.
    - Include **hooks, questions, or call-to-actions (CTA)**.
    - Format the response as a **numbered list**.
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}], options={"temperature": 0.7})
    
    # Debugging: Print response to verify
    print("Generated Captions:\n", response)

    # Ensure response has correct structure
    captions = response.get('message', {}).get('content', '')

    if captions:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(captions)
        print(f"Captions saved to {output_file}")
    else:
        print("Error: No captions generated.")

# Run script
video_type = input("Enter video type: ")
generate_captions(video_type)
