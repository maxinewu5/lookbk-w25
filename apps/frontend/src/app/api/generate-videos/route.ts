import { NextResponse } from "next/server"
import { VideoService } from "@/lib/video-service"

const videoService = new VideoService()

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

    // Generate multiple video options using our video service
    const generatedOptions = await Promise.all(
      Array.from({ length: 3 }, async (_, i) => {
        const result = await videoService.generateReactionVideo(
          videoUrl,
          reactionType,
          demoType,
          `${prompt} (variation ${i + 1})`
        )
        return {
          id: result.id,
          name: `generated-${Date.now()}-${i}.mp4`,
          url: result.url,
          prompt: result.prompt,
          reaction: result.reaction,
          demoType: result.demoType,
          createdAt: new Date().toISOString(),
          previewUrl: result.previewUrl,
          description: result.description,
        }
      })
    )

    return NextResponse.json({ 
      options: generatedOptions,
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