export function exportScheduleCsv(
  schedule: Record<string, Record<string, string>>,
  filename = "schedule.csv"
) {
  const dates = Object.keys(schedule).sort();
  if (!dates.length) return;

  const employees = Object.keys(schedule[dates[0]]);
  const header = ["Date", ...employees].join(",");
  const rows = dates.map((date) =>
    [date, ...employees.map((e) => schedule[date][e] ?? "")].join(",")
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
