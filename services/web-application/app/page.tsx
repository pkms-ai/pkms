"use client";

import { useState } from "react";
import { ContentList } from "@/components/content/content-list";
import { Navigation } from "@/components/navigation";
import { ContentType } from "@/types/content";

export default function Home() {
  const [selectedType, setSelectedType] = useState<ContentType | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <>
      <Navigation
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
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