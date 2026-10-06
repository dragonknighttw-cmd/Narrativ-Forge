import type { ButtonHTMLAttributes, HTMLAttributes, InputHTMLAttributes, PropsWithChildren } from "react";

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
