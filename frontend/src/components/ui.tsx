import type { ButtonHTMLAttributes, HTMLAttributes, PropsWithChildren } from 'react'
import { Link } from 'react-router'

type Tone = 'default' | 'success' | 'warning' | 'danger'

const toneStyles: Record<Tone, string> = {
  default: 'border-line bg-surface-muted text-ink-muted',
  success: 'border-transparent bg-lexis-soft text-lexis',
  warning: 'border-transparent bg-warning-soft text-warning',
  danger: 'border-transparent bg-danger-soft text-danger',
}

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link className="inline-flex items-center gap-3 no-underline" to="/app/workspace">
      <span className="grid size-8 place-items-center rounded-lg bg-lexis text-sm font-semibold text-white md:size-9">L</span>
      <span className="leading-none">
        <strong className="block text-sm font-semibold text-ink">Lexis</strong>
        {!compact && <small className="mt-1 block text-[11px] text-ink-muted">Context learning workspace</small>}
      </span>
    </Link>
  )
}

export function StatusChip({ children, tone = 'success' }: PropsWithChildren<{ tone?: Tone }>) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs font-medium ${toneStyles[tone]}`}>
      <span className="size-1.5 rounded-full bg-current" aria-hidden="true" />
      {children}
    </span>
  )
}

export function Card({ className = '', ...props }: HTMLAttributes<HTMLElement>) {
  return <section className={`rounded-lg border border-line bg-white ${className}`} {...props} />
}

export function PrimaryButton({ className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`inline-flex min-h-11 items-center justify-center rounded-lg bg-lexis px-5 text-sm font-semibold text-white transition hover:bg-[#285f56] disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  )
}

export function SecondaryLink({ children, className = '', to }: PropsWithChildren<{ className?: string; to: string }>) {
  return (
    <Link className={`inline-flex min-h-9 items-center justify-center rounded-lg border border-line bg-white px-4 text-sm font-medium text-ink transition hover:bg-surface-muted ${className}`} to={to}>
      {children}
    </Link>
  )
}

export function WordChip({ active = false, children, onClick }: PropsWithChildren<{ active?: boolean; onClick?: () => void }>) {
  const className = active ? 'border-lexis bg-lexis-soft text-lexis' : 'border-line bg-surface-muted text-ink hover:border-lexis/40'
  return (
    <button className={`inline-flex h-7 items-center gap-1.5 rounded-md border px-2 text-[11px] font-medium transition md:h-[30px] md:gap-2 md:px-2.5 md:text-xs ${className}`} onClick={onClick} type="button">
      <span className="size-1.5 rounded-full bg-lexis" aria-hidden="true" />
      {children}
    </button>
  )
}

export function MetricTile({ label, note, value }: { label: string; note?: string; value: string }) {
  return (
    <div className="h-14 overflow-hidden rounded-lg bg-surface-muted p-2 md:h-[66px] md:overflow-hidden md:p-2">
      <span className="block text-[11px] text-ink-muted">{label}</span>
      <strong className="mt-1 block text-lg font-semibold leading-none text-ink">{value}</strong>
      {note && <small className="mt-0.5 hidden text-[10px] text-ink-muted/70 md:block">{note}</small>}
    </div>
  )
}

export function PageTitle({ children, subtitle }: PropsWithChildren<{ subtitle: string }>) {
  return (
    <div>
      <h1 className="text-[28px] font-semibold tracking-[-0.03em] text-ink">{children}</h1>
      <p className="mt-1 whitespace-nowrap text-[10px] leading-4 text-ink-muted md:whitespace-normal md:text-xs md:leading-4">{subtitle}</p>
    </div>
  )
}

export function SectionHeading({ children, subtitle }: PropsWithChildren<{ subtitle?: string }>) {
  return (
    <div>
      <h2 className="text-lg font-semibold tracking-[-0.015em] text-ink">{children}</h2>
      {subtitle && <p className="mt-1 text-[11px] leading-4 text-ink-muted md:text-[11px] md:leading-4">{subtitle}</p>}
    </div>
  )
}

export function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-surface-muted" aria-label={`完成 ${value}%`}>
      <div className="h-full rounded-full bg-lexis transition-[width]" style={{ width: `${value}%` }} />
    </div>
  )
}
