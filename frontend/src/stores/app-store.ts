import { create } from 'zustand'

interface AppState {
  isNavigationOpen: boolean
  toggleNavigation: () => void
}

export const useAppStore = create<AppState>((set) => ({
  isNavigationOpen: true,
  toggleNavigation: () =>
    set((state) => ({
      isNavigationOpen: !state.isNavigationOpen,
    })),
}))
