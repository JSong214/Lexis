import { LockKey, WarningCircle } from '@phosphor-icons/react'
import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { Brand, Card, PrimaryButton, StatusChip } from '../components/ui'

interface AuthPageProps { mode: 'login' | 'register' }

export function AuthPage({ mode }: AuthPageProps) {
  const isLogin = mode === 'login'
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const email = String(data.get('email') ?? '')
    const password = String(data.get('password') ?? '')
    const confirmPassword = String(data.get('confirmPassword') ?? '')
    if (!email.includes('@') || password.length < 6 || (!isLogin && password !== confirmPassword)) {
      setError(isLogin ? 'Invalid email or password. Try again.' : 'Check your email and matching passwords.')
      return
    }
    setError('')
    setPending(true)
    window.setTimeout(() => navigate('/app/workspace'), 450)
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
          <div className="mt-8 h-[360px] rounded-xl border border-line bg-white" aria-hidden="true" />
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
            {isLogin ? 'Log in to continue to Workspace.' : 'Credentials are sent only to the Lexis API.'}
          </div>
          <form className="mt-6 grid gap-4" onSubmit={handleSubmit}>
            <label className="grid gap-2 text-xs font-semibold">Email
              <input className="h-11 rounded-lg border border-line bg-white px-3 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" name="email" placeholder="you@example.com" type="email" />
            </label>
            <label className="grid gap-2 text-xs font-semibold">Password
              <input className="h-11 rounded-lg border border-line bg-white px-3 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" name="password" placeholder="Enter password" type="password" />
            </label>
            {!isLogin && (
              <label className="grid gap-2 text-xs font-semibold">Confirm password
                <input className="h-11 rounded-lg border border-line bg-white px-3 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" name="confirmPassword" placeholder="Repeat password" type="password" />
              </label>
            )}
            {error && <p className="flex items-center gap-2 rounded-lg bg-danger-soft p-3 text-xs text-danger" role="alert"><WarningCircle aria-hidden="true" size={18} />{error}</p>}
            <PrimaryButton className="mt-1 w-full" disabled={pending} type="submit">{pending ? 'Opening workspace…' : isLogin ? 'Log in' : 'Create account'}</PrimaryButton>
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
