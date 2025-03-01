"use client"

import { useState } from "react"
import { ArrowRight, Check, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import VideoPreview from "@/components/video-preview"
import { toast } from "sonner"

interface Video {
  id: string
  name: string
  url: string
  prompt: string
  reaction: string
  demoType: string
  previewUrl?: string
  description?: string
}

interface VideoMatcherProps {
  originalVideo: Video
  generatedOptions: Video[]
  onComplete: (selectedVideo: Video) => void
  onCancel: () => void
  step: "hook" | "demo"
  selectedHook: Video | null
}

export default function VideoMatcher({ 
  originalVideo, 
  generatedOptions, 
  onComplete,
  onCancel,
  step,
  selectedHook
}: VideoMatcherProps) {
  const [selectedOption, setSelectedOption] = useState<Video | null>(null)
  const [isCombining, setIsCombining] = useState(false)

  const handleBack = () => {
    if (step === "demo") {
      setSelectedOption(null)
      onComplete(selectedHook!) // This will trigger the step change back to "hook"
    } else {
      onCancel()
    }
  }

  const handleCombine = async () => {
    if (!selectedOption) return

    if (step === "hook") {
      onComplete(selectedOption)
      return
    }

    setIsCombining(true)
    try {
      // In real implementation, this would call an API to combine videos
      await new Promise(resolve => setTimeout(resolve, 2000))
      onComplete(selectedOption)
      toast.success("Videos combined successfully!")
    } catch (error) {
      toast.error("Failed to combine videos")
      console.error(error)
    } finally {
      setIsCombining(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">
            {step === "hook" ? "Choose Hook Video" : "Choose Demo Video"}
          </h2>
          <p className="text-muted-foreground mt-1">
            {step === "hook" 
              ? "Select a hook video that will grab attention" 
              : "Now select a demo video to showcase your content"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleBack}>
            Back
          </Button>
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
        </div>
      </div>

      <div className="grid gap-6">
        {step === "demo" && selectedHook && (
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Selected Hook</h3>
            <div className="border rounded-lg overflow-hidden max-w-sm">
              <VideoPreview videoUrl={selectedHook.url} />
              {selectedHook.description && (
                <div className="p-3 border-t bg-muted/50">
                  <p className="text-sm text-muted-foreground">{selectedHook.description}</p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="space-y-4">
          <h3 className="text-lg font-medium">
            {step === "hook" ? "Hook Options" : "Demo Options"}
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {generatedOptions.map((option) => (
              <div
                key={option.id}
                className={`group border rounded-lg overflow-hidden transition-colors ${
                  selectedOption?.id === option.id 
                    ? "border-primary ring-2 ring-primary ring-offset-2" 
                    : "hover:border-primary/50"
                }`}
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity" />
                  <VideoPreview videoUrl={option.url} />
                  <Button
                    variant={selectedOption?.id === option.id ? "default" : "secondary"}
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-primary text-primary-foreground hover:bg-primary/90 opacity-0 group-hover:opacity-100 transition-opacity"
                    size="sm"
                    onClick={() => setSelectedOption(option)}
                  >
                    {selectedOption?.id === option.id ? (
                      <>
                        <Check className="mr-1 h-3 w-3" />
                        Selected
                      </>
                    ) : (
                      "Select"
                    )}
                  </Button>
                </div>
                {option.description && (
                  <div className="p-3 border-t bg-muted/50">
                    <p className="text-sm text-muted-foreground">{option.description}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <Button
          size="lg"
          onClick={handleCombine}
          disabled={!selectedOption || isCombining}
          className="bg-primary hover:bg-primary/90"
        >
          {isCombining ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Combining Videos...
            </>
          ) : (
            <>
              <ArrowRight className="mr-2 h-4 w-4" />
              {step === "hook" ? "Continue to Demo" : "Combine Videos"}
            </>
          )}
        </Button>
      </div>
    </div>
  )
} 