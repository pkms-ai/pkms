import { Content } from "@/types/content";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Link, Video } from "lucide-react";
import Image from "next/image";

const TYPE_ICONS = {
  article: FileText,
  video: Video,
  link: Link,
};

export function ContentCard({ content }: { content: Content }) {
  const Icon = TYPE_ICONS[content.type];
  const date = new Date(content.createdAt).toLocaleDateString();

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative aspect-video">
        <Image
          src={content.thumbnail}
          alt={content.title}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          priority
        />
        <div className="absolute top-2 right-2">
          <Badge variant="secondary" className="flex items-center gap-1">
            <Icon className="h-3 w-3" />
            <span className="capitalize">{content.type}</span>
          </Badge>
        </div>
      </div>
      <CardHeader className="space-y-2">
        <h3 className="font-semibold leading-tight line-clamp-2">{content.title}</h3>
        <div className="flex flex-wrap gap-1">
          {content.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {content.summary}
        </p>
        <p className="text-xs text-muted-foreground mt-2">{date}</p>
      </CardContent>
    </Card>
  );
}