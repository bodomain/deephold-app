"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { SeriesSummary } from "@/lib/types";

const TYPE_COLORS: Record<string, "blue" | "green" | "purple" | "orange"> = {
  price: "blue",
  bond: "green",
  fx: "purple",
  macro: "orange",
};

function formatNumber(v: number | null): string {
  if (v === null) return "—";
  if (Math.abs(v) >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`;
  return v.toFixed(2);
}

export function SeriesTable({ series }: { series: SeriesSummary[] }) {
  if (series.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No series found. Try adjusting your filters.
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Asset Class</TableHead>
          <TableHead>Source</TableHead>
          <TableHead className="text-right">Count</TableHead>
          <TableHead>Last Date</TableHead>
          <TableHead className="text-right">Latest</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {series.map((s) => (
          <TableRow key={s.id}>
            <TableCell>
              <Link
                href={`/series/${encodeURIComponent(s.id)}`}
                className="font-medium hover:underline"
              >
                {s.name}
              </Link>
              <div className="text-xs text-muted-foreground">{s.identifier}</div>
            </TableCell>
            <TableCell>
              <Badge variant={TYPE_COLORS[s.type] || "secondary"}>{s.type}</Badge>
            </TableCell>
            <TableCell className="text-sm">{s.asset_class}</TableCell>
            <TableCell className="text-sm">{s.source || "—"}</TableCell>
            <TableCell className="text-right tabular-nums">
              {s.count.toLocaleString()}
            </TableCell>
            <TableCell className="text-sm">
              {s.last_date || "—"}
            </TableCell>
            <TableCell className="text-right tabular-nums font-mono">
              {formatNumber(s.latest_value)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
