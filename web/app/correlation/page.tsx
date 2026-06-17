"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });
import { apiGet, apiPost } from "@/lib/api";
import type { CorrelationResponse, SeriesSummary } from "@/lib/types";

export default function CorrelationPage() {
  const [allSeries, setAllSeries] = useState<SeriesSummary[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [data, setData] = useState<CorrelationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<SeriesSummary[]>("/api/series?limit=500").then(setAllSeries);
  }, []);

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id)
        ? prev.filter((x) => x !== id)
        : prev.length < 10
          ? [...prev, id]
          : prev
    );
  };

  const run = () => {
    if (selected.length < 2) return;
    setLoading(true);
    setError(null);
    apiPost<CorrelationResponse>("/api/correlation", { ids: selected })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const heatmapOption = data
    ? {
        animation: false,
        tooltip: {
          position: "top",
          formatter: (params: { name: string; value: [number, number, number] }) =>
            `${data.labels[params.value[1]]} vs ${data.labels[params.value[0]]}<br/>Correlation: ${params.value[2]?.toFixed(3)}`,
        },
        grid: { left: 150, right: 40, top: 20, bottom: 150 },
        xAxis: {
          type: "category",
          data: data.labels,
          axisLabel: { rotate: 45, fontSize: 10 },
        },
        yAxis: {
          type: "category",
          data: data.labels,
          axisLabel: { fontSize: 10 },
        },
        visualMap: {
          min: -1,
          max: 1,
          calculable: true,
          orient: "horizontal",
          left: "center",
          bottom: 10,
          inRange: { color: ["#ef4444", "#f5f5f5", "#22c55e"] },
        },
        series: [
          {
            type: "heatmap",
            data: data.matrix.flatMap((row, i) =>
              row.map((v, j) => [i, j, v])
            ),
            label: { show: true, fontSize: 9, formatter: (p: { value: [number, number, number] }) => p.value[2]?.toFixed(2) },
          },
        ],
      }
    : null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Correlation Matrix</h1>
      <p className="text-sm text-muted-foreground">
        Select 2-10 series to compute pairwise correlation.
      </p>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Selected ({selected.length}/10)
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
          </div>
          <Button onClick={run} disabled={selected.length < 2 || loading}>
            {loading ? "Computing..." : "Compute Correlation"}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-md border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {heatmapOption && (
        <Card>
          <CardHeader>
            <CardTitle>Correlation Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <ReactECharts
              option={heatmapOption}
              style={{ height: "500px", width: "100%" }}
            />
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
                  disabled={!selected.includes(s.id) && selected.length >= 10}
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
