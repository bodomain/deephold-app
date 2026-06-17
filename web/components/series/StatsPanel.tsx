"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SeriesStats } from "@/lib/types";

function fmtPct(v: number | null): string {
  if (v === null) return "—";
  return `${v >= 0 ? "+" : ""}${(v * 100).toFixed(2)}%`;
}

function fmtNum(v: number | null, digits = 2): string {
  if (v === null) return "—";
  return v.toFixed(digits);
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className={`text-lg font-semibold tabular-nums ${color || ""}`}>
        {value}
      </div>
    </div>
  );
}

export function StatsPanel({ stats }: { stats: SeriesStats | null }) {
  if (!stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground text-sm">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <StatCard
            label="CAGR"
            value={fmtPct(stats.cagr)}
            color={stats.cagr !== null && stats.cagr >= 0 ? "text-green-600" : "text-red-600"}
          />
          <StatCard
            label="Volatility (ann.)"
            value={fmtPct(stats.volatility)}
          />
          <StatCard
            label="Sharpe Ratio"
            value={fmtNum(stats.sharpe)}
            color={stats.sharpe !== null && stats.sharpe >= 0 ? "text-green-600" : "text-red-600"}
          />
          <StatCard
            label="Max Drawdown"
            value={fmtPct(stats.max_drawdown)}
            color="text-red-600"
          />
          <StatCard label="Latest" value={fmtNum(stats.latest)} />
          <StatCard label="First" value={fmtNum(stats.first)} />
          <StatCard label="Min" value={fmtNum(stats.min)} />
          <StatCard label="Max" value={fmtNum(stats.max)} />
          <StatCard label="Mean" value={fmtNum(stats.mean)} />
        </div>
        <div className="mt-3 text-xs text-muted-foreground">
          Based on {stats.count.toLocaleString()} observations.
        </div>
      </CardContent>
    </Card>
  );
}
