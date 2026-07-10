import { Link } from 'react-router'

import { Brand, Card, PrimaryButton } from '../components/ui'

export function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-canvas p-6">
      <Card className="w-full max-w-md p-8 text-center">
        <div className="flex justify-center"><Brand /></div>
        <span className="mt-8 block text-xs font-semibold uppercase tracking-[0.16em] text-lexis">404</span>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.03em]">Page not found</h1>
        <p className="mt-3 text-sm leading-6 text-ink-muted">The requested Lexis page does not exist.</p>
        <Link to="/app/workspace"><PrimaryButton className="mt-6 w-full">Return to Workspace</PrimaryButton></Link>
      </Card>
    </main>
  )
}
