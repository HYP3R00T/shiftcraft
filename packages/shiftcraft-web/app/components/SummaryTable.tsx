import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import type { EmployeeSummary } from "@/lib/types";

const COLS: (keyof EmployeeSummary)[] = [
    "morning", "afternoon", "night", "regular", "week_off", "annual", "comp_off",
];

const COL_LABEL: Record<keyof EmployeeSummary, string> = {
    morning: "Morning", afternoon: "Afternoon", night: "Night", regular: "Regular",
    week_off: "Week Off", annual: "Annual", comp_off: "Comp Off",
};

export function SummaryTable({ summary }: { summary: Record<string, EmployeeSummary> }) {
    return (
        <ScrollArea className="rounded-md border">
            <table className="min-w-full text-sm">
                <thead className="bg-muted/50 border-b">
                    <tr>
                        <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Employee</th>
                        {COLS.map((col) => (
                            <th key={col} className="px-4 py-2.5 text-center text-xs font-medium text-muted-foreground">
                                {COL_LABEL[col]}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-border">
                    {Object.entries(summary).map(([emp, counts]) => (
                        <tr key={emp} className="hover:bg-muted/30 transition-colors">
                            <td className="px-4 py-2.5 font-medium">{emp}</td>
                            {COLS.map((col) => (
                                <td key={col} className="px-4 py-2.5 text-center font-mono text-xs text-muted-foreground">
                                    {counts[col]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
            <ScrollBar orientation="horizontal" />
        </ScrollArea>
    );
}
