"use client";

import { useRef, useState } from "react";
import type { ScheduleInput } from "@/lib/types";
import { Btn } from "./ui";

export function JsonImport({ onImport }: { onImport: (input: ScheduleInput) => void }) {
    const [open, setOpen] = useState(false);
    const [text, setText] = useState("");
    const [error, setError] = useState<string | null>(null);
    const fileRef = useRef<HTMLInputElement>(null);

    function handleParse() {
        try {
            const parsed = JSON.parse(text);
            onImport(parsed as ScheduleInput);
            setOpen(false);
            setText("");
            setError(null);
        } catch {
            setError("Invalid JSON — check the format and try again.");
        }
    }

    function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => setText(ev.target?.result as string);
        reader.readAsText(file);
    }

    if (!open) {
        return (
            <Btn variant="ghost" onClick={() => setOpen(true)}>
                Import JSON
            </Btn>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
            <div className="w-full max-w-2xl rounded-xl border border-zinc-700 bg-zinc-900 shadow-2xl">
                <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4">
                    <h2 className="text-sm font-semibold text-zinc-100">Import JSON</h2>
                    <button
                        onClick={() => { setOpen(false); setError(null); }}
                        className="text-zinc-500 hover:text-zinc-200 transition text-xl leading-none"
                    >
                        ×
                    </button>
                </div>

                <div className="p-5 space-y-4">
                    <div className="flex items-center gap-3">
                        <Btn variant="ghost" onClick={() => fileRef.current?.click()}>
                            Upload file
                        </Btn>
                        <span className="text-xs text-zinc-500">or paste JSON below</span>
                        <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={handleFile} />
                    </div>

                    <textarea
                        value={text}
                        onChange={(e) => { setText(e.target.value); setError(null); }}
                        placeholder='{ "period": { "start": "...", "end": "..." }, ... }'
                        spellCheck={false}
                        rows={16}
                        className="w-full rounded-md border border-zinc-700 bg-zinc-950 p-3 font-mono text-xs text-zinc-200 placeholder-zinc-600 outline-none focus:border-zinc-500 resize-none"
                    />

                    {error && (
                        <p className="text-xs text-rose-400">{error}</p>
                    )}

                    <div className="flex justify-end gap-2">
                        <Btn variant="ghost" onClick={() => { setOpen(false); setError(null); }}>
                            Cancel
                        </Btn>
                        <Btn onClick={handleParse} disabled={!text.trim()}>
                            Import
                        </Btn>
                    </div>
                </div>
            </div>
        </div>
    );
}
