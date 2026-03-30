import type { DayEntry, ShiftType } from "@/lib/types";

const SHIFT_STYLES: Record<ShiftType, string> = {
    morning: "bg-amber-900/50 text-amber-300",
    afternoon: "bg-blue-900/50 text-blue-300",
    night: "bg-indigo-900/50 text-indigo-300",
    regular: "bg-emerald-900/50 text-emerald-300",
    week_off: "bg-zinc-800 text-zinc-500",
    annual: "bg-rose-900/50 text-rose-300",
    comp_off: "bg-purple-900/50 text-purple-300",
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
    const style = SHIFT_STYLES[shift as ShiftType] ?? "bg-zinc-800 text-zinc-400";
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
        <div className="overflow-x-auto rounded-lg border border-zinc-700">
            <table className="min-w-full text-sm">
                <thead className="bg-zinc-800/80 border-b border-zinc-700">
                    <tr>
                        <th className="sticky left-0 bg-zinc-800 px-4 py-2.5 text-left text-xs font-medium text-zinc-400 whitespace-nowrap">
                            Date
                        </th>
                        {employees.map((emp) => (
                            <th key={emp} className="px-4 py-2.5 text-center text-xs font-medium text-zinc-400 whitespace-nowrap">
                                {emp}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                    {schedule.map((day) => {
                        const d = new Date(day.date + "T00:00:00");
                        const isWeekend = d.getDay() === 0 || d.getDay() === 6;
                        return (
                            <tr key={day.date} className={isWeekend ? "bg-zinc-800/30" : "bg-transparent"}>
                                <td className="sticky left-0 bg-[#0f1117] px-4 py-2 font-mono text-xs text-zinc-500 whitespace-nowrap">
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
