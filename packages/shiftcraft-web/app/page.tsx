"use client";

import { useState } from "react";
import { generateSchedule } from "@/lib/api";
import type { ScheduleResult } from "@/lib/types";
import { ScheduleTable } from "./components/ScheduleTable";
import { SummaryTable } from "./components/SummaryTable";

const EXAMPLE_INPUT = {
    period: { start: "2026-04-01", end: "2026-04-30" },
    team: [
        {
            id: "E001", name: "Alice", is_senior: true, city: "Hyderabad",
            comp_off_balance: 0,
            previous_week_days: { "2026-03-30": "afternoon", "2026-03-31": "week_off" },
            leave_requests: [{ date: "2026-04-05", leave_type: null }],
            history: {
                last_month_shift_counts: { morning: 8, afternoon: 5, night: 6, regular: 2, week_off: 9, leave: 1 },
                comp_off: { remaining_count: 0, records: [] },
            },
        },
        {
            id: "E002", name: "Bob", is_senior: true, city: "Bengaluru",
            comp_off_balance: 0,
            previous_week_days: { "2026-03-30": "morning", "2026-03-31": "regular" },
            leave_requests: [],
            history: {
                last_month_shift_counts: { morning: 6, afternoon: 7, night: 7, regular: 3, week_off: 8, leave: 0 },
                comp_off: { remaining_count: 0, records: [] },
            },
        },
        {
            id: "E003", name: "Carol", is_senior: false, city: "Hyderabad",
            comp_off_balance: 0,
            previous_week_days: { "2026-03-30": "night", "2026-03-31": "night" },
            leave_requests: [],
            history: {
                last_month_shift_counts: { morning: 3, afternoon: 9, night: 6, regular: 2, week_off: 8, leave: 1 },
                comp_off: { remaining_count: 0, records: [] },
            },
        },
    ],
    coverage: {
        by_day_of_week: Object.fromEntries(
            ["monday", "tuesday", "wednesday", "thursday", "friday"].map((d) => [
                d,
                {
                    morning: { min: 1, target: 1, max: 1 },
                    afternoon: { min: 1, target: 1, max: 1 },
                    night: { min: 1, target: 1, max: 1 },
                    regular: { min: 0, target: 0, max: 1 },
                },
            ]).concat(
                ["saturday", "sunday"].map((d) => [
                    d,
                    {
                        morning: { min: 1, target: 1, max: 1 },
                        afternoon: { min: 1, target: 1, max: 1 },
                        night: { min: 1, target: 1, max: 1 },
                        regular: { min: 0, target: 0, max: 0 },
                    },
                ])
            )
        ),
        by_date_range: [],
    },
    holidays: [],
};

export default function Home() {
    const [input, setInput] = useState(JSON.stringify(EXAMPLE_INPUT, null, 2));
    const [result, setResult] = useState<ScheduleResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState<"schedule" | "summary">("schedule");

    async function handleGenerate() {
        setError(null);
        setResult(null);
        setLoading(true);
        try {
            const payload = JSON.parse(input);
            const res = await generateSchedule(payload);
            setResult(res);
            setTab("schedule");
        } catch (e) {
            setError(e instanceof Error ? e.message : "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    const isSuccess = result && (result.status === "ok" || result.status === "feasible");

    return (
        <div className="min-h-screen bg-zinc-50 font-sans">
            {/* Header */}
            <header className="border-b border-zinc-200 bg-white px-6 py-4">
                <div className="mx-auto max-w-7xl flex items-center justify-between">
                    <div>
                        <h1 className="text-lg font-semibold text-zinc-900">Shiftcraft</h1>
                        <p className="text-xs text-zinc-500">Constraint-driven workforce scheduler</p>
                    </div>
                    {result && isSuccess && (
                        <span className="text-xs text-zinc-500">
                            Penalty score: <span className="font-mono font-medium text-zinc-700">{result.penalty}</span>
                            {result.status === "feasible" && (
                                <span className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-amber-700">feasible</span>
                            )}
                            {result.status === "ok" && (
                                <span className="ml-2 rounded bg-green-100 px-1.5 py-0.5 text-green-700">optimal</span>
                            )}
                        </span>
                    )}
                </div>
            </header>

            <main className="mx-auto max-w-7xl px-6 py-8 space-y-6">
                {/* Input panel */}
                <div className="rounded-lg border border-zinc-200 bg-white overflow-hidden">
                    <div className="flex items-center justify-between border-b border-zinc-100 px-4 py-3">
                        <span className="text-sm font-medium text-zinc-700">Input JSON</span>
                        <button
                            onClick={handleGenerate}
                            disabled={loading}
                            className="rounded-md bg-zinc-900 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-zinc-700 disabled:opacity-50"
                        >
                            {loading ? "Generating…" : "Generate Schedule"}
                        </button>
                    </div>
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        spellCheck={false}
                        className="w-full resize-none bg-zinc-950 p-4 font-mono text-xs text-zinc-200 outline-none"
                        rows={20}
                    />
                </div>

                {/* Error */}
                {error && (
                    <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                        {error}
                    </div>
                )}

                {/* Infeasible */}
                {result && result.status === "infeasible" && (
                    <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 space-y-2">
                        <p className="text-sm font-medium text-rose-700">No valid schedule found</p>
                        <ul className="list-disc pl-5 space-y-1">
                            {result.conflicts?.map((c, i) => (
                                <li key={i} className="text-xs text-rose-600">{c}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Results */}
                {isSuccess && result.schedule && result.summary && (
                    <div className="rounded-lg border border-zinc-200 bg-white overflow-hidden">
                        {/* Tabs */}
                        <div className="flex border-b border-zinc-100">
                            {(["schedule", "summary"] as const).map((t) => (
                                <button
                                    key={t}
                                    onClick={() => setTab(t)}
                                    className={`px-5 py-3 text-sm font-medium capitalize transition ${tab === t
                                            ? "border-b-2 border-zinc-900 text-zinc-900"
                                            : "text-zinc-500 hover:text-zinc-700"
                                        }`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                        <div className="p-4">
                            {tab === "schedule" && <ScheduleTable schedule={result.schedule} />}
                            {tab === "summary" && <SummaryTable summary={result.summary} />}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
