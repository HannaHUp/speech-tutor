import {
  demoDashboardData,
  type DashboardData,
  type ErrorPattern,
  type SkillScore,
  type TrendPoint,
} from "./dashboardData";

const data: DashboardData = demoDashboardData;

function assertPercentScore(score: number): asserts score is number {
  if (score < 0 || score > 100) {
    throw new Error(`Expected score from 0 to 100, received ${score}`);
  }
}

function assertTrendPoint(point: TrendPoint) {
  assertPercentScore(point.overall);
  assertPercentScore(point.accuracy);
  assertPercentScore(point.fluency);
  assertPercentScore(point.pronunciation);
}

function assertSkillScore(skill: SkillScore) {
  assertPercentScore(skill.average);
  assertPercentScore(skill.latest);
}

function assertErrorPattern(error: ErrorPattern) {
  if (!error.example || !error.nextDrill) {
    throw new Error(`Expected example and next drill for ${error.tag}`);
  }
}

if (data.skills.length !== 6) {
  throw new Error("Dashboard radar chart expects six skill dimensions");
}

if (data.trend.length < 5) {
  throw new Error("Dashboard trend chart expects at least five sessions");
}

data.metrics.forEach((metric) => {
  if (!metric.label || !metric.value) {
    throw new Error("Dashboard metrics must include labels and values");
  }
});
data.skills.forEach(assertSkillScore);
data.trend.forEach(assertTrendPoint);
data.errors.forEach(assertErrorPattern);
