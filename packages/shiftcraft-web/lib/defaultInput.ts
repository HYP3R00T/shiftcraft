import type { ScheduleInput } from "./types";

const WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"];
const WEEKEND = ["saturday", "sunday"];

export const DEFAULT_INPUT: ScheduleInput = {
    period: { start: "2026-04-01", end: "2026-04-30" },
    team: [],
    coverage: {
        by_day_of_week: Object.fromEntries([
            ...WEEKDAYS.map((d) => [
                d,
                {
                    morning: { min: 1, target: 1, max: 1 },
                    afternoon: { min: 1, target: 1, max: 1 },
                    night: { min: 1, target: 1, max: 1 },
                    regular: { min: 0, target: 1, max: 1 },
                },
            ]),
            ...WEEKEND.map((d) => [
                d,
                {
                    morning: { min: 1, target: 1, max: 1 },
                    afternoon: { min: 1, target: 1, max: 1 },
                    night: { min: 1, target: 1, max: 1 },
                    regular: { min: 0, target: 0, max: 0 },
                },
            ]),
        ]),
        by_date_range: [],
    },
    holidays: [],
};

export function newEmployee(index: number) {
    return {
        id: `E${String(index).padStart(3, "0")}`,
        name: "",
        is_senior: false,
        city: "",
        comp_off_balance: 0,
        leave_requests: [],
        previous_week_days: {},
        history: {
            last_month_shift_counts: {
                morning: 0,
                afternoon: 0,
                night: 0,
                regular: 0,
                week_off: 0,
                leave: 0,
            },
            comp_off: { remaining_count: 0, records: [] },
        },
    };
}
