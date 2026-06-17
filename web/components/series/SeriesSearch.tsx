"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import type { SeriesSummary } from "@/lib/types";

const TYPE_COLORS: Record<string, "blue" | "green" | "purple" | "orange"> = {
  price: "blue",
  bond: "green",
  fx: "purple",
  macro: "orange",
};

interface SeriesSearchProps {
  allSeries: SeriesSummary[];
  value: string;
  onChange: (v: string) => void;
  typeFilter?: string;
  sourceFilter?: string;
}

export function SeriesSearch({
  allSeries,
  value,
  onChange,
  typeFilter,
  sourceFilter,
}: SeriesSearchProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const suggestions = useMemo(() => {
    if (!value.trim()) return [];
    const q = value.toLowerCase();
    let pool = allSeries;
    if (typeFilter) pool = pool.filter((s) => s.type === typeFilter);
    if (sourceFilter) pool = pool.filter((s) => (s.source || "") === sourceFilter);

    const scored: { s: SeriesSummary; score: number }[] = [];
    for (const s of pool) {
      const name = (s.name || "").toLowerCase();
      const ident = s.identifier.toLowerCase();
      let score = -1;
      if (ident === q) score = 100;
      else if (ident.startsWith(q)) score = 90;
      else if (name === q) score = 80;
      else if (name.startsWith(q)) score = 70;
      else if (ident.includes(q)) score = 50;
      else if (name.includes(q)) score = 40;
      else continue;
      scored.push({ s, score });
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, 8).map((x) => x.s);
  }, [value, allSeries, typeFilter, sourceFilter]);

  useEffect(() => {
    setHighlight(0);
  }, [value]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function selectSeries(s: SeriesSummary) {
    setOpen(false);
    onChange("");
    router.push(`/series/${encodeURIComponent(s.id)}`);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!open || suggestions.length === 0) {
      if (e.key === "ArrowDown" && value.trim()) {
        setOpen(true);
        e.preventDefault();
      }
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      if (highlight < suggestions.length) {
        e.preventDefault();
        selectSeries(suggestions[highlight]);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-xs">
      <input
        ref={inputRef}
        type="text"
        placeholder="Search series... (↑↓ to navigate, Enter to open)"
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
        }}
        onFocus={() => value.trim() && setOpen(true)}
        onKeyDown={handleKeyDown}
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      />
      {open && suggestions.length > 0 && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md overflow-hidden">
          {suggestions.map((s, i) => (
            <button
              key={s.id}
              onMouseEnter={() => setHighlight(i)}
              onClick={() => selectSeries(s)}
              className={`flex w-full items-center gap-3 px-3 py-2 text-left text-sm transition-colors ${
                i === highlight ? "bg-accent" : "hover:bg-accent/50"
              }`}
            >
              <Badge variant={TYPE_COLORS[s.type] || "secondary"} className="shrink-0 text-xs">
                {s.type}
              </Badge>
              <span className="font-medium truncate flex-1">{s.name}</span>
              <span className="text-xs text-muted-foreground font-mono shrink-0">
                {s.identifier}
              </span>
            </button>
          ))}
          <div className="border-t px-3 py-1.5 text-xs text-muted-foreground">
            {suggestions.length} match{suggestions.length !== 1 ? "es" : ""} · Enter to open
          </div>
        </div>
      )}
    </div>
  );
}
