"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Trash2, Plus } from "lucide-react";
import { DatePicker } from "@/components/date-picker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Employee, LeaveRequest } from "@/lib/types";

const LEAVE_TYPES = ["annual", "comp_off", "week_off"] as const;

function LeaveRow({ req, onChange, onRemove }: {
    req: LeaveRequest;
    onChange: (r: LeaveRequest) => void;
    onRemove: () => void;
}) {
    return (
        <div className="flex gap-2 items-center">
            <DatePicker
                value={req.date}
                onChange={(v) => onChange({ ...req, date: v })}
                className="flex-1"
            />
            <Select
                value={req.leave_type ?? "preference"}
                onValueChange={(v) => onChange({ ...req, leave_type: (v === "preference" ? null : v) as LeaveRequest["leave_type"] })}
            >
                <SelectTrigger className="flex-1 text-xs">
                    <SelectValue />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="preference">preference</SelectItem>
                    {LEAVE_TYPES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
            </Select>
            <Button variant="ghost" size="icon" onClick={onRemove} className="text-muted-foreground hover:text-destructive shrink-0">
                <Trash2 className="h-3.5 w-3.5" />
            </Button>
        </div>
    );
}

export function EmployeeEditor({ employee, onChange, onRemove }: {
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
                last_month_shift_counts: { ...employee.history.last_month_shift_counts, [key]: value },
            },
        });
    }

    const histKeys = ["morning", "afternoon", "night", "regular", "week_off", "leave"] as const;

    return (
        <Card>
            <CardHeader className="py-3 px-4">
                <div className="flex items-center justify-between">
                    <button
                        onClick={() => setOpen((o) => !o)}
                        className="flex items-center gap-2 text-sm font-medium hover:text-foreground transition-colors text-left"
                    >
                        {open ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                        {employee.name || <span className="text-muted-foreground italic">Unnamed employee</span>}
                        {employee.is_senior && <Badge variant="secondary" className="text-xs">Senior</Badge>}
                    </button>
                    <Button variant="ghost" size="icon" onClick={onRemove} className="text-muted-foreground hover:text-destructive">
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </CardHeader>

            {open && (
                <CardContent className="pt-0 space-y-5">
                    <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-1">
                            <Label className="text-xs">ID</Label>
                            <Input value={employee.id} onChange={(e) => set("id", e.target.value)} className="text-xs" />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">Name</Label>
                            <Input value={employee.name} placeholder="Full name" onChange={(e) => set("name", e.target.value)} className="text-xs" />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">City</Label>
                            <Input value={employee.city} placeholder="e.g. Hyderabad" onChange={(e) => set("city", e.target.value)} className="text-xs" />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">Seniority</Label>
                            <Select value={employee.is_senior ? "senior" : "junior"} onValueChange={(v) => set("is_senior", v === "senior")}>
                                <SelectTrigger className="text-xs"><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="junior">Junior</SelectItem>
                                    <SelectItem value="senior">Senior</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">Comp-off balance</Label>
                            <Input type="number" min={0} value={employee.comp_off_balance} onChange={(e) => set("comp_off_balance", Number(e.target.value))} className="text-xs" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <Label className="text-xs">Leave requests</Label>
                            <Button variant="outline" size="sm" className="h-7 text-xs gap-1"
                                onClick={() => set("leave_requests", [...employee.leave_requests, { date: "", leave_type: null }])}>
                                <Plus className="h-3 w-3" /> Add
                            </Button>
                        </div>
                        {employee.leave_requests.length === 0
                            ? <p className="text-xs text-muted-foreground italic">No leave requests</p>
                            : <div className="space-y-2">
                                {employee.leave_requests.map((r, i) => (
                                    <LeaveRow key={i} req={r}
                                        onChange={(u) => { const l = [...employee.leave_requests]; l[i] = u; set("leave_requests", l); }}
                                        onRemove={() => set("leave_requests", employee.leave_requests.filter((_, idx) => idx !== i))}
                                    />
                                ))}
                            </div>
                        }
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs">Last month shift counts</Label>
                        <div className="grid grid-cols-3 gap-2">
                            {histKeys.map((k) => (
                                <div key={k} className="space-y-1">
                                    <p className="text-xs text-muted-foreground capitalize">{k.replace("_", " ")}</p>
                                    <Input type="number" min={0} value={employee.history.last_month_shift_counts[k]}
                                        onChange={(e) => setHistory(k, Number(e.target.value))} className="text-xs" />
                                </div>
                            ))}
                        </div>
                    </div>
                </CardContent>
            )}
        </Card>
    );
}
