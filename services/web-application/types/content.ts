export type ContentType = "article" | "video" | "link";

export interface Content {
  id: string;
  title: string;
  type: ContentType;
  url: string;
  summary: string;
  thumbnail: string;
  createdAt: string;
  tags: string[];
}