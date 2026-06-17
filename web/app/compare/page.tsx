"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });
import { apiGet, apiPost } from "@/lib/api";
import type { CompareResponse, SeriesSummary } from "@/lib/types";

const COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899"];

export default function ComparePage() {
  const [allSeries, setAllSeries] = useState<SeriesSummary[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<SeriesSummary[]>("/api/series?limit=500").then(setAllSeries);
  }, []);

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id)
        ? prev.filter((x) => x !== id)
        : prev.length < 6
          ? [...prev, id]
          : prev
    );
  };

  const run = () => {
    if (selected.length < 2) return;
    setLoading(true);
    setError(null);
    apiPost<CompareResponse>("/api/compare", {
      ids: selected,
      normalize: true,
    })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const option = data
    ? {
        animation: false,
        tooltip: { trigger: "axis" },
        legend: { data: data.series.map((s) => s.name), top: 5 },
        grid: { left: 60, right: 30, top: 40, bottom: 80 },
        xAxis: {
          type: "category",
          data: data.dates,
          axisLabel: { fontSize: 11 },
        },
        yAxis: { type: "value", scale: true },
        dataZoom: [
          { type: "inside", start: 0, end: 100 },
          { type: "slider", start: 0, end: 100, bottom: 10 },
        ],
        series: data.series.map((s, i) => ({
          name: s.name,
          type: "line",
          data: s.values,
          symbol: "none",
          lineStyle: { width: 1.5, color: COLORS[i % COLORS.length] },
        })),
      }
    : null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Compare Series</h1>
      <p className="text-sm text-muted-foreground">
        Select 2-6 series to overlay, normalized to base 100.
      </p>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Selected ({selected.length}/6)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-3">
            {selected.map((id) => {
              const s = allSeries.find((x) => x.id === id);
              return (
                <Badge key={id} variant="secondary">
                  {s?.name || id}
                  <button
                    onClick={() => toggle(id)}
                    className="ml-2 text-muted-foreground hover:text-foreground"
                  >
                    ×
                  </button>
                </Badge>
              );
            })}
            {selected.length === 0 && (
              <span className="text-sm text-muted-foreground">
                Pick series below to start.
              </span>
            )}
          </div>
          <Button onClick={run} disabled={selected.length < 2 || loading}>
            {loading ? "Loading..." : "Compare"}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-md border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {option && (
        <Card>
          <CardHeader>
            <CardTitle>Normalized Comparison (Base = 100)</CardTitle>
          </CardHeader>
          <CardContent>
            <ReactECharts option={option} style={{ height: "450px", width: "100%" }} />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Available Series</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-96 overflow-y-auto space-y-1">
            {allSeries.map((s) => (
              <label
                key={s.id}
                className="flex items-center gap-2 p-2 rounded hover:bg-muted cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selected.includes(s.id)}
                  onChange={() => toggle(s.id)}
                  disabled={!selected.includes(s.id) && selected.length >= 6}
                />
                <span className="text-sm font-medium">{s.name}</span>
                <Badge variant="outline" className="text-xs">
                  {s.type}
                </Badge>
                <span className="text-xs text-muted-foreground ml-auto">
                  {s.identifier}
                </span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
