"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface VideoUploaderProps {
  onUpload: (videoUrl: string) => void
}

export default function VideoUploader({ onUpload }: VideoUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]
      if (file.type.startsWith("video/")) {
        handleFile(file)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    setUploadedFile(file)
    // Create a URL for the video
    const videoUrl = URL.createObjectURL(file)
    onUpload(videoUrl)
  }

  const handleRemoveFile = () => {
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center min-h-[300px] ${
        isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/20"
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {!uploadedFile ? (
        <>
          <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Upload className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">Upload Demo Video</h3>
          <p className="text-sm text-muted-foreground text-center mb-4">
            Drag and drop your demo video here, or click to browse
          </p>
          <Button onClick={handleButtonClick}>Select Video</Button>
          <input type="file" ref={fileInputRef} className="hidden" accept="video/*" onChange={handleFileChange} />
          <p className="text-xs text-muted-foreground mt-4">Supported formats: MP4, MOV, AVI, WebM</p>
        </>
      ) : (
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-muted rounded">
            <File className="h-8 w-8" />
          </div>
          <div className="flex-1">
            <p className="font-medium truncate max-w-[200px]">{uploadedFile.name}</p>
            <p className="text-sm text-muted-foreground">{(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
          </div>
          <Button variant="ghost" size="icon" onClick={handleRemoveFile}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}

