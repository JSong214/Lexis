import type { PropsWithChildren } from 'react'
import { Navigate, useLocation } from 'react-router'

import { Brand, Card, PrimaryButton, StatusChip } from '../../components/ui'
import { ApiError } from '../../lib/api-client'
import { useCurrentUserQuery } from './auth'

function SessionStatus({
  error = false,
  onRetry,
}: {
  error?: boolean
  onRetry?: () => void
}) {
  return (
    <main className="grid min-h-screen place-items-center bg-canvas px-6">
      <Card className="w-full max-w-md p-8 text-center">
        <Brand />
        <div className="mt-8">
          <StatusChip tone={error ? 'danger' : 'default'}>
            {error ? 'Session unavailable' : 'Restoring session'}
          </StatusChip>
        </div>
        <h1 className="mt-5 text-xl font-semibold">
          {error ? 'Lexis API could not restore your session.' : 'Opening your private workspace…'}
        </h1>
        <p className="mt-3 text-sm leading-6 text-ink-muted">
          {error ? 'Check that the backend is running, then try again.' : 'Your sign-in state is being verified.'}
        </p>
        {onRetry && <PrimaryButton className="mt-6" onClick={onRetry}>Try again</PrimaryButton>}
      </Card>
    </main>
  )
}

export function ProtectedRoute({ children }: PropsWithChildren) {
  const location = useLocation()
  const currentUser = useCurrentUserQuery()

  if (currentUser.isPending) {
    return <SessionStatus />
  }

  if (currentUser.isError) {
    if (currentUser.error instanceof ApiError && currentUser.error.status === 401) {
      return <Navigate replace state={{ from: location.pathname }} to="/login" />
    }
    return <SessionStatus error onRetry={() => currentUser.refetch()} />
  }

  return children
}

export function GuestOnlyRoute({ children }: PropsWithChildren) {
  const currentUser = useCurrentUserQuery()

  if (currentUser.isPending) {
    return <SessionStatus />
  }

  if (currentUser.isSuccess) {
    return <Navigate replace to="/app/workspace" />
  }

  return children
}
