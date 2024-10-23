"use client";

import { BookMarked, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ContentFilter } from "./content/content-filter";
import { ContentType } from "@/types/content";

interface NavigationProps {
  selectedType?: ContentType | "all";
  onTypeChange?: (type: ContentType | "all") => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export function Navigation({ 
  selectedType = "all",
  onTypeChange = () => {},
  searchQuery = "",
  onSearchChange = () => {},
}: NavigationProps) {
  const { setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-7xl items-center mx-auto px-4 sm:px-6 lg:px-8">
        <Link href="/" className="mr-4 flex items-center space-x-2">
          <BookMarked className="h-6 w-6" />
          <span className="hidden font-bold sm:inline-block">
            Knowledge Hub
          </span>
        </Link>

        <div className="flex-1">
          <ContentFilter
            selectedType={selectedType}
            onTypeChange={onTypeChange}
            searchQuery={searchQuery}
            onSearchChange={onSearchChange}
          />
        </div>

        <div className="ml-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme("light")}>
                Light
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("dark")}>
                Dark
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("system")}>
                System
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}