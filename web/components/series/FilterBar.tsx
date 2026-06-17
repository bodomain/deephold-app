"use client";

import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface FilterBarProps {
  type: string;
  source: string;
  query: string;
  onTypeChange: (v: string) => void;
  onSourceChange: (v: string) => void;
  onQueryChange: (v: string) => void;
}

const TYPES = ["", "price", "bond", "fx", "macro"];
const SOURCES = ["", "yahoo", "fred", "ecb", "mixed"];

export function FilterBar({
  type,
  source,
  query,
  onTypeChange,
  onSourceChange,
  onQueryChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 mb-4">
      <Input
        placeholder="Search series..."
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        className="max-w-xs"
      />

      <div className="flex items-center gap-1">
        {TYPES.map((t) => (
          <button
            key={t || "all"}
            onClick={() => onTypeChange(t)}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              type === t
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {t || "All"}
          </button>
        ))}
      </div>

      <select
        value={source}
        onChange={(e) => onSourceChange(e.target.value)}
        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
      >
        {SOURCES.map((s) => (
          <option key={s || "all"} value={s}>
            {s ? `Source: ${s}` : "All Sources"}
          </option>
        ))}
      </select>

      <Badge variant="secondary" className="ml-auto">
        {TYPES.indexOf(type) >= 0 ? type || "All" : type}
      </Badge>
    </div>
  );
}
