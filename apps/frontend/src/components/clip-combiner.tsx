"use client"

import { useState } from "react"
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd"
import { GripVertical, Play, X, ArrowRight, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import VideoPreview from "@/components/video-preview"

interface Video {
  id: string
  name: string
  url: string
  prompt: string
  reaction: string
  demoType: string
}

interface ClipCombinerProps {
  videos: Video[]
}

export default function ClipCombiner({ videos }: ClipCombinerProps) {
  const [selectedClips, setSelectedClips] = useState<Video[]>([])
  const [availableClips, setAvailableClips] = useState<Video[]>(videos)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isCombining, setIsCombining] = useState(false)

  const handleAddClip = (clip: Video) => {
    setSelectedClips([...selectedClips, clip])
    setAvailableClips(availableClips.filter((v) => v.id !== clip.id))
  }

  const handleRemoveClip = (clip: Video) => {
    setSelectedClips(selectedClips.filter((v) => v.id !== clip.id))
    setAvailableClips([...availableClips, clip])
  }

  const handleDragEnd = (result: any) => {
    if (!result.destination) return

    const items = Array.from(selectedClips)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    setSelectedClips(items)
  }

  const handleCombineClips = () => {
    if (selectedClips.length === 0) return

    setIsCombining(true)

    // Simulate combining process
    setTimeout(() => {
      // In a real app, you would combine the videos on the server
      // For now, we'll just use the first video as the "combined" result
      setPreviewUrl(selectedClips[0].url)
      setIsCombining(false)
    }, 2000)
  }

  if (videos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] text-center">
        <h3 className="text-lg font-medium mb-2">No videos available</h3>
        <p className="text-sm text-muted-foreground">Generate some videos first to combine them</p>
      </div>
    )
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium mb-4">Available Clips</h3>
          <div className="border rounded-lg overflow-hidden">
            {availableClips.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">All clips have been added to the sequence</div>
            ) : (
              <div className="divide-y">
                {availableClips.map((clip) => (
                  <div key={clip.id} className="p-3 flex items-center justify-between hover:bg-muted/50">
                    <div className="flex items-center">
                      <div className="w-16 h-9 bg-muted rounded overflow-hidden mr-3">
                        <video src={clip.url} className="w-full h-full object-cover" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{clip.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {clip.reaction} • {clip.demoType}
                        </p>
                      </div>
                    </div>
                    <Button size="sm" onClick={() => handleAddClip(clip)}>
                      Add
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Clip Sequence</h3>
            <Button
              variant="default"
              size="sm"
              onClick={handleCombineClips}
              disabled={selectedClips.length === 0 || isCombining}
            >
              {isCombining ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Combining...
                </>
              ) : (
                "Combine Clips"
              )}
            </Button>
          </div>

          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="clips">
              {(provided) => (
                <div {...provided.droppableProps} ref={provided.innerRef} className="border rounded-lg overflow-hidden">
                  {selectedClips.length === 0 ? (
                    <div className="p-6 text-center text-muted-foreground">Add clips to create a sequence</div>
                  ) : (
                    <div className="divide-y">
                      {selectedClips.map((clip, index) => (
                        <Draggable key={clip.id} draggableId={clip.id} index={index}>
                          {(provided) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              className="p-3 flex items-center justify-between hover:bg-muted/50"
                            >
                              <div className="flex items-center">
                                <div {...provided.dragHandleProps} className="mr-2 text-muted-foreground">
                                  <GripVertical className="h-5 w-5" />
                                </div>
                                <div className="w-16 h-9 bg-muted rounded overflow-hidden mr-3">
                                  <video src={clip.url} className="w-full h-full object-cover" />
                                </div>
                                <div>
                                  <p className="font-medium text-sm">{clip.name}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {clip.reaction} • {clip.demoType}
                                  </p>
                                </div>
                              </div>
                              <Button variant="ghost" size="icon" onClick={() => handleRemoveClip(clip)}>
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                        </Draggable>
                      ))}
                    </div>
                  )}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>

          {selectedClips.length > 0 && (
            <div className="mt-4 flex items-center justify-center text-sm text-muted-foreground">
              <ArrowRight className="h-4 w-4 mr-2" />
              Drag and drop to reorder clips
            </div>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-4">Combined Preview</h3>
        {previewUrl ? (
          <VideoPreview videoUrl={previewUrl} />
        ) : (
          <div className="border rounded-lg aspect-video flex items-center justify-center bg-muted/50">
            <div className="text-center p-6">
              <Play className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                {isCombining ? "Combining clips..." : "Combine clips to preview the result"}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

