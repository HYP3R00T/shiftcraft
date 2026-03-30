"use client";

import { useRef, useState } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { ScheduleInput } from "@/lib/types";

export function JsonImport({ onImport }: { onImport: (input: ScheduleInput) => void }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  function close() {
    setOpen(false);
    setError(null);
  }

  function handleParse() {
    try {
      onImport(JSON.parse(text) as ScheduleInput);
      setText("");
      close();
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
    e.target.value = "";
  }

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        Import JSON
      </Button>

      {open && createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/60" onClick={close} />

          {/* Modal */}
          <div className="relative z-10 w-full max-w-2xl mx-4 bg-background border border-border shadow-2xl flex flex-col max-h-[90vh]">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border px-5 py-4 shrink-0">
              <h2 className="text-sm font-semibold">Import JSON</h2>
              <button onClick={close} className="text-muted-foreground hover:text-foreground transition">
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Body */}
            <div className="p-5 space-y-4 flex flex-col flex-1 min-h-0">
              <div className="flex items-center gap-3 shrink-0">
                <Button variant="outline" size="sm" onClick={() => fileRef.current?.click()}>
                  Upload file
                </Button>
                <span className="text-xs text-muted-foreground">or paste JSON below</span>
                <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={handleFile} />
              </div>

              <Textarea
                value={text}
                onChange={(e) => { setText(e.target.value); setError(null); }}
                placeholder='{ "period": { "start": "...", "end": "..." }, ... }'
                spellCheck={false}
                className="font-mono text-xs resize-none flex-1 min-h-0"
              />

              {error && <p className="text-xs text-destructive shrink-0">{error}</p>}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-2 border-t border-border px-5 py-4 shrink-0">
              <Button variant="outline" onClick={close}>Cancel</Button>
              <Button onClick={handleParse} disabled={!text.trim()}>Import</Button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
