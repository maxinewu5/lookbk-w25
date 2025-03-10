interface VideoGenerationResult {
  id: string;
  url: string;
  prompt: string;
  reaction: string;
  demoType: string;
  previewUrl: string;
  description: string;
}

interface ProcessedVideo {
  id: string;
  url: string;
  caption: string;
}

export class VideoService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  async generateReactionVideo(
    videoUrl: string,
    reactionType: string,
    demoType: string,
    prompt: string
  ): Promise<VideoGenerationResult> {
    const response = await fetch(`${this.baseUrl}/generate-videos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        videoUrl,
        prompt,
        reactionType,
        demoType,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate video');
    }

    const data = await response.json();
    return data.options[0]; // Return the first option for now
  }

  async processVideos(
    hookUrls: string[],
    demoUrls: string[],
    videoType: string
  ): Promise<ProcessedVideo[]> {
    const response = await fetch(`${this.baseUrl}/process-videos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        hook_urls: hookUrls,
        demo_urls: demoUrls,
        video_type: videoType,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to process videos');
    }

    const data = await response.json();
    return data.videos;
  }

  async combineVideos(
    hookVideo: VideoGenerationResult,
    demoVideo: VideoGenerationResult,
    outputFilename: string
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/combine-videos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        hookVideoPath: hookVideo.url,
        demoVideoPath: demoVideo.url,
        outputFilename,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to combine videos');
    }

    const data = await response.json();
    return data.url;
  }

  async addCaptions(
    videoPath: string,
    captions: string[],
    outputFilename: string,
    fontSize: number = 70
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/add-captions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        videoPath,
        captions,
        outputFilename,
        fontSize,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to add captions');
    }

    const data = await response.json();
    return data.url;
  }
} 