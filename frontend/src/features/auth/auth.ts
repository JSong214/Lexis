import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiGet, apiPatch, apiPost } from '../../lib/api-client'

export type CefrLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'
export type LearningGoal =
  | 'General English'
  | 'CET-4'
  | 'CET-6'
  | 'IELTS'
  | 'TOEFL'
  | 'Postgraduate Entrance English'
  | 'Academic English'
  | 'Workplace English'

export interface AuthUser {
  created_at: string
  email: string
  id: string
  cefr_level: CefrLevel
  learning_goal: LearningGoal
}

export interface UserPreferences {
  cefr_level: CefrLevel
  learning_goal: LearningGoal
}

export interface AuthCredentials {
  email: string
  password: string
}

export const currentUserQueryKey = ['auth', 'me'] as const

export function getCurrentUser() {
  return apiGet<AuthUser>('/auth/me')
}

export function useCurrentUserQuery() {
  return useQuery({
    queryKey: currentUserQueryKey,
    queryFn: getCurrentUser,
    retry: false,
  })
}

function updatePreferences(preferences: UserPreferences) {
  return apiPatch<AuthUser>('/auth/me/preferences', preferences)
}

function login(credentials: AuthCredentials) {
  return apiPost<AuthUser>('/auth/login', credentials)
}

function register(credentials: AuthCredentials) {
  return apiPost<AuthUser>('/auth/register', credentials)
}

function logout() {
  return apiPost<void>('/auth/logout')
}

export function useUpdatePreferencesMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: updatePreferences,
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserQueryKey, user)
    },
  })
}

export function useLoginMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: login,
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserQueryKey, user)
    },
  })
}

export function useRegisterMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: register,
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserQueryKey, user)
    },
  })
}

export function useLogoutMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: currentUserQueryKey })
    },
  })
}
