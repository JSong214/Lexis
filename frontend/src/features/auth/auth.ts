import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiGet, apiPost } from '../../lib/api-client'

export interface AuthUser {
  created_at: string
  email: string
  id: string
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

function login(credentials: AuthCredentials) {
  return apiPost<AuthUser>('/auth/login', credentials)
}

function register(credentials: AuthCredentials) {
  return apiPost<AuthUser>('/auth/register', credentials)
}

function logout() {
  return apiPost<void>('/auth/logout')
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
