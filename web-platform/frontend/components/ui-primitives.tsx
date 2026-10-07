import type { ButtonHTMLAttributes, HTMLAttributes, InputHTMLAttributes, PropsWithChildren, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

type Tone = "neutral" | "success" | "warning" | "danger";
type Variant = "secondary" | "primary" | "danger";

export function Stack({ children, ...props }: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return <div className="ds-stack" {...props}>{children}</div>;
}

export function Row({ children, ...props }: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return <div className="ds-row" {...props}>{children}</div>;
}

export function Card({ children, ...props }: PropsWithChildren<HTMLAttributes<HTMLElement>>) {
  return <section className="ds-card" {...props}>{children}</section>;
}

export function Button({
  variant = "secondary",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return <button className="ds-button" data-variant={variant} {...props}>{children}</button>;
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className="ds-input" {...props} />;
}

export function Badge({ tone = "neutral", children }: PropsWithChildren<{ tone?: Tone }>) {
  return <span className="ds-badge" data-tone={tone}>{children}</span>;
}

export function Alert({
  tone = "neutral",
  children,
}: PropsWithChildren<{ tone?: Tone }>) {
  return <div className="ds-alert" data-tone={tone} role={tone === "danger" ? "alert" : undefined}>{children}</div>;
}


export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className="ds-select" {...props} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className="ds-textarea" {...props} />;
}

export function Checkbox({ label, ...props }: InputHTMLAttributes<HTMLInputElement> & { label?: string }) {
  return (
    <label className="ds-row">
      <input className="ds-checkbox" {...props} type="checkbox" />
      {label ? <span>{label}</span> : null}
    </label>
  );
}

export function Switch({ label, ...props }: InputHTMLAttributes<HTMLInputElement> & { label?: string }) {
  return (
    <label className="ds-switch">
      <input role="switch" {...props} type="checkbox" />
      {label ? <span>{label}</span> : null}
    </label>
  );
}

export function Spinner({ label = "Loading" }: { label?: string }) {
  return <span className="ds-spinner" role="status" aria-label={label} />;
}

export function Progress({ value, label = "Progress" }: { value: number; label?: string }) {
  const bounded = Math.max(0, Math.min(100, value));
  return (
    <div className="ds-progress" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={bounded}>
      <span style={{ width: `${bounded}%` }} />
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`ds-skeleton ${className}`} aria-hidden="true" />;
}

export function EmptyState({ title, children }: PropsWithChildren<{ title: string }>) {
  return <section className="ds-empty" aria-label={title}><strong>{title}</strong>{children ? <div>{children}</div> : null}</section>;
}

export function VisuallyHidden({ children }: PropsWithChildren) {
  return <span className="ds-visually-hidden">{children}</span>;
}
