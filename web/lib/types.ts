export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface SeriesSummary {
  id: string;
  type: string;
  identifier: string;
  name: string;
  asset_class: string;
  source: string | null;
  currency: string | null;
  unit: string | null;
  frequency: string | null;
  count: number;
  first_date: string | null;
  last_date: string | null;
  latest_value: number | null;
}

export interface SeriesDetail {
  id: string;
  type: string;
  identifier: string;
  name: string;
  asset_class: string;
  source: string | null;
  currency: string | null;
  unit: string | null;
  frequency: string | null;
  count: number;
  first_date: string | null;
  last_date: string | null;
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
  count: number;
}

export interface CompareSeries {
  id: string;
  name: string;
  dates: string[];
  values: (number | null)[];
}

export interface CompareResponse {
  series: CompareSeries[];
  dates: string[];
}

export interface CorrelationResponse {
  matrix: (number | null)[][];
  labels: string[];
}

export interface DashboardItem {
  id: string;
  name: string;
  latest_value: number | null;
  latest_date: string | null;
  change_pct: number | null;
  sparkline: number[];
}

export interface DashboardResponse {
  items: DashboardItem[];
}
