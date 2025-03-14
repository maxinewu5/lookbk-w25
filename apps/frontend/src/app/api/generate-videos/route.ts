import { NextResponse } from "next/server"

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const { videoUrl, prompt, reactionType, demoType } = body

    if (!videoUrl || !prompt || !reactionType || !demoType) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      )
    }

    // Generate videos from backend
    const generatedResponse = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate-videos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ videoUrl, prompt, reactionType, demoType }),
    })

    if (!generatedResponse.ok) {
      throw new Error('Failed to generate videos')
    }

    const generatedOptions = await generatedResponse.json()

    // Upload each generated video to S3
    const uploadedVideos = await Promise.all(
      generatedOptions.map(async (option: any) => {
        const uploadResponse = await fetch('/api/upload-generated', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt,
            reactionType,
            demoType,
          }),
        })

        if (!uploadResponse.ok) {
          throw new Error('Failed to get upload URL')
        }

        const { signedUrl, video } = await uploadResponse.json()

        // Upload video to S3
        const uploadResult = await fetch(signedUrl, {
          method: 'PUT',
          body: option.videoData,
          headers: {
            'Content-Type': 'video/mp4',
          },
        })

        if (!uploadResult.ok) {
          throw new Error('Failed to upload to S3')
        }

        return {
          ...video,
          url: video.url,
          name: video.name,
        }
      })
    )

    return NextResponse.json({ 
      options: uploadedVideos,
      originalVideo: {
        id: 'original',
        url: videoUrl,
        name: 'Original Demo Video'
      }
    })
  } catch (error) {
    console.error("Error generating video:", error)
    return NextResponse.json(
      { error: "Failed to generate video" },
      { status: 500 }
    )
  }
}