"use client";

import { ContentType } from "@/types/content";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { BookMarked, Link2, Search, Youtube } from "lucide-react";

interface ContentFilterProps {
  selectedType: ContentType | "all";
  onTypeChange: (type: ContentType | "all") => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

const CONTENT_TYPES = [
  { value: "all", label: "All", icon: Search },
  { value: "article", label: "Articles", icon: BookMarked },
  { value: "video", label: "Videos", icon: Youtube },
  { value: "link", label: "Links", icon: Link2 },
] as const;

export function ContentFilter({
  selectedType,
  onTypeChange,
  searchQuery,
  onSearchChange,
}: ContentFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by title or tags..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-8 w-full"
          />
        </div>
      </div>
      <div className="flex gap-1">
        {CONTENT_TYPES.map(({ value, label, icon: Icon }) => (
          <Button
            key={value}
            variant={selectedType === value ? "default" : "ghost"}
            size="sm"
            onClick={() => onTypeChange(value as ContentType | "all")}
            className="hidden sm:flex items-center gap-1"
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}