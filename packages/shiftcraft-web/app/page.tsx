"use client";

import { useState } from "react";
import { Download, Plus, FileJson } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ThemeToggle } from "@/components/theme-toggle";
import { DatePicker } from "@/components/date-picker";
import { generateSchedule } from "@/lib/api";
import { DEFAULT_INPUT, newEmployee } from "@/lib/defaultInput";
import { exportScheduleCsv } from "@/lib/exportCsv";
import type { ScheduleInput, ScheduleResult } from "@/lib/types";
import { EmployeeEditor } from "./components/EmployeeEditor";
import { JsonImport } from "./components/JsonImport";
import { ScheduleTable } from "./components/ScheduleTable";
import { SummaryTable } from "./components/SummaryTable";

export default function Home() {
    const [input, setInput] = useState<ScheduleInput>(DEFAULT_INPUT);
    const [result, setResult] = useState<ScheduleResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleGenerate() {
        setError(null);
        setResult(null);
        setLoading(true);
        try {
            setResult(await generateSchedule(input));
        } catch (e) {
            setError(e instanceof Error ? e.message : "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    function exportJson() {
        const blob = new Blob([JSON.stringify(input, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `shiftcraft-input-${input.period.start.slice(0, 7)}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    const isSuccess = result && (result.status === "ok" || result.status === "feasible");

    return (
        <div className="flex flex-col h-screen overflow-hidden bg-background">
            {/* Header — always visible */}
            <header className="border-b px-6 py-3 flex items-center justify-between shrink-0 bg-background z-10">
                <div className="flex items-center gap-3">
                    <span className="text-base font-semibold">Shiftcraft</span>
                    <span className="text-xs text-muted-foreground hidden sm:block">workforce scheduler</span>
                </div>
                <div className="flex items-center gap-2">
                    <JsonImport onImport={(parsed) => { setInput(parsed); setResult(null); }} />
                    <Button variant="outline" size="sm" onClick={exportJson} className="gap-1.5">
                        <FileJson className="h-3.5 w-3.5" /> Export JSON
                    </Button>
                    <Separator orientation="vertical" className="h-5" />
                    <Button size="sm" onClick={handleGenerate} disabled={loading || input.team.length === 0} className="gap-1.5">
                        {loading ? (
                            <>
                                <span className="h-3.5 w-3.5 rounded-full border-2 border-current border-t-transparent animate-spin" />
                                Solving…
                            </>
                        ) : "Generate Schedule"}
                    </Button>
                    <ThemeToggle />
                </div>
            </header>

            {/* Body — fills remaining height, panels scroll independently */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left: Input panel — scrolls independently */}
                <div className="w-[420px] shrink-0 border-r overflow-y-auto p-5 space-y-6">

                    {/* Period */}
                    <div className="space-y-3">
                        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Period</p>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1">
                                <Label className="text-xs">Start date</Label>
                                <DatePicker
                                    value={input.period.start}
                                    onChange={(v) => setInput((p) => ({ ...p, period: { ...p.period, start: v } }))}
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs">End date</Label>
                                <DatePicker
                                    value={input.period.end}
                                    onChange={(v) => setInput((p) => ({ ...p, period: { ...p.period, end: v } }))}
                                />
                            </div>
                        </div>
                    </div>

                    <Separator />

                    {/* Team */}
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                Team <span className="text-foreground">({input.team.length})</span>
                            </p>
                            <Button variant="outline" size="sm" className="h-7 text-xs gap-1"
                                onClick={() => setInput((p) => ({ ...p, team: [...p.team, newEmployee(p.team.length + 1)] }))}>
                                <Plus className="h-3 w-3" /> Add employee
                            </Button>
                        </div>

                        {input.team.length === 0 ? (
                            <div className="border border-dashed p-6 text-center space-y-1">
                                <p className="text-sm text-muted-foreground">No employees yet.</p>
                                <p className="text-xs text-muted-foreground">Add manually or import a JSON file.</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {input.team.map((emp, i) => (
                                    <EmployeeEditor key={emp.id + i} employee={emp}
                                        onChange={(u) => { const t = [...input.team]; t[i] = u; setInput((p) => ({ ...p, team: t })); }}
                                        onRemove={() => setInput((p) => ({ ...p, team: p.team.filter((_, idx) => idx !== i) }))}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Results panel — scrolls independently */}
                <div className="flex-1 overflow-y-auto p-5">
                    {!result && !error && !loading && (
                        <div className="flex flex-col items-center justify-center h-full text-center gap-3">
                            <div className="text-4xl">📅</div>
                            <p className="text-muted-foreground text-sm">Configure your team on the left, then click Generate Schedule.</p>
                            <p className="text-muted-foreground/60 text-xs">Or use Import JSON to load an existing payload.</p>
                        </div>
                    )}

                    {loading && (
                        <div className="flex flex-col items-center justify-center h-full gap-4">
                            <div className="h-8 w-8 rounded-full border-2 border-muted border-t-foreground animate-spin" />
                            <p className="text-muted-foreground text-sm">Solving schedule…</p>
                        </div>
                    )}

                    {error && (
                        <div className="border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                            {error}
                        </div>
                    )}

                    {result?.status === "infeasible" && (
                        <div className="border border-destructive/50 bg-destructive/10 px-4 py-4 space-y-3">
                            <p className="text-sm font-medium text-destructive">No valid schedule found</p>
                            <ul className="list-disc pl-5 space-y-1">
                                {result.conflicts?.map((c, i) => (
                                    <li key={i} className="text-xs text-destructive/80">{c}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {isSuccess && result.schedule && result.summary && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    {result.status === "ok"
                                        ? <Badge variant="outline" className="text-emerald-600 border-emerald-600/30 bg-emerald-50 dark:bg-emerald-950/30">Optimal</Badge>
                                        : <Badge variant="outline" className="text-amber-600 border-amber-600/30 bg-amber-50 dark:bg-amber-950/30">Feasible</Badge>
                                    }
                                    <span className="text-xs text-muted-foreground">
                                        Penalty: <span className="font-mono text-foreground">{result.penalty}</span>
                                    </span>
                                </div>
                                <Button variant="outline" size="sm" className="gap-1.5"
                                    onClick={() => exportScheduleCsv(result.schedule!, `schedule-${result.schedule![0].date.slice(0, 7)}.csv`)}>
                                    <Download className="h-3.5 w-3.5" /> Download CSV
                                </Button>
                            </div>

                            <Tabs defaultValue="schedule">
                                <TabsList>
                                    <TabsTrigger value="schedule">Schedule</TabsTrigger>
                                    <TabsTrigger value="summary">Summary</TabsTrigger>
                                </TabsList>
                                <TabsContent value="schedule" className="mt-4">
                                    <ScheduleTable schedule={result.schedule} />
                                </TabsContent>
                                <TabsContent value="summary" className="mt-4">
                                    <SummaryTable summary={result.summary} />
                                </TabsContent>
                            </Tabs>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
