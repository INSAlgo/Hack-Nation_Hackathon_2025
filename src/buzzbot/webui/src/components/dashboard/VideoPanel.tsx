import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AspectRatio } from "@/components/ui/aspect-ratio";

const defaultUrl =
  "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4";

export default function VideoPanel() {

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
          <video
            src={defaultUrl}
            controls
            className="h-full w-full rounded-lg object-cover"
          />
        </AspectRatio>
        <p className="text-xs text-muted-foreground">
          Tip: Keep it 9:16 for TikTok. Use quick cuts and bold on-screen text.
        </p>
      </CardContent>
    </Card>
  );
}
