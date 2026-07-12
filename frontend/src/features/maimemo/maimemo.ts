import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiGet, apiPost, apiPut } from '../../lib/api-client'

export interface MaimemoConnection {
  configured: boolean
  provider: string | null
  secretSaved: boolean
  updatedAt: string | null
}

export interface VocabularyProfile {
  id: string
  snapshotId: string
  newWords: string[]
  fuzzyWords: string[]
  masteredWordsSample: string[]
  masteredWordCount: number
  createdAt: string
}

export const connectionQueryKey = ['maimemo', 'connection'] as const
export const vocabularyProfileQueryKey = ['vocabulary', 'profile'] as const

export function useMaimemoConnectionQuery() {
  return useQuery({
    queryKey: connectionQueryKey,
    queryFn: () => apiGet<MaimemoConnection>('/maimemo/connection'),
  })
}

export function useVocabularyProfileQuery() {
  return useQuery({
    queryKey: vocabularyProfileQueryKey,
    queryFn: () => apiGet<VocabularyProfile>('/vocabulary/profile'),
    retry: false,
  })
}

export function useSaveMaimemoConnectionMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (secret?: string) => apiPut<MaimemoConnection>(
      '/maimemo/connection',
      { provider: 'mock', secret: secret || null },
    ),
    onSuccess: (connection) => {
      queryClient.setQueryData(connectionQueryKey, connection)
    },
  })
}

export function useSyncMaimemoMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiPost<VocabularyProfile>('/maimemo/sync'),
    onSuccess: (profile) => {
      queryClient.setQueryData(vocabularyProfileQueryKey, profile)
    },
  })
}
