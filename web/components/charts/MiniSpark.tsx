"use client";

import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface MiniSparkProps {
  values: number[];
  color?: string;
  height?: number;
}

export function MiniSpark({ values, color = "#3b82f6", height = 40 }: MiniSparkProps) {
  if (!values || values.length === 0) return null;

  const option = {
    animation: false,
    grid: { left: 0, right: 0, top: 2, bottom: 2 },
    xAxis: { type: "category", show: false, data: values.map((_, i) => i) },
    yAxis: { type: "value", show: false, scale: true },
    tooltip: { show: false },
    series: [
      {
        type: "line",
        data: values,
        smooth: true,
        symbol: "none",
        lineStyle: { width: 1.5, color },
        areaStyle: { opacity: 0.15, color },
      },
    ],
  };

  return (
    <ReactECharts option={option} style={{ height: `${height}px`, width: "100%" }} />
  );
}
