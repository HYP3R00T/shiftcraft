"use client";

import { useState } from "react";
import type { Employee, LeaveRequest } from "@/lib/types";
import { Btn, Field, Input, Label, Select } from "./ui";

const LEAVE_TYPES = ["annual", "comp_off", "week_off"] as const;
const SHIFT_TYPES = ["morning", "afternoon", "night", "regular", "week_off"] as const;

function LeaveRow({
    req,
    onChange,
    onRemove,
}: {
    req: LeaveRequest;
    onChange: (r: LeaveRequest) => void;
    onRemove: () => void;
}) {
    return (
        <div className="flex gap-2 items-center">
            <Input
                type="date"
                value={req.date}
                onChange={(e) => onChange({ ...req, date: e.target.value })}
                className="flex-1"
            />
            <Select
                value={req.leave_type ?? ""}
                onChange={(e) =>
                    onChange({
                        ...req,
                        leave_type: (e.target.value || null) as LeaveRequest["leave_type"],
                    })
                }
                className="flex-1"
            >
                <option value="">preference</option>
                {LEAVE_TYPES.map((t) => (
                    <option key={t} value={t}>
                        {t}
                    </option>
                ))}
            </Select>
            <button
                onClick={onRemove}
                className="text-zinc-500 hover:text-rose-400 transition text-lg leading-none"
                aria-label="Remove"
            >
                ×
            </button>
        </div>
    );
}

export function EmployeeEditor({
    employee,
    onChange,
    onRemove,
}: {
    employee: Employee;
    onChange: (e: Employee) => void;
    onRemove: () => void;
}) {
    const [open, setOpen] = useState(true);

    function set<K extends keyof Employee>(key: K, value: Employee[K]) {
        onChange({ ...employee, [key]: value });
    }

    function setHistory(key: keyof Employee["history"]["last_month_shift_counts"], value: number) {
        onChange({
            ...employee,
            history: {
                ...employee.history,
                last_month_shift_counts: {
                    ...employee.history.last_month_shift_counts,
                    [key]: value,
                },
            },
        });
    }

    function addLeave() {
        set("leave_requests", [
            ...employee.leave_requests,
            { date: "", leave_type: null },
        ]);
    }

    function updateLeave(i: number, r: LeaveRequest) {
        const updated = [...employee.leave_requests];
        updated[i] = r;
        set("leave_requests", updated);
    }

    function removeLeave(i: number) {
        set("leave_requests", employee.leave_requests.filter((_, idx) => idx !== i));
    }

    const histKeys = ["morning", "afternoon", "night", "regular", "week_off", "leave"] as const;

    return (
        <div className="rounded-lg border border-zinc-700 bg-zinc-900 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-zinc-800/60">
                <button
                    onClick={() => setOpen((o) => !o)}
                    className="flex items-center gap-2 text-sm font-medium text-zinc-200 hover:text-white transition"
                >
                    <span className="text-zinc-500">{open ? "▾" : "▸"}</span>
                    {employee.name || <span className="text-zinc-500 italic">Unnamed employee</span>}
                    {employee.is_senior && (
                        <span className="rounded bg-amber-900/50 px-1.5 py-0.5 text-xs text-amber-400">
                            Senior
                        </span>
                    )}
                </button>
                <Btn variant="danger" onClick={onRemove} className="text-xs py-1 px-2">
                    Remove
                </Btn>
            </div>

            {open && (
                <div className="p-4 space-y-5">
                    {/* Identity */}
                    <div className="grid grid-cols-2 gap-3">
                        <Field label="ID">
                            <Input value={employee.id} onChange={(e) => set("id", e.target.value)} />
                        </Field>
                        <Field label="Name">
                            <Input
                                value={employee.name}
                                placeholder="Full name"
                                onChange={(e) => set("name", e.target.value)}
                            />
                        </Field>
                        <Field label="City">
                            <Input
                                value={employee.city}
                                placeholder="e.g. Hyderabad"
                                onChange={(e) => set("city", e.target.value)}
                            />
                        </Field>
                        <Field label="Seniority">
                            <Select
                                value={employee.is_senior ? "senior" : "junior"}
                                onChange={(e) => set("is_senior", e.target.value === "senior")}
                            >
                                <option value="junior">Junior</option>
                                <option value="senior">Senior</option>
                            </Select>
                        </Field>
                        <Field label="Comp-off balance">
                            <Input
                                type="number"
                                min={0}
                                value={employee.comp_off_balance}
                                onChange={(e) => set("comp_off_balance", Number(e.target.value))}
                            />
                        </Field>
                    </div>

                    {/* Leave requests */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <Label>Leave requests</Label>
                            <Btn variant="ghost" onClick={addLeave} className="text-xs py-1 px-2">
                                + Add
                            </Btn>
                        </div>
                        {employee.leave_requests.length === 0 ? (
                            <p className="text-xs text-zinc-600 italic">No leave requests</p>
                        ) : (
                            <div className="space-y-2">
                                {employee.leave_requests.map((r, i) => (
                                    <LeaveRow
                                        key={i}
                                        req={r}
                                        onChange={(updated) => updateLeave(i, updated)}
                                        onRemove={() => removeLeave(i)}
                                    />
                                ))}
                            </div>
                        )}
                    </div>

                    {/* History */}
                    <div>
                        <Label>Last month shift counts</Label>
                        <div className="grid grid-cols-3 gap-2 mt-1">
                            {histKeys.map((k) => (
                                <div key={k}>
                                    <p className="text-xs text-zinc-500 mb-1 capitalize">{k.replace("_", " ")}</p>
                                    <Input
                                        type="number"
                                        min={0}
                                        value={employee.history.last_month_shift_counts[k]}
                                        onChange={(e) => setHistory(k, Number(e.target.value))}
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
