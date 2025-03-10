"use client"

import { useState } from "react"
import { Upload, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

interface VideoUploaderProps {
  onUpload: (url: string) => void
  prompt?: string
  reactionType?: string
  demoType?: string
}

export default function VideoUploader({ onUpload, prompt, reactionType, demoType }: VideoUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleUpload = async (file: File) => {
    if (!file || !file.type.includes("video/")) {
      toast.error("Please upload a valid video file")
      return
    }

    setIsUploading(true)
    try {
      // Get presigned URL
      const response = await fetch("/api/upload-video", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          file: file.name,
          prompt: prompt || "",
          reactionType: reactionType || "",
          demoType: demoType || "",
        }),
      })

      if (!response.ok) throw new Error("Failed to get upload URL")
      
      const { signedUrl, video } = await response.json()

      // Upload to S3
      await fetch(signedUrl, {
        method: "PUT",
        body: file,
        headers: {
          "Content-Type": file.type,
        },
      })

      toast.success("Video uploaded successfully!")
      onUpload(video.url)
    } catch (error) {
      console.error("Error uploading video:", error)
      toast.error("Failed to upload video")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    await handleUpload(file)
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      await handleUpload(file)
    }
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 text-center ${
        isDragging ? "border-primary bg-primary/5" : "border-gray-300"
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept="video/*"
        className="hidden"
        id="video-upload"
        onChange={handleFileChange}
        disabled={isUploading}
      />
      <label
        htmlFor="video-upload"
        className="cursor-pointer flex flex-col items-center justify-center"
      >
        {isUploading ? (
          <>
            <Loader2 className="h-10 w-10 text-primary animate-spin mb-2" />
            <p className="text-sm text-muted-foreground">Uploading video...</p>
          </>
        ) : (
          <>
            <Upload className="h-10 w-10 text-primary mb-2" />
            <p className="text-sm text-muted-foreground">
              Drag and drop a video file here, or click to select
            </p>
          </>
        )}
      </label>
    </div>
  )
}

