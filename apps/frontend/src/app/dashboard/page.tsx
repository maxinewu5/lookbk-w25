"use client"

import { useState } from "react"
import { Video, Play, Home, Settings, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import VideoUploader from "@/components/video-uploader"
import VideoPreview from "@/components/video-preview"
import GeneratedVideos from "@/components/generated-videos"
import ClipCombiner from "@/components/clip-combiner"
import VideoMatcher from "@/components/video-matcher"
import { toast } from "sonner"

interface GeneratedOption {
  id: string
  name: string
  url: string
  prompt: string
  reaction: string
  demoType: string
  previewUrl?: string
  description?: string
}

type MatcherStep = "hook" | "demo"

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"generate" | "view">("generate")
  const [reactionType, setReactionType] = useState<string>("happy")
  const [demoType, setDemoType] = useState<string>("shazaming")
  const [prompt, setPrompt] = useState<string>("")
  const [currentVideo, setCurrentVideo] = useState<string | null>(null)
  const [generatedVideos, setGeneratedVideos] = useState<GeneratedOption[]>([])
  const [isGenerating, setIsGenerating] = useState<boolean>(false)
  const [showCombiner, setShowCombiner] = useState<boolean>(false)
  
  // New states for matching step
  const [showMatcher, setShowMatcher] = useState<boolean>(false)
  const [generatedOptions, setGeneratedOptions] = useState<GeneratedOption[]>([])
  const [matcherStep, setMatcherStep] = useState<MatcherStep>("hook")
  const [selectedHook, setSelectedHook] = useState<GeneratedOption | null>(null)
  const [originalVideo, setOriginalVideo] = useState<GeneratedOption | null>(null)

  const handleVideoUpload = (videoUrl: string) => {
    setCurrentVideo(videoUrl)
  }

  const handleGenerate = async () => {
    if (!currentVideo || !prompt) return

    setIsGenerating(true)

    try {
      const response = await fetch("/api/generate-videos", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          videoUrl: currentVideo,
          prompt,
          reactionType,
          demoType,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to generate video")
      }

      const data = await response.json()
      setGeneratedOptions(data.options)
      setOriginalVideo({
        id: 'original',
        url: currentVideo,
        name: 'Original Demo Video',
        prompt,
        reaction: reactionType,
        demoType
      })
      setShowMatcher(true)
    } catch (error) {
      console.error("Error generating video:", error)
      toast.error("Failed to generate video", {
        description: "Please try again later"
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleMatchingComplete = (selectedVideo: GeneratedOption) => {
    if (matcherStep === "hook") {
      setSelectedHook(selectedVideo)
      setMatcherStep("demo")
      return
    }

    // Here we would combine the hook and demo videos
    const combinedVideo = {
      ...selectedVideo,
      name: `${selectedHook?.name}-${selectedVideo.name}`,
      description: `Combined: ${selectedHook?.description} with ${selectedVideo.description}`
    }
    
    setGeneratedVideos([...generatedVideos, combinedVideo])
    setShowMatcher(false)
    setMatcherStep("hook")
    setSelectedHook(null)
    setActiveTab("view")
    setCurrentVideo(null)
    setPrompt("")
    setGeneratedOptions([])
    setOriginalVideo(null)
  }

  const handleMatchingCancel = () => {
    setShowMatcher(false)
    setGeneratedOptions([])
    setOriginalVideo(null)
  }

  return (
    <div className="flex h-screen bg-white text-gray-800">
      {/* Sidebar */}
      <div className="hidden md:flex w-64 flex-col bg-gray-100 border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-black">Video Dashboard</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant={activeTab === "generate" ? "default" : "ghost"}
            className={`w-full justify-start ${activeTab === "generate" ? "bg-blue-500 text-white hover:bg-blue-600" : "text-gray-700 hover:bg-gray-200"}`}
            onClick={() => setActiveTab("generate")}
          >
            <Video className="mr-2 h-4 w-4" />
            Generate Videos
          </Button>
          <Button
            variant={activeTab === "view" ? "default" : "ghost"}
            className={`w-full justify-start ${activeTab === "view" ? "bg-blue-500 text-white hover:bg-blue-600" : "text-gray-700 hover:bg-gray-200"}`}
            onClick={() => setActiveTab("view")}
          >
            <Play className="mr-2 h-4 w-4" />
            View Videos
          </Button>
        </nav>
        <div className="p-4 border-t border-gray-200">
          <Button variant="outline" className="w-full justify-start text-gray-700 border-gray-300 hover:bg-gray-200">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </div>
      </div>

      {/* Mobile navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around p-2 z-10">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setActiveTab("generate")}
          className={activeTab === "generate" ? "bg-gray-200" : ""}
        >
          <Video className="h-5 w-5 text-blue-600" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setActiveTab("view")}
          className={activeTab === "view" ? "bg-gray-200" : ""}
        >
          <Play className="h-5 w-5 text-blue-600" />
        </Button>
        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5 text-blue-600" />
        </Button>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="border-b px-6 py-4 flex items-center justify-between bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <h2 className="text-2xl font-semibold tracking-tight">
            {activeTab === "generate" && (showMatcher ? "Choose Generated Video" : "Generate Videos")}
            {activeTab === "view" && (showCombiner ? "Combine Clips" : "View Generated Videos")}
          </h2>
          <div className="flex items-center gap-4">
            <div className="flex md:hidden">
              <Button variant="ghost" size="icon" className="h-10 w-10">
                <Home className="h-5 w-5" />
              </Button>
            </div>
            {activeTab === "view" && (
              <Button variant="outline" onClick={() => setShowCombiner(!showCombiner)} className="h-10">
                {showCombiner ? "View All Videos" : "Combine Clips"}
              </Button>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-auto p-6 bg-muted/20">
          {activeTab === "generate" && !showMatcher && (
            <div className="h-full flex flex-col">
              <div className="flex-1 overflow-auto">
                <div className="grid gap-8 md:grid-cols-2 mb-4">
                  <div className="space-y-6 bg-white p-6 rounded-lg shadow-sm">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-800">Reaction Type</h3>
                      <RadioGroup
                        value={reactionType}
                        onValueChange={setReactionType}
                        className="grid grid-cols-2 gap-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="happy" id="happy" className="text-blue-600" />
                          <Label htmlFor="happy" className="text-gray-700">Happy</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="neutral" id="neutral" className="text-blue-600" />
                          <Label htmlFor="neutral" className="text-gray-700">Neutral</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="sad" id="sad" className="text-blue-600" />
                          <Label htmlFor="sad" className="text-gray-700">Sad</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="surprised" id="surprised" className="text-blue-600" />
                          <Label htmlFor="surprised" className="text-gray-700">Surprised</Label>
                        </div>
                      </RadioGroup>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-800">Demo Type</h3>
                      <RadioGroup value={demoType} onValueChange={setDemoType} className="grid grid-cols-2 gap-2">
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="shazaming" id="shazaming" className="text-blue-600" />
                          <Label htmlFor="shazaming" className="text-gray-700">Shazaming</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="feed" id="feed" className="text-blue-600" />
                          <Label htmlFor="feed" className="text-gray-700">Feed</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="keywords" id="keywords" className="text-blue-600" />
                          <Label htmlFor="keywords" className="text-gray-700">Keywords</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="other" id="other" className="text-blue-600" />
                          <Label htmlFor="other" className="text-gray-700">Other</Label>
                        </div>
                      </RadioGroup>
                    </div>
                  </div>

                  <div className="space-y-6 bg-white p-6 rounded-lg shadow-sm">
                    <h3 className="text-lg font-medium text-gray-800">Upload Demo Video</h3>
                    <VideoUploader onUpload={handleVideoUpload} />

                    {currentVideo && (
                      <div className="mt-6">
                        <h3 className="text-lg font-medium mb-4 text-gray-800">Demo Preview</h3>
                        <VideoPreview videoUrl={currentVideo} />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Prompt input and generate button */}
              <div className="mt-4 border-t border-gray-200 pt-4 bg-white p-4 rounded-lg shadow-sm">
                <div className="flex items-end space-x-4">
                  <div className="flex-1">
                    <Textarea
                      placeholder="Enter a prompt for video generation..."
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      className="min-h-[100px] resize-none border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                  <Button
                    onClick={handleGenerate}
                    disabled={!currentVideo || !prompt || isGenerating}
                    className="h-[100px] px-8 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      "Generate Video"
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "generate" && showMatcher && originalVideo && (
            <VideoMatcher
              originalVideo={originalVideo}
              generatedOptions={generatedOptions}
              onComplete={handleMatchingComplete}
              onCancel={handleMatchingCancel}
              step={matcherStep}
              selectedHook={selectedHook}
            />
          )}

          {activeTab === "view" && !showCombiner && (
            <GeneratedVideos videos={generatedVideos} />
          )}

          {activeTab === "view" && showCombiner && (
            <ClipCombiner videos={generatedVideos} />
          )}

          {isGenerating && (
            <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
              <div className="bg-card p-8 rounded-lg shadow-lg flex flex-col items-center max-w-md mx-auto">
                <div className="rounded-full bg-primary/10 p-4 mb-4">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
                <h3 className="text-xl font-semibold">Generating Video</h3>
                <p className="text-muted-foreground mt-2">This may take a moment...</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
