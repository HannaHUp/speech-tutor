<script lang="ts">
  import DashboardCharts from "./DashboardCharts.svelte";
  import { demoDashboardData, type DashboardData } from "./dashboardData";

  let { data = demoDashboardData }: { data?: DashboardData } = $props();

  function trendLabel(trend?: "up" | "down" | "flat") {
    if (trend === "up") return "Improving";
    if (trend === "down") return "Needs focus";
    return "Stable";
  }
</script>

<div class="dashboard">
  <header class="dashboard-header">
    <div>
      <p class="eyebrow">Evidence dashboard</p>
      <h1>{data.learner.name}</h1>
      <p class="learner-goal">{data.learner.goal}</p>
    </div>
    <div class="estimate">
      <span>Current estimate</span>
      <strong>{data.learner.currentEstimate}</strong>
      {#if data.learner.targetDate}
        <small>Target review: {data.learner.targetDate}</small>
      {/if}
    </div>
  </header>

  <section class="metrics" aria-label="Dashboard metrics">
    {#each data.metrics as metric}
      <article class="metric-card">
        <div>
          <span>{metric.label}</span>
          <strong>{metric.value}</strong>
        </div>
        {#if metric.detail}
          <p>{metric.detail}</p>
        {/if}
        <small class:focus={metric.trend === "down"}>{trendLabel(metric.trend)}</small>
      </article>
    {/each}
  </section>

  <section class="chart-grid" aria-label="Skill and trend charts">
    <DashboardCharts kind="radar" skills={data.skills} />
    <DashboardCharts kind="trend" trend={data.trend} />
  </section>

  <section class="recommendation" aria-labelledby="recommendation-title">
    <div class="recommendation-copy">
      <p class="eyebrow">Teacher next action</p>
      <h2 id="recommendation-title">{data.recommendation.title}</h2>
      <p>{data.recommendation.summary}</p>
      <strong>{data.recommendation.activity}</strong>
    </div>
    <div class="evidence-list">
      <span>Why</span>
      <ul>
        {#each data.recommendation.evidence as item}
          <li>{item}</li>
        {/each}
      </ul>
    </div>
  </section>

  <DashboardCharts kind="errors" errors={data.errors} />

  <section class="sessions" aria-labelledby="sessions-title">
    <div class="section-heading">
      <div>
        <h2 id="sessions-title">Recent Sessions</h2>
        <p>Fixture evidence ready to be replaced by session summaries later.</p>
      </div>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Mode</th>
            <th>Minutes</th>
            <th>Focus</th>
            <th>Accuracy</th>
            <th>Fluency</th>
            <th>Top signal</th>
            <th>Next action</th>
          </tr>
        </thead>
        <tbody>
          {#each data.sessions as session}
            <tr>
              <td>{session.date}</td>
              <td>{session.mode}</td>
              <td>{session.minutes}</td>
              <td>{session.focus}</td>
              <td>{session.accuracy}%</td>
              <td>{session.fluency}</td>
              <td>{session.topSignal}</td>
              <td>{session.nextAction}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>
</div>

<style>
  .dashboard {
    display: grid;
    gap: 1rem;
  }

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
    padding: 1rem 0 0.25rem;
  }

  .eyebrow {
    margin: 0 0 0.25rem;
    color: #2563eb;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
  }

  h1,
  h2,
  p {
    margin: 0;
  }

  h1 {
    color: #172033;
    font-size: 1.8rem;
    line-height: 1.15;
  }

  h2 {
    color: #172033;
    font-size: 1rem;
    line-height: 1.3;
  }

  .learner-goal,
  .section-heading p,
  .recommendation p {
    color: #667085;
    line-height: 1.45;
  }

  .estimate {
    min-width: 14rem;
    padding: 0.875rem 1rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .estimate span,
  .estimate small,
  .metric-card span,
  .metric-card small {
    display: block;
    color: #667085;
    font-size: 0.75rem;
  }

  .estimate strong {
    display: block;
    margin: 0.25rem 0;
    color: #172033;
    font-size: 1rem;
  }

  .metrics {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 0.75rem;
  }

  .metric-card {
    display: grid;
    align-content: space-between;
    min-height: 8.5rem;
    min-width: 0;
    padding: 0.875rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .metric-card strong {
    display: block;
    margin-top: 0.3rem;
    color: #172033;
    font-size: 1.3rem;
    line-height: 1.1;
    overflow-wrap: anywhere;
  }

  .metric-card p {
    color: #667085;
    font-size: 0.8rem;
    line-height: 1.4;
  }

  .metric-card small {
    color: #15803d;
    font-weight: 700;
  }

  .metric-card small.focus {
    color: #d97706;
  }

  .chart-grid {
    display: grid;
    grid-template-columns: minmax(20rem, 0.86fr) minmax(24rem, 1.14fr);
    gap: 1rem;
  }

  .recommendation,
  .sessions {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
  }

  .recommendation {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(18rem, 0.75fr);
    gap: 1.25rem;
    border-left: 4px solid #2563eb;
  }

  .recommendation-copy {
    display: grid;
    gap: 0.625rem;
    align-content: start;
  }

  .recommendation-copy strong {
    color: #172033;
    line-height: 1.45;
  }

  .evidence-list {
    padding-left: 1rem;
    border-left: 1px solid #e5e7eb;
  }

  .evidence-list span {
    color: #172033;
    font-size: 0.875rem;
    font-weight: 700;
  }

  ul {
    margin: 0.5rem 0 0;
    padding-left: 1.125rem;
    color: #475467;
  }

  li {
    margin: 0.35rem 0;
    line-height: 1.45;
  }

  .section-heading {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.875rem;
  }

  .table-wrap {
    width: 100%;
    overflow-x: auto;
  }

  table {
    width: 100%;
    min-width: 58rem;
    border-collapse: collapse;
    color: #172033;
    font-size: 0.875rem;
  }

  th,
  td {
    padding: 0.75rem 0.625rem;
    border-top: 1px solid #eef2f7;
    text-align: left;
    vertical-align: top;
  }

  th {
    color: #667085;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
  }

  td {
    line-height: 1.4;
  }

  @media (max-width: 1180px) {
    .metrics {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .chart-grid,
    .recommendation {
      grid-template-columns: 1fr;
    }

    .evidence-list {
      padding-left: 0;
      border-left: 0;
    }
  }

  @media (max-width: 700px) {
    .dashboard-header {
      display: grid;
      align-items: start;
    }

    .estimate {
      min-width: 0;
    }

    .metrics {
      grid-template-columns: 1fr;
    }

    .metric-card {
      min-height: auto;
      gap: 0.75rem;
    }
  }
</style>
