import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'

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
  practiceWords: string[]
  masteredWordsSample: string[]
  trackedWordCount: number
  dailyFinishedCount: number
  dailyTotalCount: number
  dailyStudyTimeMs: number
  createdAt: string
}

export const connectionQueryKey = ['maimemo', 'connection'] as const
export const vocabularyProfileQueryKey = ['vocabulary', 'profile'] as const
const MAIMEMO_AUTO_SYNC_INTERVAL_MS = 5 * 60 * 1000

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
      { provider: 'maimemo', secret: secret || null },
    ),
    onSuccess: async (connection) => {
      queryClient.setQueryData(connectionQueryKey, connection)
      await queryClient.resetQueries({ queryKey: vocabularyProfileQueryKey })
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

export function useAutoSyncMaimemo(enabled: boolean) {
  const syncMaimemo = useSyncMaimemoMutation()
  const syncRef = useRef(syncMaimemo)

  useEffect(() => {
    syncRef.current = syncMaimemo
  }, [syncMaimemo])

  useEffect(() => {
    if (!enabled) {
      return
    }

    const intervalId = window.setInterval(() => {
      if (document.visibilityState === 'visible' && !syncRef.current.isPending) {
        syncRef.current.mutate()
      }
    }, MAIMEMO_AUTO_SYNC_INTERVAL_MS)

    return () => window.clearInterval(intervalId)
  }, [enabled])

  return syncMaimemo
}
