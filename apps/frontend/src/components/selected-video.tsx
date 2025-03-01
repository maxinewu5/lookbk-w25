"use client"

import { useState } from "react"
import { Edit, Trash2, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import VideoPreview from "@/components/video-preview"

interface Video {
  id: string
  name: string
  url: string
}

interface SelectedVideosProps {
  videos: Video[]
}

export default function SelectedVideos({ videos }: SelectedVideosProps) {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)

  if (videos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <Play className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">No videos selected yet</h3>
        <p className="text-sm text-muted-foreground">Upload and accept videos to see them here</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Selected Videos</h3>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {videos.map((video) => (
          <div key={video.id} className="border rounded-lg overflow-hidden bg-card">
            <div className="aspect-video bg-muted relative group">
              <video src={video.url} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="secondary" size="icon" onClick={() => setSelectedVideo(video)}>
                      <Play className="h-5 w-5" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl">
                    <DialogHeader>
                      <DialogTitle>Video Preview</DialogTitle>
                    </DialogHeader>
                    {selectedVideo && <VideoPreview videoUrl={selectedVideo.url} />}
                  </DialogContent>
                </Dialog>
              </div>
            </div>

            <div className="p-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium truncate">{video.name}</h4>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="flex items-center mt-2 text-xs text-muted-foreground">
                <span className="bg-primary/10 text-primary px-2 py-1 rounded-full">Happy</span>
                <span className="bg-muted px-2 py-1 rounded-full ml-2">Gaming</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

