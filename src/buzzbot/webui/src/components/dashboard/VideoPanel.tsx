import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Film } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";

export default function VideoPanel({ videoUrl, postOpen, onPostOpenChange }: { videoUrl?: string; postOpen?: boolean; onPostOpenChange?: (open: boolean) => void }) {
  const TEMPLATE = `🔥 {HOOK}

📝 {POST SUMMARY}

🎯 {CALL_TO_ACTION}

#buzzbot #tiktok #fyp #viral #yourNiche`;
  const [description, setDescription] = useState<string>(TEMPLATE);
  const [internalOpen, setInternalOpen] = useState(false);
  const open = postOpen ?? internalOpen;
  const setOpen = (v: boolean) => {
    if (onPostOpenChange) onPostOpenChange(v);
    else setInternalOpen(v);
  };
  const [platforms, setPlatforms] = useState({ tiktok: true, instagram: true, youtube: true, twitter: false });
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [schedule, setSchedule] = useState(false);
  const [scheduleAt, setScheduleAt] = useState<string>("");
  const { toast } = useToast();
  const selectedPlatforms = Object.entries(platforms)
    .filter(([, v]) => v)
    .map(([k]) => k)
    .join(", ") || "None";

  const handleConfirmPost = () => {
    toast({
      title: "Posting started",
      description: `Platforms: ${selectedPlatforms}`,
    });
    setOpen(false);
  };

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
        <div className="space-y-2">
          <Label htmlFor="post-desc">Post description</Label>
          <Textarea
            id="post-desc"
            placeholder="Write your post caption…"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Post this video</DialogTitle>
              <DialogDescription>
                Review your content, choose platforms, and set options before posting.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <section className="space-y-2">
                <h3 className="text-sm font-medium">Recap</h3>
                <div className="rounded-md border p-3 bg-card text-sm whitespace-pre-wrap">
                  {description}
                </div>
              </section>

              <section className="space-y-2">
                <h3 className="text-sm font-medium">Platforms</h3>
                <div className="grid grid-cols-2 gap-3">
                  <label className="flex items-center gap-2 text-sm">
                    <Checkbox checked={platforms.tiktok} onCheckedChange={(v) => setPlatforms(p => ({ ...p, tiktok: !!v }))} />
                    TikTok
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <Checkbox checked={platforms.instagram} onCheckedChange={(v) => setPlatforms(p => ({ ...p, instagram: !!v }))} />
                    Instagram Reels
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <Checkbox checked={platforms.youtube} onCheckedChange={(v) => setPlatforms(p => ({ ...p, youtube: !!v }))} />
                    YouTube Shorts
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <Checkbox checked={platforms.twitter} onCheckedChange={(v) => setPlatforms(p => ({ ...p, twitter: !!v }))} />
                    Twitter/X
                  </label>
                </div>
              </section>

              <section className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Include hashtags</span>
                  <Switch checked={includeHashtags} onCheckedChange={setIncludeHashtags} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Schedule</span>
                  <Switch checked={schedule} onCheckedChange={setSchedule} />
                </div>
                {schedule && (
                  <div className="pt-2">
                    <Label htmlFor="scheduleAt" className="text-sm">Publish at</Label>
                    <Input id="scheduleAt" type="datetime-local" value={scheduleAt} onChange={(e) => setScheduleAt(e.target.value)} />
                  </div>
                )}
              </section>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={handleConfirmPost}>Confirm Post</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
