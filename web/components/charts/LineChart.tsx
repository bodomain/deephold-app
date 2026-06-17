"use client";

import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface LineChartProps {
  dates: string[];
  values: (number | null)[];
  height?: number;
  color?: string;
}

export function LineChart({
  dates,
  values,
  height = 400,
  color = "#3b82f6",
}: LineChartProps) {
  const option = {
    animation: false,
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(30,30,30,0.9)",
      borderColor: "#444",
      textStyle: { color: "#eee", fontSize: 12 },
    },
    grid: { left: 60, right: 30, top: 20, bottom: 80 },
    xAxis: {
      type: "category",
      data: dates,
      axisLabel: { fontSize: 11, color: "#888" },
      axisLine: { lineStyle: { color: "#ccc" } },
    },
    yAxis: {
      type: "value",
      scale: true,
      axisLabel: { fontSize: 11, color: "#888" },
      splitLine: { lineStyle: { color: "#f0f0f0" } },
    },
    dataZoom: [
      { type: "inside", start: 0, end: 100 },
      {
        type: "slider",
        start: 0,
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
        type: "line",
        data: values,
        smooth: false,
        symbol: "none",
        lineStyle: { width: 1.5, color },
        areaStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: `${color}33` },
              { offset: 1, color: `${color}00` },
            ],
          },
        },
      },
    ],
  };

  return (
    <ReactECharts option={option} style={{ height: `${height}px`, width: "100%" }} />
  );
}
