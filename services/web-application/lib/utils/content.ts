import { Content, ContentType } from "@/types/content";

const TITLES = [
  "TypeScript Tips for Better Code",
  "React Best Practices Guide",
  "Web Development Fundamentals",
  "CSS Modern Techniques",
  "JavaScript Design Patterns"
];

const TAGS = ["web", "development", "programming", "frontend", "backend"];

export async function generateMockContent(startId: number, count: number): Promise<Content[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));

  const types: ContentType[] = ["article", "video", "link"];
  return Array.from({ length: count }, (_, i) => {
    const id = `content-${startId + i}`;
    return {
      id,
      title: TITLES[i % TITLES.length],
      type: types[i % types.length],
      url: "https://example.com",
      summary: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      thumbnail: `https://picsum.photos/seed/${id}/800/600`,
      createdAt: new Date(2024, 0, 1 + i).toISOString(),
      tags: TAGS.slice(0, 2 + (i % 3)),
    };
  });
}
