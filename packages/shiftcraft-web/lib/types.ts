export type ShiftType =
    | "morning"
    | "afternoon"
    | "night"
    | "regular"
    | "week_off"
    | "annual"
    | "comp_off";

export type DayEntry = {
    date: string;
    [employee: string]: string;
};

export type EmployeeSummary = {
    morning: number;
    afternoon: number;
    night: number;
    regular: number;
    week_off: number;
    annual: number;
    comp_off: number;
};

export type ScheduleResult = {
    status: "ok" | "feasible" | "infeasible" | "unknown";
    schedule?: DayEntry[];
    summary?: Record<string, EmployeeSummary>;
    penalty?: number;
    conflicts?: string[];
};
