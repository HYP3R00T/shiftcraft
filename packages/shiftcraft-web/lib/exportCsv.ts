import type { DayEntry } from "./types";

export function exportScheduleCsv(schedule: DayEntry[], filename = "schedule.csv") {
    const employees = Object.keys(schedule[0]).filter((k) => k !== "date");
    const header = ["Date", ...employees].join(",");
    const rows = schedule.map((day) =>
        [day.date, ...employees.map((e) => day[e])].join(",")
    );
    const csv = [header, ...rows].join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
