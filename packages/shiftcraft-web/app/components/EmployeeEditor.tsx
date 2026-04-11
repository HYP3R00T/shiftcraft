"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Trash2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { Employee } from "@/lib/types";

export function EmployeeEditor({ employee, onChange, onRemove }: {
  employee: Employee;
  onChange: (e: Employee) => void;
  onRemove: () => void;
}) {
  const [open, setOpen] = useState(true);

  function set<K extends keyof Employee>(key: K, value: Employee[K]) {
    onChange({ ...employee, [key]: value });
  }

  function setAttribute(key: string, value: string) {
    onChange({ ...employee, attributes: { ...employee.attributes, [key]: value } });
  }

  function setBalance(key: string, value: number) {
    onChange({ ...employee, balances: { ...employee.balances, [key]: value } });
  }

  function setHistoryCount(state: string, value: number) {
    onChange({
      ...employee,
      history: {
        ...employee.history,
        last_month_shift_counts: {
          ...employee.history.last_month_shift_counts,
          [state]: value,
        },
      },
    });
  }

  const histStates = ["morning", "afternoon", "night", "regular", "week_off", "annual", "comp_off"];

  return (
    <Card>
      <CardHeader className="py-3 px-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setOpen((o) => !o)}
            className="flex items-center gap-2 text-sm font-medium hover:text-foreground transition-colors text-left"
          >
            {open
              ? <ChevronDown className="h-4 w-4 text-muted-foreground" />
              : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
            {employee.name || <span className="text-muted-foreground italic">Unnamed employee</span>}
          </button>
          <Button variant="ghost" size="icon" onClick={onRemove} className="text-muted-foreground hover:text-destructive">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      {open && (
        <CardContent className="pt-0 space-y-5">
          {/* Identity */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">ID</Label>
              <Input value={employee.id} onChange={(e) => set("id", e.target.value)} className="text-xs" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Name</Label>
              <Input value={employee.name} placeholder="Full name" onChange={(e) => set("name", e.target.value)} className="text-xs" />
            </div>
          </div>

          {/* Attributes */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs">Attributes</Label>
              <Button variant="outline" size="sm" className="h-7 text-xs gap-1"
                onClick={() => setAttribute("", "")}>
                <Plus className="h-3 w-3" /> Add
              </Button>
            </div>
            {Object.entries(employee.attributes).length === 0
              ? <p className="text-xs text-muted-foreground italic">No attributes (e.g. city, role)</p>
              : <div className="space-y-2">
                {Object.entries(employee.attributes).map(([k, v], i) => (
                  <div key={i} className="flex gap-2">
                    <Input
                      value={k}
                      placeholder="key"
                      className="text-xs flex-1"
                      onChange={(e) => {
                        const attrs = { ...employee.attributes };
                        delete attrs[k];
                        attrs[e.target.value] = v;
                        set("attributes", attrs);
                      }}
                    />
                    <Input
                      value={v}
                      placeholder="value"
                      className="text-xs flex-1"
                      onChange={(e) => setAttribute(k, e.target.value)}
                    />
                    <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive shrink-0"
                      onClick={() => {
                        const attrs = { ...employee.attributes };
                        delete attrs[k];
                        set("attributes", attrs);
                      }}>
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            }
          </div>

          {/* Balances */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs">Balances</Label>
              <Button variant="outline" size="sm" className="h-7 text-xs gap-1"
                onClick={() => setBalance("comp_off", 0)}>
                <Plus className="h-3 w-3" /> Add
              </Button>
            </div>
            {Object.entries(employee.balances).length === 0
              ? <p className="text-xs text-muted-foreground italic">No balances (e.g. comp_off: 2)</p>
              : <div className="grid grid-cols-2 gap-2">
                {Object.entries(employee.balances).map(([k, v]) => (
                  <div key={k} className="space-y-1">
                    <p className="text-xs text-muted-foreground capitalize">{k.replace("_", " ")}</p>
                    <Input type="number" min={0} value={v}
                      onChange={(e) => setBalance(k, Number(e.target.value))}
                      className="text-xs" />
                  </div>
                ))}
              </div>
            }
          </div>

          {/* Last month shift counts */}
          <div className="space-y-2">
            <Label className="text-xs">Last month shift counts</Label>
            <div className="grid grid-cols-3 gap-2">
              {histStates.map((s) => (
                <div key={s} className="space-y-1">
                  <p className="text-xs text-muted-foreground capitalize">{s.replace("_", " ")}</p>
                  <Input
                    type="number" min={0}
                    value={employee.history.last_month_shift_counts[s] ?? 0}
                    onChange={(e) => setHistoryCount(s, Number(e.target.value))}
                    className="text-xs"
                  />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
