import { Content, ContentType } from "@/types/content";
import { ContentCard } from "./content-card";
import { generateMockContent } from "@/lib/utils/content";

interface ContentListProps {
  selectedType: ContentType | "all";
  searchQuery: string;
}

export async function ContentList({ selectedType, searchQuery }: ContentListProps) {
  // Simulate fetching data from an API
  const allContent = await generateMockContent(0, 60);

  const filteredContent = allContent.filter((item) => {
    const matchesType = selectedType === "all" || item.type === selectedType;
    const matchesSearch = searchQuery === "" || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filteredContent.map((item) => (
          <ContentCard key={item.id} content={item} />
        ))}
      </div>
      {filteredContent.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No content found</p>
        </div>
      )}
    </div>
  );
}
