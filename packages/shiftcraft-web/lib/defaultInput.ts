import type { Employee, ScheduleInput, ScheduleSettings } from "./types";

const SETTINGS_STORAGE_KEY = "shiftcraft:settings";

export const DEFAULT_SETTINGS: ScheduleSettings = {
    shifts: ["morning", "afternoon", "night", "regular"],
    leave_types: ["week_off", "annual", "comp_off", "public_holiday"],
    rules: [],
    solver: { time_limit_seconds: 60, relative_gap_limit: 0.02 },
};

export const DEFAULT_INPUT: ScheduleInput = {
    period: { start: "2026-04-01", end: "2026-04-30" },
    team: [],
    holidays: [],
};

/** Load settings from localStorage, falling back to DEFAULT_SETTINGS. */
export function loadSettings(): ScheduleSettings {
    if (typeof window === "undefined") return DEFAULT_SETTINGS;
    try {
        const raw = localStorage.getItem(SETTINGS_STORAGE_KEY);
        return raw ? (JSON.parse(raw) as ScheduleSettings) : DEFAULT_SETTINGS;
    } catch {
        return DEFAULT_SETTINGS;
    }
}

/** Persist settings to localStorage. */
export function saveSettings(settings: ScheduleSettings): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
}

export function newEmployee(index: number): Employee {
    return {
        id: `E${String(index).padStart(3, "0")}`,
        name: "",
        attributes: {},
        balances: {},
        records: {},
        history: { last_month_shift_counts: {} },
        previous_week_days: {},
    };
}
