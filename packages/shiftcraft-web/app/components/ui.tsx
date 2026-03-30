"use client";

import type { InputHTMLAttributes, SelectHTMLAttributes } from "react";

const inputBase =
    "w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
    return <input {...props} className={`${inputBase} ${props.className ?? ""}`} />;
}

export function Select({
    children,
    ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { children: React.ReactNode }) {
    return (
        <select {...props} className={`${inputBase} ${props.className ?? ""}`}>
            {children}
        </select>
    );
}

export function Label({ children }: { children: React.ReactNode }) {
    return <label className="block text-xs font-medium text-zinc-400 mb-1">{children}</label>;
}

export function Field({
    label,
    children,
}: {
    label: string;
    children: React.ReactNode;
}) {
    return (
        <div>
            <Label>{label}</Label>
            {children}
        </div>
    );
}

export function SectionTitle({ children }: { children: React.ReactNode }) {
    return (
        <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-3">
            {children}
        </h3>
    );
}

export function Btn({
    children,
    variant = "default",
    ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: "default" | "ghost" | "danger";
}) {
    const styles = {
        default: "bg-zinc-100 text-zinc-900 hover:bg-white",
        ghost: "bg-zinc-800 text-zinc-300 hover:bg-zinc-700 border border-zinc-700",
        danger: "bg-rose-900/40 text-rose-400 hover:bg-rose-900/60 border border-rose-800",
    };
    return (
        <button
            {...props}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition disabled:opacity-50 ${styles[variant]} ${props.className ?? ""}`}
        >
            {children}
        </button>
    );
}
