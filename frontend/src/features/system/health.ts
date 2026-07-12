import { useQuery } from '@tanstack/react-query'

import { apiGet } from '../../lib/api-client'

export interface HealthResponse {
  api_version: string
  environment: string
  service: string
  status: 'ok'
}

export function getHealth() {
  return apiGet<HealthResponse>('/health')
}

export function useHealthQuery() {
  return useQuery({
    queryKey: ['system', 'health'],
    queryFn: getHealth,
    staleTime: 60_000,
    refetchInterval: (query) =>
      query.state.status === 'error' ? 30_000 : 120_000,
    refetchIntervalInBackground: false,
    refetchOnWindowFocus: true,
  })
}
