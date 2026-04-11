// ── Settings types ────────────────────────────────────────────────────────────

export type RuleScope = {
    who: Record<string, unknown>;
    when: Record<string, unknown>;
};

export type Rule = {
    id: string;
    type: string;
    label?: string;
    scope: RuleScope;
    enforcement: "hard" | "soft" | "preference";
    weight?: "high" | "medium" | "low";
    overrides?: string[];
    [key: string]: unknown; // primitive-specific params
};

export type SolverConfig = {
    time_limit_seconds?: number;
    log_progress?: boolean;
    num_workers?: number;
    linearization_level?: number;
    relative_gap_limit?: number;
};

export type ScheduleSettings = {
    shifts: string[];
    leave_types: string[];
    rules: Rule[];
    solver: SolverConfig;
};

// ── Output types ──────────────────────────────────────────────────────────────

export type SolverStatus = "optimal" | "feasible" | "infeasible" | "unknown" | "model_invalid";

export type ScheduleResult = {
    status: SolverStatus;
    // date-keyed: { "2026-04-01": { "E001": "morning", ... }, ... }
    schedule: Record<string, Record<string, string>>;
    metadata: {
        status: SolverStatus;
        solve_time_seconds: number;
        objective: number | null;
    };
};

// ── Input types ───────────────────────────────────────────────────────────────

export type CompOffRecord = {
    earned_date: string;
    redeemed_on: string | null;
};

export type EmployeeHistory = {
    last_month_shift_counts: Record<string, number>;
    previous_state_run?: { value: string; count: number } | null;
};

export type Employee = {
    id: string;
    name: string;
    attributes: Record<string, string>;
    balances: Record<string, number>;
    records: Record<string, CompOffRecord[]>;
    history: EmployeeHistory;
    previous_week_days: Record<string, string>;
};

export type Holiday = {
    date: string;
    locations: string[];
};

export type ScheduleInput = {
    period: { start: string; end: string };
    team: Employee[];
    holidays: Holiday[];
};

// ── Display helpers ───────────────────────────────────────────────────────────

// Known shift/leave states for styling — open-ended, unknown states fall back gracefully.
export type KnownState =
    | "morning"
    | "afternoon"
    | "night"
    | "regular"
    | "week_off"
    | "annual"
    | "comp_off"
    | "public_holiday";
