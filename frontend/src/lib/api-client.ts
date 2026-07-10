const API_PREFIX = import.meta.env.VITE_API_PREFIX ?? '/api/v1'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, {
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw new ApiError(`API request failed with status ${response.status}`, response.status)
  }

  return response.json() as Promise<T>
}

