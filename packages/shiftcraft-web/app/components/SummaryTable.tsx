import type { EmployeeSummary } from "@/lib/types";

const COLS: (keyof EmployeeSummary)[] = [
    "morning", "afternoon", "night", "regular", "week_off", "annual", "comp_off",
];

const COL_LABEL: Record<keyof EmployeeSummary, string> = {
    morning: "Morning",
    afternoon: "Afternoon",
    night: "Night",
    regular: "Regular",
    week_off: "Week Off",
    annual: "Annual",
    comp_off: "Comp Off",
};

export function SummaryTable({ summary }: { summary: Record<string, EmployeeSummary> }) {
    const employees = Object.keys(summary);

    return (
        <div className="overflow-x-auto rounded-lg border border-zinc-700">
            <table className="min-w-full text-sm">
                <thead className="bg-zinc-800/80 border-b border-zinc-700">
                    <tr>
                        <th className="px-4 py-2.5 text-left text-xs font-medium text-zinc-400">Employee</th>
                        {COLS.map((col) => (
                            <th key={col} className="px-4 py-2.5 text-center text-xs font-medium text-zinc-400">
                                {COL_LABEL[col]}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                    {employees.map((emp) => (
                        <tr key={emp} className="hover:bg-zinc-800/30 transition">
                            <td className="px-4 py-2.5 font-medium text-zinc-200">{emp}</td>
                            {COLS.map((col) => (
                                <td key={col} className="px-4 py-2.5 text-center text-zinc-400 font-mono text-xs">
                                    {summary[emp][col]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
