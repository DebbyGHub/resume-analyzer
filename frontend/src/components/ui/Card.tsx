import { type HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  accent?: boolean;
}

export function Card({
  accent = false,
  className = "",
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={
        "bg-surface-card rounded-xl card-glow " +
        (accent ? "border border-accent/30 " : "") +
        className
      }
      {...rest}
    >
      {children}
    </div>
  );
}
