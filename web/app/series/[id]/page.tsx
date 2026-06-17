"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart } from "@/components/charts/LineChart";
import { CandleChart } from "@/components/charts/CandleChart";
import { StatsPanel } from "@/components/series/StatsPanel";
import { apiGet } from "@/lib/api";
import type {
  Candle,
  Observation,
  SeriesDetail,
  SeriesStats,
} from "@/lib/types";

const TYPE_COLORS: Record<string, "blue" | "green" | "purple" | "orange"> = {
  price: "blue",
  bond: "green",
  fx: "purple",
  macro: "orange",
};

export default function SeriesDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const seriesId = decodeURIComponent(id);

  const [detail, setDetail] = useState<SeriesDetail | null>(null);
  const [stats, setStats] = useState<SeriesStats | null>(null);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [view, setView] = useState<"line" | "candle">("line");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      apiGet<SeriesDetail>(`/api/series/${encodeURIComponent(seriesId)}`),
      apiGet<SeriesStats>(`/api/series/${encodeURIComponent(seriesId)}/stats`),
    ])
      .then(([d, s]) => {
        setDetail(d);
        setStats(s);
        if (d.type === "price") {
          apiGet<Candle[]>(
            `/api/series/${encodeURIComponent(seriesId)}/candles?limit=5000`
          ).then((c) => {
            setCandles(c);
            setLoading(false);
          });
        } else {
          apiGet<Observation[]>(
            `/api/series/${encodeURIComponent(seriesId)}/observations?limit=10000`
          ).then((o) => {
            setObservations(o);
            setLoading(false);
          });
        }
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [seriesId]);

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">Loading...</div>;
  }

  if (error || !detail) {
    return (
      <div className="space-y-4">
        <div className="rounded-md border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          {error || "Series not found"}
        </div>
        <Link href="/series">
          <Button variant="outline">Back to Browser</Button>
        </Link>
      </div>
    );
  }

  const isPrice = detail.type === "price";
  const lineDates = observations.map((o) => o.date);
  const lineValues = observations.map((o) => o.value);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold">{detail.name}</h1>
            <Badge variant={TYPE_COLORS[detail.type] || "secondary"}>
              {detail.type}
            </Badge>
          </div>
          <div className="text-sm text-muted-foreground">
            {detail.identifier} · {detail.source} ·{" "}
            {detail.count.toLocaleString()} observations ·{" "}
            {detail.first_date} to {detail.last_date}
          </div>
        </div>
        <div className="flex gap-2">
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || ""}/api/series/${encodeURIComponent(seriesId)}/export?format=csv`}
          >
            <Button variant="outline" size="sm">Export CSV</Button>
          </a>
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || ""}/api/series/${encodeURIComponent(seriesId)}/export?format=json`}
          >
            <Button variant="outline" size="sm">Export JSON</Button>
          </a>
        </div>
      </div>

      <StatsPanel stats={stats} />

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Price Chart</CardTitle>
            {isPrice && (
              <div className="flex gap-1">
                <button
                  onClick={() => setView("line")}
                  className={`px-3 py-1 rounded text-sm ${
                    view === "line"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  Line
                </button>
                <button
                  onClick={() => setView("candle")}
                  className={`px-3 py-1 rounded text-sm ${
                    view === "candle"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  Candlestick
                </button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isPrice && view === "candle" ? (
            <CandleChart candles={candles} />
          ) : (
            <LineChart dates={lineDates} values={lineValues} height={450} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
