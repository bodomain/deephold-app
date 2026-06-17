"use client";

import { useEffect, useState } from "react";
import { FilterBar } from "@/components/series/FilterBar";
import { SeriesTable } from "@/components/series/SeriesTable";
import { apiGet } from "@/lib/api";
import type { SeriesSummary } from "@/lib/types";

export default function SeriesPage() {
  const [series, setSeries] = useState<SeriesSummary[]>([]);
  const [allSeries, setAllSeries] = useState<SeriesSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [type, setType] = useState("");
  const [source, setSource] = useState("");
  const [query, setQuery] = useState("");

  // Load full series list once for autocomplete
  useEffect(() => {
    apiGet<SeriesSummary[]>("/api/series?limit=1000")
      .then(setAllSeries)
      .catch(() => {});
  }, []);

  // Load filtered series for the table
  useEffect(() => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (type) params.set("type", type);
    if (source) params.set("source", source);
    if (query) params.set("q", query);
    params.set("limit", "500");
    apiGet<SeriesSummary[]>(`/api/series?${params}`)
      .then((data) => setSeries(data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [type, source, query]);

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
        <SeriesTable series={series} />
      )}
    </div>
  );
}
