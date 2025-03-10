"use client"

import { useState } from "react"
import { Trash2, Play, Download, Copy, X } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import VideoPreview from "@/components/video-preview"

interface Video {
  id: string
  name: string
  url: string
  prompt: string
  reaction: string
  demoType: string
  description?: string
}

interface GeneratedVideosProps {
  videos: Video[]
}

export default function GeneratedVideos({ videos }: GeneratedVideosProps) {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)

  const handleDownload = async (video: Video) => {
    try {
      const toastId = toast.loading(`Downloading ${video.name}...`)
      
      const response = await fetch(video.url)
      if (!response.ok) throw new Error('Failed to fetch video')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = video.name
      document.body.appendChild(a)
      a.click()
      
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success('Download complete!', {
        id: toastId,
        description: video.name
      })
    } catch (error) {
      console.error('Error downloading video:', error)
      toast.error('Failed to download video', {
        description: 'Please try again later'
      })
    }
  }

  if (videos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <Play className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">No generated videos yet</h3>
        <p className="text-sm text-muted-foreground">Upload a demo video and add a prompt to generate content</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {videos.map((video) => (
          <div
            key={video.id}
            className="group border rounded-lg overflow-hidden transition-colors hover:border-primary/50"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity" />
              <VideoPreview videoUrl={video.url} />
              <Button
                variant="secondary"
                className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-primary text-primary-foreground hover:bg-primary/90 opacity-0 group-hover:opacity-100 transition-opacity"
                size="sm"
                onClick={() => setSelectedVideo(video)}
              >
                Preview
              </Button>
            </div>
            <div className="p-3 border-t bg-muted/50">
              <p className="font-medium truncate">{video.name}</p>
              {video.description && (
                <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{video.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {selectedVideo && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50">
          <div className="fixed inset-x-4 top-[50%] translate-y-[-50%] max-h-[90vh] overflow-auto rounded-lg border bg-card p-0 shadow-lg sm:inset-x-auto sm:left-[50%] sm:translate-x-[-50%] sm:max-w-3xl">
            <div className="relative flex w-full flex-col">
              <div className="flex items-center justify-between border-b px-4 py-3">
                <div>
                  <h3 className="text-lg font-semibold">{selectedVideo.name}</h3>
                  {selectedVideo.description && (
                    <p className="text-sm text-muted-foreground mt-1">{selectedVideo.description}</p>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="rounded-full"
                  onClick={() => setSelectedVideo(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="p-0">
                <VideoPreview videoUrl={selectedVideo.url} />
              </div>
              <div className="flex items-center justify-end gap-2 border-t px-4 py-3">
                <Button variant="ghost" onClick={() => setSelectedVideo(null)}>
                  Close
                </Button>
                <Button variant="default" className="bg-primary hover:bg-primary/90" onClick={() => handleDownload(selectedVideo)}>
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

