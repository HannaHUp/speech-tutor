export type DashboardMetric = {
  label: string;
  value: string;
  detail?: string;
  trend?: "up" | "down" | "flat";
};

export type SkillScore = {
  label: string;
  average: number;
  latest: number;
};

export type TrendPoint = {
  date: string;
  overall: number;
  accuracy: number;
  fluency: number;
  pronunciation: number;
};

export type ErrorPattern = {
  tag: string;
  label: string;
  count: number;
  category: "reading" | "grammar" | "pronunciation" | "fluency" | "interaction";
  example: string;
  nextDrill: string;
  trend: "improving" | "stable" | "worse";
};

export type RecentSession = {
  date: string;
  mode: string;
  minutes: number;
  focus: string;
  accuracy: number;
  fluency: number;
  topSignal: string;
  nextAction: string;
};

export type DashboardChartKind = "radar" | "trend" | "errors";

export type DashboardData = {
  learner: {
    name: string;
    goal: string;
    currentEstimate: string;
    targetDate?: string;
  };
  metrics: DashboardMetric[];
  skills: SkillScore[];
  trend: TrendPoint[];
  errors: ErrorPattern[];
  sessions: RecentSession[];
  recommendation: {
    title: string;
    summary: string;
    evidence: string[];
    activity: string;
  };
};

export const demoDashboardData: DashboardData = {
  learner: {
    name: "Maya",
    goal: "B1 -> B2 workplace speaking",
    currentEstimate: "B1+ Hermes estimate",
    targetDate: "June 2026",
  },
  metrics: [
    {
      label: "Hermes estimate",
      value: "B1+",
      detail: "Goal: B2 workplace speaking",
      trend: "up",
    },
    {
      label: "Sessions",
      value: "8",
      detail: "5 sessions in the latest cycle",
      trend: "flat",
    },
    {
      label: "Speaking minutes",
      value: "46",
      detail: "18 minutes from read-aloud evidence",
      trend: "up",
    },
    {
      label: "Oral accuracy",
      value: "86%",
      detail: "Stable across the last 3 sessions",
      trend: "flat",
    },
    {
      label: "Fluency",
      value: "72/100",
      detail: "Up from 64 at the start of cycle",
      trend: "up",
    },
    {
      label: "Biggest issue",
      value: "Omissions",
      detail: "Most visible in adjective-rich noun phrases",
      trend: "down",
    },
  ],
  skills: [
    { label: "Accuracy", average: 82, latest: 86 },
    { label: "Fluency", average: 68, latest: 72 },
    { label: "Pronunciation", average: 74, latest: 76 },
    { label: "Vocabulary", average: 70, latest: 74 },
    { label: "Coherence", average: 73, latest: 78 },
    { label: "Self-correction", average: 61, latest: 69 },
  ],
  trend: [
    { date: "Apr 24", overall: 66, accuracy: 79, fluency: 64, pronunciation: 70 },
    { date: "Apr 27", overall: 68, accuracy: 81, fluency: 65, pronunciation: 72 },
    { date: "May 01", overall: 70, accuracy: 82, fluency: 67, pronunciation: 72 },
    { date: "May 04", overall: 71, accuracy: 84, fluency: 69, pronunciation: 73 },
    { date: "May 08", overall: 73, accuracy: 85, fluency: 70, pronunciation: 74 },
    { date: "May 11", overall: 75, accuracy: 86, fluency: 72, pronunciation: 76 },
  ],
  errors: [
    {
      tag: "omission",
      label: "Omitted modifiers",
      count: 6,
      category: "reading",
      example: 'Expected "the small bird"; observed "the bird"',
      nextDrill: "Reread adjective-rich noun phrases, then retell in 30 seconds",
      trend: "improving",
    },
    {
      tag: "past_tense_error",
      label: "Past tense slips",
      count: 5,
      category: "grammar",
      example: 'Said "Yesterday I walk to the office"',
      nextDrill: "Contrast present and past workplace routines",
      trend: "stable",
    },
    {
      tag: "long_pause",
      label: "Planning pauses",
      count: 4,
      category: "fluency",
      example: "Paused 3+ seconds before giving the reason",
      nextDrill: "Use because/so sentence frames under a short timer",
      trend: "improving",
    },
    {
      tag: "unclear_word_stress",
      label: "Word stress unclear",
      count: 3,
      category: "pronunciation",
      example: 'Stress shifted in "delivery" and "manager"',
      nextDrill: "Mark stress before recording two-sentence answers",
      trend: "stable",
    },
    {
      tag: "limited_follow_up",
      label: "Short follow-up",
      count: 2,
      category: "interaction",
      example: "Answered the prompt but did not extend with detail",
      nextDrill: "Add one detail and one reason after each answer",
      trend: "worse",
    },
  ],
  sessions: [
    {
      date: "May 11",
      mode: "retell practice",
      minutes: 7,
      focus: "past-tense storytelling",
      accuracy: 86,
      fluency: 72,
      topSignal: "omissions fell after reread",
      nextAction: "repeat short reread, then retell from memory",
    },
    {
      date: "May 08",
      mode: "workplace role-play",
      minutes: 6,
      focus: "explaining a delay",
      accuracy: 85,
      fluency: 70,
      topSignal: "long pauses before reasons",
      nextAction: "practice because/so frames with a timer",
    },
    {
      date: "May 04",
      mode: "passage read-aloud",
      minutes: 8,
      focus: "modifier accuracy",
      accuracy: 84,
      fluency: 69,
      topSignal: "adjectives omitted in noun phrases",
      nextAction: "underline modifiers before rereading",
    },
    {
      date: "May 01",
      mode: "picture description",
      minutes: 5,
      focus: "sequence and detail",
      accuracy: 82,
      fluency: 67,
      topSignal: "short follow-up answers",
      nextAction: "add one reason to each observation",
    },
    {
      date: "Apr 27",
      mode: "free conversation",
      minutes: 6,
      focus: "workplace routines",
      accuracy: 81,
      fluency: 65,
      topSignal: "past tense slips in stories",
      nextAction: "contrast today/yesterday routines",
    },
  ],
  recommendation: {
    title: "Recommended next action",
    summary:
      "Maya is improving fluency, but omissions still appear during read-aloud tasks. Keep the accuracy focus while increasing spoken output.",
    evidence: [
      "Omissions appeared 6 times across the last 5 sessions.",
      "Fluency improved from 64 to 72 while accuracy stayed above 84 in the last 3 sessions.",
      "Read-aloud evidence shows modifier omissions before free retell tasks.",
    ],
    activity:
      "Use a short reread passage with adjective-rich noun phrases, then ask for a 30-second oral retell using the same details.",
  },
};
