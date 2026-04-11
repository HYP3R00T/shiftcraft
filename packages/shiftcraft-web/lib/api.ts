import type { ScheduleInput, ScheduleResult, ScheduleSettings } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function generateSchedule(
    settings: ScheduleSettings,
    input: ScheduleInput,
): Promise<ScheduleResult> {
    const res = await fetch(`${API_BASE}/schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ settings, input }),
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        const detail = err.detail;
        throw new Error(
            typeof detail === "string" ? detail : JSON.stringify(detail)
        );
    }

    return res.json();
}
