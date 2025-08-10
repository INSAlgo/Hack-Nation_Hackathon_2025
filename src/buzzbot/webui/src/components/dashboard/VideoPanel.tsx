import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Film } from "lucide-react";


export default function VideoPanel({ videoUrl }: { videoUrl?: string }) {

  return (
    <Card className="h-full flex flex-col bg-transparent border-0 shadow-none">
      <CardHeader>
        <CardTitle>Video Preview</CardTitle>
        <CardDescription>
          Preview your concept video.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 flex-1 overflow-auto">
        <AspectRatio ratio={9 / 16} className="rounded-lg border bg-muted overflow-hidden w-full">
          {videoUrl ? (
            <video
              src={videoUrl}
              controls
              className="h-full w-full rounded-lg object-cover"
            />
          ) : (
            <div className="h-full w-full flex flex-col items-center justify-center gap-2 text-muted-foreground bg-card">
              <Film className="h-8 w-8" aria-hidden="true" />
              <p className="text-sm">No video yet. Generate a preview from the chat.</p>
            </div>
          )}
        </AspectRatio>
      </CardContent>
    </Card>
  );
}
