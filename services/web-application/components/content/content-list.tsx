"use client";

import { useState } from "react";
import { Content, ContentType } from "@/types/content";
import { ContentCard } from "./content-card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { generateMockContent } from "@/lib/utils/content";

const ITEMS_PER_PAGE = 12;
const TOTAL_ITEMS = 60;

interface ContentListProps {
  selectedType: ContentType | "all";
  searchQuery: string;
}

export function ContentList({ selectedType, searchQuery }: ContentListProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);

  // Generate content once and memoize it
  const allContent = generateMockContent(0, TOTAL_ITEMS);

  const filteredContent = allContent.filter((item) => {
    const matchesType = selectedType === "all" || item.type === selectedType;
    const matchesSearch = searchQuery === "" || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  const totalPages = Math.ceil(filteredContent.length / ITEMS_PER_PAGE);
  const pageContent = filteredContent.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handlePageChange = async (page: number) => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 300));
    setCurrentPage(page);
    setLoading(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-6">
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Loading...</span>
          </div>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {pageContent.map((item) => (
              <ContentCard key={item.id} content={item} />
            ))}
          </div>

          {pageContent.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No content found</p>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2 py-8">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || loading}
              >
                <ChevronLeft className="h-4 w-4" />
                <span className="sr-only">Previous page</span>
              </Button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={currentPage === page ? "default" : "outline"}
                  size="sm"
                  onClick={() => handlePageChange(page)}
                  disabled={loading}
                  className="min-w-[2.5rem]"
                >
                  {page}
                </Button>
              ))}

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages || loading}
              >
                <ChevronRight className="h-4 w-4" />
                <span className="sr-only">Next page</span>
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}