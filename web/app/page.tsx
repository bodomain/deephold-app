import { Button } from "@/components/ui/button";
import {
  Activity,
  TrendingUp,
  Database,
  LineChart,
} from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">deephold</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Financial market data platform — 30 years of history, 4M+ time
          series observations across equities, macro, FX, bonds, and
          commodities.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <FeatureCard
          icon={<Database className="h-8 w-8 text-blue-500" />}
          title="Series Browser"
          description="Filter by asset class, source, region. Search 600+ instruments and 100+ macro series."
        />
        <FeatureCard
          icon={<LineChart className="h-8 w-8 text-green-500" />}
          title="Interactive Charts"
          description="Line and candlestick plots with zoom, pan, and date range selection."
        />
        <FeatureCard
          icon={<TrendingUp className="h-8 w-8 text-purple-500" />}
          title="Analytics"
          description="CAGR, volatility, Sharpe ratio, max drawdown — computed on the fly."
        />
        <FeatureCard
          icon={<Activity className="h-8 w-8 text-orange-500" />}
          title="Compare & Correlate"
          description="Overlay multiple series, rolling correlation matrices, macro dashboard."
        />
      </div>

      <div className="text-center">
        <Button size="lg" asChild>
          <a href="/series">Browse Series</a>
        </Button>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-6 space-y-3">
      <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-muted">
        {icon}
      </div>
      <h3 className="font-semibold text-lg">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
