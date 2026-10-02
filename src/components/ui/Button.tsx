import React from "react";
import { cn } from "../../lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg" | "icon";
  children?: React.ReactNode;
}

export function Button({ variant = "secondary", size = "md", className, children, ...props }: ButtonProps) {
  const variants: Record<string, string> = {
    primary: "bg-primary text-white hover:bg-primary-dim border-transparent",
    secondary: "bg-elevated text-text-main hover:border-primary/50 border-border",
    ghost: "bg-transparent text-text-sec hover:bg-elevated hover:text-text-main border-transparent",
    danger: "bg-error/15 text-error hover:bg-error/25 border-error/30",
  };
  const sizes: Record<string, string> = {
    sm: "px-2.5 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-5 py-2.5 text-sm",
    icon: "w-8 h-8 p-0",
  };
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 font-medium rounded-md border transition-colors disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary/50",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export function IconButton({ className, children, ...props }: IconButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center w-8 h-8 rounded-md text-text-sec hover:bg-elevated hover:text-text-main transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
