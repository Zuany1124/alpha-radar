/**
 * UI Store (Zustand)
 *
 * Optional store for complex UI state that doesn't fit in:
 * - wagmi hooks (wallet/chain state)
 * - React Context (theme, providers)
 * - Component local state
 *
 * Use sparingly - prefer wagmi hooks and React Context for most cases.
 *
 * @see https://zustand-demo.pmnd.rs/
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface UIState {
  // Sidebar state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Modal state
  activeModal: string | null;
  openModal: (modalId: string) => void;
  closeModal: () => void;

  // User preferences (persisted)
  preferences: {
    compactMode: boolean;
    showBalances: boolean;
    defaultChainId: number | null;
  };
  setPreference: <K extends keyof UIState['preferences']>(
    key: K,
    value: UIState['preferences'][K]
  ) => void;
}

/**
 * UI Store
 *
 * @example
 * // In a component
 * const { sidebarOpen, toggleSidebar } = useUIStore();
 *
 * // Or select specific values
 * const sidebarOpen = useUIStore((state) => state.sidebarOpen);
 */
export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Sidebar
      sidebarOpen: false,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      // Modal
      activeModal: null,
      openModal: (modalId) => set({ activeModal: modalId }),
      closeModal: () => set({ activeModal: null }),

      // Preferences
      preferences: {
        compactMode: false,
        showBalances: true,
        defaultChainId: null,
      },
      setPreference: (key, value) =>
        set((state) => ({
          preferences: {
            ...state.preferences,
            [key]: value,
          },
        })),
    }),
    {
      name: 'ui-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist preferences
      partialize: (state) => ({ preferences: state.preferences }),
    }
  )
);
