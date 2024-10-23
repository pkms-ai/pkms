import { ContentList } from "@/components/content/content-list";
import { Navigation } from "@/components/navigation";
import { ContentType } from "@/types/content";

export const revalidate = 3600; // Revalidate every hour



export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ type?: string; search?: string }>;
}) {
  const { type, search } = await searchParams;
  const selectedType = (type as ContentType | "all") ?? "all";
  const searchQuery = search ?? "";

  return (
    <>
      <Navigation
        selectedType={selectedType}
        searchQuery={searchQuery}
      />
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ContentList
          selectedType={selectedType}
          searchQuery={searchQuery}
        />
      </div>
    </>
  );
}
