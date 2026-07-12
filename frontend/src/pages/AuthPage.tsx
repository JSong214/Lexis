import { LockKey, WarningCircle } from '@phosphor-icons/react'
import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { Brand, Card, PrimaryButton, StatusChip } from '../components/ui'
import { useLoginMutation, useRegisterMutation } from '../features/auth/auth'

interface AuthPageProps { mode: 'login' | 'register' }

export function AuthPage({ mode }: AuthPageProps) {
  const isLogin = mode === 'login'
  const navigate = useNavigate()
  const loginMutation = useLoginMutation()
  const registerMutation = useRegisterMutation()
  const mutation = isLogin ? loginMutation : registerMutation
  const [localError, setLocalError] = useState('')
  const requestError = mutation.error instanceof Error ? mutation.error.message : ''
  const error = localError || requestError

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const email = String(data.get('email') ?? '').trim()
    const password = String(data.get('password') ?? '')
    const confirmPassword = String(data.get('confirmPassword') ?? '')
    if (!email.includes('@') || password.length < 8) {
      setLocalError('Enter a valid email and a password with at least 8 characters.')
      return
    }
    if (!isLogin && password !== confirmPassword) {
      setLocalError('The passwords do not match.')
      return
    }

    setLocalError('')
    mutation.mutate(
      { email, password },
      { onSuccess: () => navigate('/app/workspace', { replace: true }) },
    )
  }

  return (
    <main className="min-h-screen bg-canvas px-6 py-7 md:px-10 lg:grid lg:place-items-center">
      <div className="mx-auto grid w-full max-w-[1156px] gap-8 lg:grid-cols-[1fr_440px] lg:items-center lg:gap-24">
        <section className="hidden lg:block">
          <Brand />
          <h1 className="mt-9 max-w-[640px] text-[42px] font-semibold leading-[1.14] tracking-[-0.035em] text-ink">
            {isLogin ? 'Welcome back to your learning workspace.' : 'Build a private workspace for context learning.'}
          </h1>
          <p className="mt-7 max-w-[560px] text-base leading-6 text-ink-muted">
            {isLogin ? 'Log in to restore your private session and continue with today’s Maimemo-backed context lesson workflow.' : 'Create an account, connect Maimemo, and turn your daily vocabulary into one focused lesson.'}
          </p>
          <div className="mt-8 grid h-[360px] content-between rounded-xl border border-line bg-white p-8" aria-hidden="true">
            <div>
              <StatusChip>Private by default</StatusChip>
              <p className="mt-6 max-w-sm text-2xl font-semibold leading-9">One account keeps each vocabulary profile, lesson, and answer separate.</p>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {['Vocabulary sync', 'Context lesson', 'Saved feedback'].map((label) => (
                <div className="rounded-lg bg-surface-muted p-4 text-xs font-medium text-ink-muted" key={label}>{label}</div>
              ))}
            </div>
          </div>
        </section>
        <div className="pt-1 lg:hidden"><Brand /></div>
        <Card className="mx-auto w-full max-w-[440px] p-6 shadow-[0_22px_60px_rgba(17,20,23,0.04)] sm:p-10">
          <StatusChip>{isLogin ? 'Session login' : 'Private workspace'}</StatusChip>
          <h1 className="mt-6 text-[26px] font-semibold tracking-[-0.025em]">{isLogin ? 'Log in to Lexis' : 'Create your Lexis account'}</h1>
          <p className="mt-4 text-sm leading-6 text-ink-muted">
            {isLogin ? 'Use your email and password to continue to your private lessons and feedback.' : 'Your vocabulary source and lesson history remain private to this account.'}
          </p>
          <div className="mt-5 flex items-center gap-3 rounded-lg bg-lexis-soft p-3 text-xs text-lexis">
            <LockKey aria-hidden="true" size={18} />
            {isLogin ? 'Your session is restored with an HttpOnly cookie.' : 'Your password is hashed before it is stored.'}
          </div>
          <form className="mt-6 grid gap-4" onSubmit={handleSubmit}>
            <label className="grid gap-2 text-xs font-semibold">Email
              <input autoComplete="email" className="h-11 rounded-lg border border-line bg-white px-3 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" disabled={mutation.isPending} name="email" placeholder="you@example.com" required type="email" />
            </label>
            <label className="grid gap-2 text-xs font-semibold">Password
              <input autoComplete={isLogin ? 'current-password' : 'new-password'} className="h-11 rounded-lg border border-line bg-white px-3 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" disabled={mutation.isPending} minLength={8} name="password" placeholder="At least 8 characters" required type="password" />
            </label>
            {!isLogin && (
              <label className="grid gap-2 text-xs font-semibold">Confirm password
                <input autoComplete="new-password" className="h-11 rounded-lg border border-line bg-white px-3 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" disabled={mutation.isPending} minLength={8} name="confirmPassword" placeholder="Repeat password" required type="password" />
              </label>
            )}
            {error && <p className="flex items-center gap-2 rounded-lg bg-danger-soft p-3 text-xs text-danger" role="alert"><WarningCircle aria-hidden="true" size={18} />{error}</p>}
            <PrimaryButton className="mt-1 w-full" disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Opening workspace…' : isLogin ? 'Log in' : 'Create account'}</PrimaryButton>
          </form>
          <p className="mt-5 text-xs text-ink-muted">
            {isLogin ? 'New to Lexis?' : 'Already have an account?'}{' '}
            <Link className="font-semibold text-lexis" to={isLogin ? '/register' : '/login'}>{isLogin ? 'Create account' : 'Log in'}</Link>
          </p>
        </Card>
      </div>
    </main>
  )
}
