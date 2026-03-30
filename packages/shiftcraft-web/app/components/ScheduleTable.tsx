import type { DayEntry, ShiftType } from "@/lib/types";

const SHIFT_STYLES: Record<ShiftType, string> = {
    morning: "bg-amber-100 text-amber-800",
    afternoon: "bg-blue-100 text-blue-800",
    night: "bg-indigo-100 text-indigo-800",
    regular: "bg-green-100 text-green-800",
    week_off: "bg-zinc-100 text-zinc-500",
    annual: "bg-rose-100 text-rose-700",
    comp_off: "bg-purple-100 text-purple-700",
};

const SHIFT_LABEL: Record<ShiftType, string> = {
    morning: "M",
    afternoon: "A",
    night: "N",
    regular: "R",
    week_off: "WO",
    annual: "AL",
    comp_off: "CO",
};

function ShiftBadge({ shift }: { shift: string }) {
    const style = SHIFT_STYLES[shift as ShiftType] ?? "bg-zinc-100 text-zinc-600";
    const label = SHIFT_LABEL[shift as ShiftType] ?? shift;
    return (
        <span className={`inline-block rounded px-1.5 py-0.5 text-xs font-semibold ${style}`}>
            {label}
        </span>
    );
}

function formatDate(iso: string) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", weekday: "short" });
}

export function ScheduleTable({ schedule }: { schedule: DayEntry[] }) {
    if (!schedule.length) return null;

    const employees = Object.keys(schedule[0]).filter((k) => k !== "date");

    return (
        <div className="overflow-x-auto rounded-lg border border-zinc-200">
            <table className="min-w-full text-sm">
                <thead className="bg-zinc-50 border-b border-zinc-200">
                    <tr>
                        <th className="sticky left-0 bg-zinc-50 px-4 py-2 text-left font-medium text-zinc-600 whitespace-nowrap">
                            Date
                        </th>
                        {employees.map((emp) => (
                            <th key={emp} className="px-4 py-2 text-center font-medium text-zinc-600 whitespace-nowrap">
                                {emp}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100">
                    {schedule.map((day) => {
                        const d = new Date(day.date + "T00:00:00");
                        const isWeekend = d.getDay() === 0 || d.getDay() === 6;
                        return (
                            <tr key={day.date} className={isWeekend ? "bg-zinc-50/60" : "bg-white"}>
                                <td className="sticky left-0 bg-inherit px-4 py-2 font-mono text-xs text-zinc-500 whitespace-nowrap">
                                    {formatDate(day.date)}
                                </td>
                                {employees.map((emp) => (
                                    <td key={emp} className="px-4 py-2 text-center">
                                        <ShiftBadge shift={day[emp]} />
                                    </td>
                                ))}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
