"use client";

import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface Candle {
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

interface CandleChartProps {
  candles: Candle[];
  height?: number;
}

export function CandleChart({ candles, height = 450 }: CandleChartProps) {
  const ohlc = candles.map((c) => [c.open, c.close, c.low, c.high]);
  const volumes = candles.map((c) => c.volume ?? 0);
  const dates = candles.map((c) => c.date);

  const option = {
    animation: false,
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      backgroundColor: "rgba(30,30,30,0.9)",
      borderColor: "#444",
      textStyle: { color: "#eee", fontSize: 12 },
    },
    legend: { data: ["Price", "Volume"], top: 5 },
    grid: [
      { left: 60, right: 30, top: 40, height: "55%" },
      { left: 60, right: 30, top: "72%", height: "18%" },
    ],
    xAxis: [
      {
        type: "category",
        data: dates,
        scale: true,
        axisLabel: { show: false },
        boundaryGap: false,
      },
      {
        type: "category",
        gridIndex: 1,
        data: dates,
        axisLabel: { fontSize: 11, color: "#888" },
      },
    ],
    yAxis: [
      { scale: true, splitLine: { lineStyle: { color: "#f0f0f0" } } },
      { gridIndex: 1, splitNumber: 2, axisLabel: { show: false } },
    ],
    dataZoom: [
      { type: "inside", xAxisIndex: [0, 1], start: 60, end: 100 },
      {
        type: "slider",
        xAxisIndex: [0, 1],
        start: 60,
        end: 100,
        height: 20,
        bottom: 10,
        borderColor: "#ddd",
        fillerColor: "rgba(59,130,246,0.1)",
        handleStyle: { color: "#3b82f6" },
      },
    ],
    series: [
      {
        name: "Price",
        type: "candlestick",
        data: ohlc,
        itemStyle: {
          color: "#22c55e",
          color0: "#ef4444",
          borderColor: "#22c55e",
          borderColor0: "#ef4444",
        },
      },
      {
        name: "Volume",
        type: "bar",
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: { color: "rgba(100,100,100,0.3)" },
      },
    ],
  };

  return (
    <ReactECharts option={option} style={{ height: `${height}px`, width: "100%" }} />
  );
}
