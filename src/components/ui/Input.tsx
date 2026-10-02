import React from "react";
import { cn } from "../../lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function Input({ label, error, hint, className, ...props }: InputProps) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-text-sec">{label}</label>}
      <input
        className={cn(
          "w-full bg-surface border rounded-md px-3 py-2 text-sm text-text-main placeholder:text-text-muted focus:outline-none focus:ring-1 transition-colors",
          error ? "border-error focus:ring-error" : "border-border focus:border-primary focus:ring-primary",
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-error">{error}</p>}
      {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
    </div>
  );
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export function Textarea({ label, error, className, ...props }: TextareaProps) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-text-sec">{label}</label>}
      <textarea
        className={cn(
          "w-full bg-surface border rounded-md px-3 py-2 text-sm text-text-main placeholder:text-text-muted focus:outline-none focus:ring-1 transition-colors resize-y",
          error ? "border-error focus:ring-error" : "border-border focus:border-primary focus:ring-primary",
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-error">{error}</p>}
    </div>
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
}

export function Select({ label, options, className, ...props }: SelectProps) {
  return (
    <div className="space-y-1.5">
      {label && <label className="block text-sm font-medium text-text-sec">{label}</label>}
      <select
        className={cn(
          "w-full bg-surface border border-border rounded-md px-3 py-2 text-sm text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors cursor-pointer",
          className
        )}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-surface text-text-main">
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
