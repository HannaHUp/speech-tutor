<script lang="ts">
  import type {
    DashboardChartKind,
    ErrorPattern,
    SkillScore,
    TrendPoint,
  } from "./dashboardData";

  let {
    kind,
    skills = [],
    trend = [],
    errors = [],
  }: {
    kind: DashboardChartKind;
    skills?: SkillScore[];
    trend?: TrendPoint[];
    errors?: ErrorPattern[];
  } = $props();

  const radarCenter = 120;
  const radarRadius = 74;
  const radarRings = [25, 50, 75, 100];
  const trendKeys = [
    { key: "overall", label: "Overall", color: "#2563eb" },
    { key: "accuracy", label: "Accuracy", color: "#0f766e" },
    { key: "fluency", label: "Fluency", color: "#d97706" },
    { key: "pronunciation", label: "Pronunciation", color: "#667085" },
  ] as const;

  function radarPoint(index: number, total: number, value: number) {
    const angle = (Math.PI * 2 * index) / total - Math.PI / 2;
    const distance = (Math.max(0, Math.min(value, 100)) / 100) * radarRadius;
    return {
      x: radarCenter + Math.cos(angle) * distance,
      y: radarCenter + Math.sin(angle) * distance,
    };
  }

  function radarPolygon(field: "average" | "latest", scale = 1) {
    if (skills.length === 0) return "";
    return skills
      .map((skill, index) => {
        const point = radarPoint(index, skills.length, skill[field] * scale);
        return `${point.x.toFixed(1)},${point.y.toFixed(1)}`;
      })
      .join(" ");
  }

  function trendX(index: number) {
    if (trend.length <= 1) return 52;
    return 52 + (index / (trend.length - 1)) * 520;
  }

  function trendY(value: number) {
    return 218 - (Math.max(0, Math.min(value, 100)) / 100) * 158;
  }

  function trendLine(key: (typeof trendKeys)[number]["key"]) {
    return trend
      .map((point, index) => `${trendX(index).toFixed(1)},${trendY(point[key]).toFixed(1)}`)
      .join(" ");
  }

  function trendArea() {
    if (trend.length === 0) return "";
    const line = trend
      .map((point, index) => `${trendX(index).toFixed(1)},${trendY(point.overall).toFixed(1)}`)
      .join(" ");
    return `52,218 ${line} ${trendX(trend.length - 1).toFixed(1)},218`;
  }

  function maxErrorCount() {
    return Math.max(...errors.map((error) => error.count), 1);
  }

  function categoryColor(category: ErrorPattern["category"]) {
    const colors: Record<ErrorPattern["category"], string> = {
      reading: "#2563eb",
      grammar: "#0f766e",
      pronunciation: "#7c3aed",
      fluency: "#d97706",
      interaction: "#be123c",
    };
    return colors[category];
  }
</script>

{#if kind === "radar"}
  <section class="panel chart-panel" aria-labelledby="radar-title">
    <div class="panel-heading">
      <div>
        <h2 id="radar-title">Skill Profile</h2>
        <p>Recent average compared with the latest spoken evidence.</p>
      </div>
      <div class="legend">
        <span><i class="latest"></i>Latest</span>
        <span><i class="average"></i>Recent average</span>
      </div>
    </div>

    <div class="radar-layout">
      <svg class="radar" viewBox="0 0 240 240" role="img" aria-label="Skill radar chart">
        {#each radarRings as ring}
          <polygon
            class="ring"
            points={skills
              .map((_, index) => {
                const point = radarPoint(index, skills.length, ring);
                return `${point.x.toFixed(1)},${point.y.toFixed(1)}`;
              })
              .join(" ")}
          />
        {/each}

        {#each skills as skill, index}
          {@const end = radarPoint(index, skills.length, 100)}
          <line class="axis" x1={radarCenter} y1={radarCenter} x2={end.x} y2={end.y} />
          <text
            class="axis-label"
            x={radarPoint(index, skills.length, 114).x}
            y={radarPoint(index, skills.length, 114).y}
            text-anchor={index === 0 || index === 3 ? "middle" : index < 3 ? "start" : "end"}
          >
            {skill.label}
          </text>
        {/each}

        <polygon class="average-shape" points={radarPolygon("average")} />
        <polygon class="latest-shape" points={radarPolygon("latest")} />
      </svg>

      <div class="score-list">
        {#each skills as skill}
          <div class="score-row">
            <span>{skill.label}</span>
            <strong>{skill.latest}</strong>
            <small>avg {skill.average}</small>
          </div>
        {/each}
      </div>
    </div>
  </section>
{:else if kind === "trend"}
  <section class="panel chart-panel" aria-labelledby="trend-title">
    <div class="panel-heading">
      <div>
        <h2 id="trend-title">Progress Trend</h2>
        <p>Session-level estimates from fixture evidence.</p>
      </div>
      <div class="legend wrap">
        {#each trendKeys as item}
          <span><i style={`background: ${item.color}`}></i>{item.label}</span>
        {/each}
      </div>
    </div>

    <svg class="trend" viewBox="0 0 640 280" role="img" aria-label="Progress trend line chart">
      <path class="trend-area" d={`M ${trendArea()} Z`} />
      {#each [25, 50, 75, 100] as tick}
        <line class="gridline" x1="52" x2="572" y1={trendY(tick)} y2={trendY(tick)} />
        <text class="tick-label" x="22" y={trendY(tick) + 4}>{tick}</text>
      {/each}
      <line class="baseline" x1="52" x2="572" y1="218" y2="218" />
      {#each trendKeys as item}
        <polyline
          class:item-primary={item.key === "overall"}
          class="trend-line"
          points={trendLine(item.key)}
          stroke={item.color}
        />
      {/each}
      {#each trend as point, index}
        <circle class="point" cx={trendX(index)} cy={trendY(point.overall)} r="4" />
        <text class="date-label" x={trendX(index)} y="246">{point.date}</text>
      {/each}
    </svg>
  </section>
{:else}
  <section class="panel errors-panel" aria-labelledby="errors-title">
    <div class="panel-heading">
      <div>
        <h2 id="errors-title">Top Recurring Evidence Signals</h2>
        <p>Patterns that shape the next instructional action.</p>
      </div>
    </div>

    <div class="error-list">
      {#each errors as error}
        <article class="error-row">
          <div class="error-main">
            <div class="error-title">
              <span class="category" style={`background: ${categoryColor(error.category)}`}>
                {error.category}
              </span>
              <strong>{error.label}</strong>
            </div>
            <div class="bar-track" aria-label={`${error.count} observations`}>
              <span
                class="bar"
                style={`width: ${(error.count / maxErrorCount()) * 100}%; background: ${categoryColor(error.category)}`}
              ></span>
            </div>
            <p>{error.example}</p>
            <small>{error.nextDrill}</small>
          </div>
          <div class="error-count">
            <strong>{error.count}</strong>
            <span>{error.trend}</span>
          </div>
        </article>
      {/each}
    </div>
  </section>
{/if}

<style>
  .panel {
    min-width: 0;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
  }

  .panel-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  h2 {
    margin: 0;
    color: #172033;
    font-size: 1rem;
    line-height: 1.3;
  }

  p {
    margin: 0.25rem 0 0;
    color: #667085;
    font-size: 0.875rem;
    line-height: 1.45;
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0.5rem 0.875rem;
    color: #475467;
    font-size: 0.75rem;
    white-space: nowrap;
  }

  .legend span {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
  }

  .legend i {
    width: 0.625rem;
    height: 0.625rem;
    border-radius: 999px;
    background: #2563eb;
  }

  .legend i.average {
    background: #0f766e;
  }

  .radar-layout {
    display: grid;
    grid-template-columns: minmax(13rem, 1fr) minmax(10rem, 0.72fr);
    gap: 1rem;
    align-items: center;
  }

  .radar,
  .trend {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }

  .ring {
    fill: none;
    stroke: #e5e7eb;
    stroke-width: 1;
  }

  .axis {
    stroke: #eef2f7;
    stroke-width: 1;
  }

  .axis-label,
  .date-label,
  .tick-label {
    fill: #667085;
    font-size: 8px;
  }

  .average-shape {
    fill: rgba(15, 118, 110, 0.14);
    stroke: #0f766e;
    stroke-width: 2;
  }

  .latest-shape {
    fill: rgba(37, 99, 235, 0.16);
    stroke: #2563eb;
    stroke-width: 2.5;
  }

  .score-list {
    display: grid;
    gap: 0.5rem;
  }

  .score-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.125rem 0.625rem;
    align-items: baseline;
    color: #172033;
    font-size: 0.875rem;
  }

  .score-row span {
    min-width: 0;
    overflow-wrap: anywhere;
  }

  .score-row small {
    grid-column: 1 / -1;
    color: #667085;
    font-size: 0.75rem;
  }

  .trend-area {
    fill: rgba(37, 99, 235, 0.08);
  }

  .gridline,
  .baseline {
    stroke: #e5e7eb;
    stroke-width: 1;
  }

  .trend-line {
    fill: none;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.58;
  }

  .trend-line.item-primary {
    stroke-width: 3;
    opacity: 1;
  }

  .point {
    fill: #ffffff;
    stroke: #2563eb;
    stroke-width: 2;
  }

  .date-label {
    text-anchor: middle;
  }

  .error-list {
    display: grid;
    gap: 0.75rem;
  }

  .error-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 1rem;
    padding: 0.875rem 0;
    border-top: 1px solid #eef2f7;
  }

  .error-row:first-child {
    border-top: 0;
    padding-top: 0;
  }

  .error-main {
    min-width: 0;
  }

  .error-title {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
    color: #172033;
    font-size: 0.9rem;
  }

  .category {
    color: #ffffff;
    border-radius: 999px;
    padding: 0.125rem 0.5rem;
    font-size: 0.7rem;
    line-height: 1.4;
  }

  .bar-track {
    width: 100%;
    height: 0.5rem;
    margin: 0.5rem 0;
    overflow: hidden;
    background: #eef2f7;
    border-radius: 999px;
  }

  .bar {
    display: block;
    height: 100%;
    min-width: 0.5rem;
    border-radius: inherit;
  }

  .error-main small {
    display: block;
    margin-top: 0.25rem;
    color: #475467;
    line-height: 1.4;
  }

  .error-count {
    display: grid;
    justify-items: end;
    align-content: start;
    gap: 0.125rem;
    color: #667085;
    font-size: 0.75rem;
    text-transform: capitalize;
  }

  .error-count strong {
    color: #172033;
    font-size: 1.35rem;
    line-height: 1;
  }

  @media (max-width: 760px) {
    .panel {
      padding: 0.875rem;
    }

    .panel-heading,
    .radar-layout,
    .error-row {
      grid-template-columns: 1fr;
    }

    .panel-heading {
      display: grid;
    }

    .legend {
      justify-content: flex-start;
      white-space: normal;
    }

    .error-count {
      justify-items: start;
    }
  }
</style>
