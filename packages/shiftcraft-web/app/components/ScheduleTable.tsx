import { Badge } from "@/components/ui/badge";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import type { DayEntry, ShiftType } from "@/lib/types";

const SHIFT_STYLES: Record<ShiftType, string> = {
    morning: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
    afternoon: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
    night: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300",
    regular: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
    week_off: "bg-muted text-muted-foreground",
    annual: "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300",
    comp_off: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300",
};

const SHIFT_LABEL: Record<ShiftType, string> = {
    morning: "M", afternoon: "A", night: "N", regular: "R",
    week_off: "WO", annual: "AL", comp_off: "CO",
};

function ShiftBadge({ shift }: { shift: string }) {
    const style = SHIFT_STYLES[shift as ShiftType] ?? "bg-muted text-muted-foreground";
    const label = SHIFT_LABEL[shift as ShiftType] ?? shift;
    return (
        <Badge variant="outline" className={`text-xs font-semibold border-0 ${style}`}>
            {label}
        </Badge>
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
        <ScrollArea className="rounded-md border">
            <table className="min-w-full text-sm">
                <thead className="bg-muted/50 border-b">
                    <tr>
                        <th className="sticky left-0 bg-muted/50 px-4 py-2.5 text-left text-xs font-medium text-muted-foreground whitespace-nowrap">
                            Date
                        </th>
                        {employees.map((emp) => (
                            <th key={emp} className="px-4 py-2.5 text-center text-xs font-medium text-muted-foreground whitespace-nowrap">
                                {emp}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-border">
                    {schedule.map((day) => {
                        const d = new Date(day.date + "T00:00:00");
                        const isWeekend = d.getDay() === 0 || d.getDay() === 6;
                        return (
                            <tr key={day.date} className={isWeekend ? "bg-muted/20" : ""}>
                                <td className="sticky left-0 bg-background px-4 py-2 font-mono text-xs text-muted-foreground whitespace-nowrap">
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
            <ScrollBar orientation="horizontal" />
        </ScrollArea>
    );
}
