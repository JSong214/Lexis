import { Navigate, createBrowserRouter } from 'react-router'

import { AppShell } from '../layouts/AppShell'
import { AuthPage } from '../pages/AuthPage'
import { CompletionPage } from '../pages/CompletionPage'
import { ConnectionPage } from '../pages/ConnectionPage'
import { HistoryDetailPage } from '../pages/HistoryDetailPage'
import { HistoryPage } from '../pages/HistoryPage'
import { LessonPage } from '../pages/LessonPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { WorkspacePage } from '../pages/WorkspacePage'

export const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/app/workspace" replace /> },
  { path: '/login', element: <AuthPage mode="login" /> },
  { path: '/register', element: <AuthPage mode="register" /> },
  {
    path: '/app',
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="workspace" replace /> },
      { path: 'workspace', element: <WorkspacePage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'history/:lessonId', element: <HistoryDetailPage /> },
      { path: 'lessons/:lessonId', element: <LessonPage /> },
      { path: 'lessons/:lessonId/complete', element: <CompletionPage /> },
      { path: 'settings/connection', element: <ConnectionPage /> },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
])
