export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface SeriesSummary {
  id: string;
  name: string;
  asset_class: string;
  source: string;
  currency: string | null;
  latest_date: string | null;
  latest_value: number | null;
  count: number;
}

export interface SeriesDetail {
  id: string;
  name: string;
  asset_class: string;
  source: string;
  currency: string | null;
  frequency: string | null;
  unit: string | null;
  first_date: string | null;
  last_date: string | null;
  count: number;
}

export interface Observation {
  date: string;
  value: number | null;
}

export interface Candle {
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface SeriesStats {
  cagr: number | null;
  volatility: number | null;
  sharpe: number | null;
  max_drawdown: number | null;
  latest: number | null;
  first: number | null;
  min: number | null;
  max: number | null;
  mean: number | null;
}
