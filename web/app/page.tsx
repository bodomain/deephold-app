"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MiniSpark } from "@/components/charts/MiniSpark";
import { apiGet } from "@/lib/api";
import type { DashboardResponse } from "@/lib/types";

function fmtNum(v: number | null, digits = 2): string {
  if (v === null) return "—";
  if (Math.abs(v) >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`;
  return v.toFixed(digits);
}

function fmtPct(v: number | null): string {
  if (v === null) return "—";
  return `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<DashboardResponse>("/api/dashboard/macro")
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading...</div>;
  if (error) return <div className="text-destructive">Error: {error}</div>;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Macro Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.items.map((item) => (
          <Link key={item.id} href={`/series/${encodeURIComponent(item.id)}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {item.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end justify-between mb-2">
                  <div className="text-2xl font-bold tabular-nums">
                    {fmtNum(item.latest_value)}
                  </div>
                  <Badge
                    variant={
                      item.change_pct !== null && item.change_pct >= 0
                        ? "green"
                        : "destructive"
                    }
                  >
                    {fmtPct(item.change_pct)}
                  </Badge>
                </div>
                <MiniSpark values={item.sparkline} />
                <div className="text-xs text-muted-foreground mt-1">
                  {item.latest_date || "—"}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
