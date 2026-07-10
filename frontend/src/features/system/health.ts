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
    refetchInterval: 30_000,
  })
}
