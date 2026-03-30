"use client";

import { useState } from "react";
import { generateSchedule } from "@/lib/api";
import { DEFAULT_INPUT, newEmployee } from "@/lib/defaultInput";
import type { ScheduleInput, ScheduleResult } from "@/lib/types";
import { EmployeeEditor } from "./components/EmployeeEditor";
import { JsonImport } from "./components/JsonImport";
import { ScheduleTable } from "./components/ScheduleTable";
import { SummaryTable } from "./components/SummaryTable";
import { Btn, Field, Input, SectionTitle } from "./components/ui";

export default function Home() {
    const [input, setInput] = useState<ScheduleInput>(DEFAULT_INPUT);
    const [result, setResult] = useState<ScheduleResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState<"schedule" | "summary">("schedule");

    async function handleGenerate() {
        setError(null);
        setResult(null);
        setLoading(true);
        try {
            const res = await generateSchedule(input);
            setResult(res);
            setTab("schedule");
        } catch (e) {
            setError(e instanceof Error ? e.message : "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    function addEmployee() {
        setInput((prev) => ({
            ...prev,
            team: [...prev.team, newEmployee(prev.team.length + 1)],
        }));
    }

    function updateEmployee(i: number, emp: ScheduleInput["team"][number]) {
        setInput((prev) => {
            const team = [...prev.team];
            team[i] = emp;
            return { ...prev, team };
        });
    }

    function removeEmployee(i: number) {
        setInput((prev) => ({
            ...prev,
            team: prev.team.filter((_, idx) => idx !== i),
        }));
    }

    const isSuccess = result && (result.status === "ok" || result.status === "feasible");

    return (
        <div className="flex flex-col min-h-screen bg-[#0f1117]">
            {/* Header */}
            <header className="border-b border-zinc-800 bg-zinc-900/60 px-6 py-3 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-3">
                    <span className="text-base font-semibold text-zinc-100">Shiftcraft</span>
                    <span className="text-xs text-zinc-600">workforce scheduler</span>
                </div>
                <div className="flex items-center gap-2">
                    <JsonImport onImport={(parsed) => { setInput(parsed); setResult(null); }} />
                    <Btn onClick={handleGenerate} disabled={loading || input.team.length === 0}>
                        {loading ? "Generating…" : "Generate Schedule"}
                    </Btn>
                </div>
            </header>

            {/* Body */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left: Input panel */}
                <div className="w-[420px] shrink-0 border-r border-zinc-800 overflow-y-auto p-5 space-y-6">

                    {/* Period */}
                    <div>
                        <SectionTitle>Period</SectionTitle>
                        <div className="grid grid-cols-2 gap-3">
                            <Field label="Start date">
                                <Input
                                    type="date"
                                    value={input.period.start}
                                    onChange={(e) =>
                                        setInput((p) => ({ ...p, period: { ...p.period, start: e.target.value } }))
                                    }
                                />
                            </Field>
                            <Field label="End date">
                                <Input
                                    type="date"
                                    value={input.period.end}
                                    onChange={(e) =>
                                        setInput((p) => ({ ...p, period: { ...p.period, end: e.target.value } }))
                                    }
                                />
                            </Field>
                        </div>
                    </div>

                    {/* Team */}
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <SectionTitle>Team ({input.team.length})</SectionTitle>
                            <Btn variant="ghost" onClick={addEmployee} className="text-xs py-1 px-2">
                                + Add employee
                            </Btn>
                        </div>
                        {input.team.length === 0 ? (
                            <div className="rounded-lg border border-dashed border-zinc-700 p-6 text-center">
                                <p className="text-sm text-zinc-500">No employees yet.</p>
                                <p className="text-xs text-zinc-600 mt-1">
                                    Add employees manually or import a JSON file.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {input.team.map((emp, i) => (
                                    <EmployeeEditor
                                        key={emp.id + i}
                                        employee={emp}
                                        onChange={(updated) => updateEmployee(i, updated)}
                                        onRemove={() => removeEmployee(i)}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Results panel */}
                <div className="flex-1 overflow-y-auto p-5">
                    {!result && !error && !loading && (
                        <div className="flex flex-col items-center justify-center h-full text-center gap-3">
                            <div className="text-4xl">📅</div>
                            <p className="text-zinc-400 text-sm">
                                Configure your team on the left, then click Generate Schedule.
                            </p>
                            <p className="text-zinc-600 text-xs">
                                Or use Import JSON to load an existing payload.
                            </p>
                        </div>
                    )}

                    {loading && (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-zinc-400 text-sm animate-pulse">Solving schedule…</p>
                        </div>
                    )}

                    {error && (
                        <div className="rounded-lg border border-rose-800 bg-rose-950/40 px-4 py-3 text-sm text-rose-400">
                            {error}
                        </div>
                    )}

                    {result?.status === "infeasible" && (
                        <div className="rounded-lg border border-rose-800 bg-rose-950/40 px-4 py-4 space-y-3">
                            <p className="text-sm font-medium text-rose-400">No valid schedule found</p>
                            <ul className="list-disc pl-5 space-y-1">
                                {result.conflicts?.map((c, i) => (
                                    <li key={i} className="text-xs text-rose-500">{c}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {isSuccess && result.schedule && result.summary && (
                        <div className="space-y-4">
                            {/* Status bar */}
                            <div className="flex items-center gap-3">
                                {result.status === "ok" ? (
                                    <span className="rounded bg-emerald-900/50 px-2 py-1 text-xs font-medium text-emerald-400">
                                        Optimal
                                    </span>
                                ) : (
                                    <span className="rounded bg-amber-900/50 px-2 py-1 text-xs font-medium text-amber-400">
                                        Feasible
                                    </span>
                                )}
                                <span className="text-xs text-zinc-500">
                                    Penalty score:{" "}
                                    <span className="font-mono text-zinc-300">{result.penalty}</span>
                                </span>
                            </div>

                            {/* Tabs */}
                            <div className="flex border-b border-zinc-800">
                                {(["schedule", "summary"] as const).map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setTab(t)}
                                        className={`px-4 py-2 text-sm font-medium capitalize transition ${tab === t
                                                ? "border-b-2 border-zinc-200 text-zinc-100"
                                                : "text-zinc-500 hover:text-zinc-300"
                                            }`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>

                            {tab === "schedule" && <ScheduleTable schedule={result.schedule} />}
                            {tab === "summary" && <SummaryTable summary={result.summary} />}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
