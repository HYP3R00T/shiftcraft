import type { EmployeeSummary } from "@/lib/types";

const COLS: (keyof EmployeeSummary)[] = [
    "morning",
    "afternoon",
    "night",
    "regular",
    "week_off",
    "annual",
    "comp_off",
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
        <div className="overflow-x-auto rounded-lg border border-zinc-200">
            <table className="min-w-full text-sm">
                <thead className="bg-zinc-50 border-b border-zinc-200">
                    <tr>
                        <th className="px-4 py-2 text-left font-medium text-zinc-600">Employee</th>
                        {COLS.map((col) => (
                            <th key={col} className="px-4 py-2 text-center font-medium text-zinc-600">
                                {COL_LABEL[col]}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100">
                    {employees.map((emp) => (
                        <tr key={emp} className="bg-white hover:bg-zinc-50">
                            <td className="px-4 py-2 font-medium text-zinc-800">{emp}</td>
                            {COLS.map((col) => (
                                <td key={col} className="px-4 py-2 text-center text-zinc-600">
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
