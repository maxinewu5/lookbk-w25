"use client"

import { useEffect, useState } from "react"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import VideoPreview from "./video-preview"
import { toast } from "sonner"

interface Video {
  id: string
  name: string
  url: string
  prompt: string
  reaction: string
  demoType: string
  createdAt: string
}

interface PaginationInfo {
  total: number
  page: number
  limit: number
  totalPages: number
}

export default function VideoGallery() {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState<PaginationInfo>({
    total: 0,
    page: 1,
    limit: 9,
    totalPages: 0,
  })
  const [filters, setFilters] = useState({
    reaction: "all",
    demoType: "all",
  })

  const fetchVideos = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString(),
        ...(filters.reaction !== "all" && { reaction: filters.reaction }),
        ...(filters.demoType !== "all" && { demoType: filters.demoType }),
      })

      const response = await fetch(`/api/fetch-videos?${params}`)
      if (!response.ok) throw new Error("Failed to fetch videos")
      
      const data = await response.json()
      setVideos(data.videos)
      setPagination(data.pagination)
    } catch (error) {
      console.error("Error fetching videos:", error)
      toast.error("Failed to load videos")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchVideos()
  }, [pagination.page, filters])

  const reactionTypes = ["happy", "neutral", "sad", "surprised"]
  const demoTypes = ["shazaming", "feed", "keywords", "other"]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Generated Videos</h2>
        <div className="flex gap-2">
          <Select
            value={filters.reaction}
            onValueChange={(value) => setFilters(prev => ({ ...prev, reaction: value }))}
          >
            <SelectTrigger className="w-[150px] bg-white text-black">
              <SelectValue placeholder="Reaction Type" />
            </SelectTrigger>
            <SelectContent className="bg-white text-black">
              <SelectItem value="all">All Reactions</SelectItem>
              {reactionTypes.map((type) => (
                <SelectItem key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={filters.demoType}
            onValueChange={(value) => setFilters(prev => ({ ...prev, demoType: value }))}
          >
            <SelectTrigger className="w-[150px] bg-white text-black">
              <SelectValue placeholder="Demo Type" />
            </SelectTrigger>
            <SelectContent className="bg-white text-black">
              <SelectItem value="all">All Types</SelectItem>
              {demoTypes.map((type) => (
                <SelectItem key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : videos.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed rounded-lg">
          <p className="text-muted-foreground">No videos found</p>
        </div>
      ) : (
        <>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {videos.map((video) => (
              <div key={video.id} className="group border rounded-lg overflow-hidden">
                <div className="relative">
                  <VideoPreview videoUrl={video.url} />
                </div>
                <div className="p-4 space-y-2">
                  <h3 className="font-medium truncate">{video.name}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">{video.prompt}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                      {video.reaction}
                    </span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-muted">
                      {video.demoType}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-4">
            <p className="text-sm text-muted-foreground">
              Showing {(pagination.page - 1) * pagination.limit + 1} to{" "}
              {Math.min(pagination.page * pagination.limit, pagination.total)} of{" "}
              {pagination.total} videos
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={pagination.page === 1}
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                disabled={pagination.page === pagination.totalPages}
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
} 