import { NavLink, Outlet, useLocation } from 'react-router'

import { Brand, StatusChip } from '../components/ui'
import { useHealthQuery } from '../features/system/health'

const navigation = [
  { label: 'Workspace', to: '/app/workspace' },
  { label: 'History', to: '/app/history' },
  { label: 'Settings', to: '/app/settings/connection' },
]

export function AppShell() {
  const healthQuery = useHealthQuery()
  const location = useLocation()
  const isWorkspace = location.pathname === '/app/workspace'
  const healthLabel = healthQuery.isPending ? 'Connecting' : healthQuery.isError ? 'API offline' : 'API connected'

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <header className="relative mx-auto flex w-full max-w-7xl items-center justify-between px-6 pt-6 md:px-8">
        <Brand />
        {isWorkspace ? (
          <section className="absolute right-8 top-6 hidden h-[82px] w-[342px] rounded-lg border border-line bg-white p-4 lg:block">
            <div className="flex items-start justify-between gap-3">
              <div><h2 className="text-base font-semibold">Maimemo connected</h2><p className="mt-3 text-xs text-ink-muted">Latest sync 09:12. Snapshot ready for generation.</p></div>
              <StatusChip tone={healthQuery.isError ? 'danger' : 'success'}>{healthQuery.isError ? 'Offline' : 'Ready'}</StatusChip>
            </div>
          </section>
        ) : (
          <div className="hidden md:block"><StatusChip tone={healthQuery.isError ? 'danger' : 'success'}>{healthLabel}</StatusChip></div>
        )}
      </header>
      <main className="mx-auto w-full max-w-7xl px-6 pb-28 pt-0 md:px-8 md:pt-4"><Outlet /></main>
      <nav aria-label="Primary navigation" className="fixed inset-x-6 bottom-3 z-50 mx-auto grid max-w-[480px] grid-cols-3 rounded-xl border border-line bg-white/95 p-2 shadow-[0_12px_36px_rgba(17,20,23,0.08)] backdrop-blur md:bottom-5">
        {navigation.map((item) => (
          <NavLink className={({ isActive }) => `flex h-11 flex-col items-center justify-center gap-1 rounded-lg text-[11px] font-medium transition ${isActive ? 'bg-lexis-soft text-lexis' : 'text-ink-muted hover:bg-surface-muted'}`} key={item.to} to={item.to}>
            {({ isActive }) => <><span className={`size-1.5 rounded-full ${isActive ? 'bg-lexis' : 'bg-[#a9b4ae]'}`} aria-hidden="true" />{item.label}</>}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
