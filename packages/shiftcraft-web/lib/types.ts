// --- Output types ---

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

// --- Input types ---

export type LeaveRequest = {
    date: string;
    leave_type: "annual" | "comp_off" | "week_off" | null;
};

export type CompOffRecord = {
    holiday_date: string;
    redeemed_on: string | null;
};

export type ShiftHistory = {
    morning: number;
    afternoon: number;
    night: number;
    regular: number;
    week_off: number;
    leave: number;
};

export type Employee = {
    id: string;
    name: string;
    is_senior: boolean;
    city: string;
    comp_off_balance: number;
    leave_requests: LeaveRequest[];
    previous_week_days: Record<string, string>;
    history: {
        last_month_shift_counts: ShiftHistory;
        comp_off: {
            remaining_count: number;
            records: CompOffRecord[];
        };
    };
};

export type CoverageSlot = {
    min: number;
    target: number;
    max: number;
};

export type DayCoverage = {
    morning: CoverageSlot;
    afternoon: CoverageSlot;
    night: CoverageSlot;
    regular: CoverageSlot;
};

export type DateRangeOverride = {
    start: string;
    end: string;
    morning: CoverageSlot;
    afternoon: CoverageSlot;
    night: CoverageSlot;
    regular: CoverageSlot;
};

export type Holiday = {
    date: string;
    locations: string[];
};

export type ScheduleInput = {
    period: { start: string; end: string };
    team: Employee[];
    coverage: {
        by_day_of_week: Record<string, DayCoverage>;
        by_date_range: DateRangeOverride[];
    };
    holidays: Holiday[];
};
