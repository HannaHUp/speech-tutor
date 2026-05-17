import type { ComponentProps } from "svelte";
import Dashboard from "./Dashboard.svelte";
import DashboardCharts from "./DashboardCharts.svelte";
import { demoDashboardData, type DashboardChartKind } from "./dashboardData";

const views: Array<"practice" | "dashboard"> = ["practice", "dashboard"];
const chartKinds: DashboardChartKind[] = ["radar", "trend", "errors"];

if (views.length !== 2 || chartKinds.length !== 3) {
  throw new Error("Dashboard navigation and chart contracts changed unexpectedly");
}

const dashboardProps: ComponentProps<typeof Dashboard> = {
  data: demoDashboardData,
};

const radarProps: ComponentProps<typeof DashboardCharts> = {
  kind: "radar",
  skills: demoDashboardData.skills,
};

const trendProps: ComponentProps<typeof DashboardCharts> = {
  kind: "trend",
  trend: demoDashboardData.trend,
};

const errorProps: ComponentProps<typeof DashboardCharts> = {
  kind: "errors",
  errors: demoDashboardData.errors,
};

void dashboardProps;
void radarProps;
void trendProps;
void errorProps;
