"use client"

import { useRef, useState, useEffect } from "react"
import { Play, Pause, Volume2, VolumeX } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { cn } from "@/lib/utils"

//TODO: something is wrong with this, slider colors don't work

interface VideoPreviewProps {
  videoUrl: string
  className?: string
}

export default function VideoPreview({ videoUrl, className }: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isMuted, setIsMuted] = useState(false)
  const [volume, setVolume] = useState(1)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const updateTime = () => setCurrentTime(video.currentTime)
    const updateDuration = () => setDuration(video.duration)
    const handleEnd = () => setIsPlaying(false)

    video.addEventListener("timeupdate", updateTime)
    video.addEventListener("loadedmetadata", updateDuration)
    video.addEventListener("ended", handleEnd)

    return () => {
      video.removeEventListener("timeupdate", updateTime)
      video.removeEventListener("loadedmetadata", updateDuration)
      video.removeEventListener("ended", handleEnd)
    }
  }, [])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return

    if (isPlaying) {
      video.pause()
    } else {
      video.play()
    }
    setIsPlaying(!isPlaying)
  }

  const toggleMute = () => {
    const video = videoRef.current
    if (!video) return

    video.muted = !isMuted
    setIsMuted(!isMuted)
  }

  const handleVolumeChange = (value: number[]) => {
    const video = videoRef.current
    if (!video) return

    const newVolume = value[0]
    video.volume = newVolume
    setVolume(newVolume)
    setIsMuted(newVolume === 0)
  }

  const handleSeek = (value: number[]) => {
    const video = videoRef.current
    if (!video) return

    video.currentTime = value[0]
    setCurrentTime(value[0])
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`
  }

  return (
    <div className={cn("w-full bg-card rounded-lg overflow-hidden border", className)}>
      <div className="relative aspect-video bg-muted">
        <video 
          ref={videoRef} 
          src={videoUrl} 
          className="w-full h-full object-contain bg-background" 
          onClick={togglePlay} 
        />

        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <Button
              variant="secondary"
              size="icon"
              className="h-16 w-16 rounded-full bg-background/80 hover:bg-background/90 hover:scale-105 transition-all"
              onClick={togglePlay}
            >
              <Play className="h-8 w-8 text-foreground" />
            </Button>
          </div>
        )}
      </div>

      <div className="p-4 space-y-3 bg-card">
        <Slider
          value={[currentTime]}
          min={0}
          max={duration || 100}
          step={0.1}
          onValueChange={handleSeek}
          className="cursor-pointer [&>.SliderTrack]:bg-blue-200 [&>.SliderTrack>.SliderRange]:bg-blue-500"
        />

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={togglePlay} className="hover:bg-muted">
            {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
          </Button>

          <div className="text-sm font-medium text-muted-foreground">
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <Button variant="ghost" size="icon" onClick={toggleMute} className="hover:bg-muted">
              {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
            </Button>
            <div className="w-24">
              <Slider 
                value={[isMuted ? 0 : volume]} 
                min={0} 
                max={1} 
                step={0.1} 
                onValueChange={handleVolumeChange}
                className="cursor-pointer [&>.SliderTrack]:bg-blue-200 [&>.SliderTrack>.SliderRange]:bg-blue-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
