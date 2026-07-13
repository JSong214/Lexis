import { QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import { Toaster } from 'sonner'

import { queryClient } from './app/query-client'
import { router } from './app/router'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster
        position="top-center"
        richColors
        theme="light"
        toastOptions={{
          duration: 4000,
          classNames: {
            toast: 'rounded-lg border border-line bg-white text-ink shadow-[0_12px_36px_rgba(17,20,23,0.12)]',
            title: 'text-sm font-semibold',
            description: 'text-xs text-ink-muted',
          },
        }}
      />
    </QueryClientProvider>
  </StrictMode>,
)
