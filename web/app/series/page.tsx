"use client";

import { useEffect, useMemo, useState } from "react";
import { FilterBar } from "@/components/series/FilterBar";
import { SeriesTable } from "@/components/series/SeriesTable";
import { apiGet } from "@/lib/api";
import type { SeriesSummary } from "@/lib/types";

export default function SeriesPage() {
  const [allSeries, setAllSeries] = useState<SeriesSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [type, setType] = useState("");
  const [source, setSource] = useState("");
  const [query, setQuery] = useState("");

  // Load full series list once — filtering is client-side
  useEffect(() => {
    apiGet<SeriesSummary[]>("/api/series?limit=1000")
      .then((data) => {
        setAllSeries(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  // Client-side filtering (instant, no API call)
  const filtered = useMemo(() => {
    let result = allSeries;
    if (type) result = result.filter((s) => s.type === type);
    if (source) result = result.filter((s) => (s.source || "") === source);
    if (query) {
      const ql = query.toLowerCase();
      result = result.filter(
        (s) =>
          (s.name || "").toLowerCase().includes(ql) ||
          s.identifier.toLowerCase().includes(ql)
      );
    }
    return result;
  }, [allSeries, type, source, query]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Series Browser</h1>
      <FilterBar
        type={type}
        source={source}
        query={query}
        allSeries={allSeries}
        onTypeChange={setType}
        onSourceChange={setSource}
        onQueryChange={setQuery}
      />
      {error && (
        <div className="rounded-md border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          Error: {error}
        </div>
      )}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading...</div>
      ) : (
        <>
          <div className="text-sm text-muted-foreground">
            {filtered.length} of {allSeries.length} series
          </div>
          <SeriesTable series={filtered} />
        </>
      )}
    </div>
  );
}
