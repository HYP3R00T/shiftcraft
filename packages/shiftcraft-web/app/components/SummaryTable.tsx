import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

function computeSummary(schedule: Record<string, Record<string, string>>) {
  const summary: Record<string, Record<string, number>> = {};
  for (const empMap of Object.values(schedule)) {
    for (const [empId, state] of Object.entries(empMap)) {
      summary[empId] ??= {};
      summary[empId][state] = (summary[empId][state] ?? 0) + 1;
    }
  }
  return summary;
}

export function SummaryTable({ schedule }: { schedule: Record<string, Record<string, string>> }) {
  const summary = computeSummary(schedule);
  const employees = Object.keys(summary);
  if (!employees.length) return null;

  // Collect all state columns that appear in the data.
  const cols = [...new Set(Object.values(summary).flatMap(Object.keys))].sort();

  return (
    <ScrollArea className="rounded-md border">
      <table className="min-w-full text-sm">
        <thead className="bg-muted/50 border-b">
          <tr>
            <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Employee</th>
            {cols.map((col) => (
              <th key={col} className="px-4 py-2.5 text-center text-xs font-medium text-muted-foreground capitalize">
                {col.replace("_", " ")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {employees.map((emp) => (
            <tr key={emp} className="hover:bg-muted/30 transition-colors">
              <td className="px-4 py-2.5 font-medium">{emp}</td>
              {cols.map((col) => (
                <td key={col} className="px-4 py-2.5 text-center font-mono text-xs text-muted-foreground">
                  {summary[emp][col] ?? 0}
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
