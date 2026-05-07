'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { RainbowKitProvider, darkTheme, lightTheme } from '@rainbow-me/rainbowkit';
import { useState, type ReactNode } from 'react';
import { useTheme } from 'next-themes';

import { wagmiConfig } from '@/lib/config/wagmi';

// Import RainbowKit styles
import '@rainbow-me/rainbowkit/styles.css';

interface Web3ProviderProps {
  children: ReactNode;
}

/**
 * Web3 Provider (RainbowKit + wagmi + TanStack Query)
 *
 * This provider sets up:
 * - wagmi for Ethereum interactions
 * - TanStack Query for async state management
 * - RainbowKit for wallet connection UI
 *
 * Use this when NOT using Privy, or as a fallback.
 */
export function Web3Provider({ children }: Web3ProviderProps) {
  const { resolvedTheme } = useTheme();

  // Create QueryClient instance (must be stable across renders)
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Stale time for chain data (30 seconds)
            staleTime: 30 * 1000,
            // Retry failed queries
            retry: 2,
            // Refetch on window focus
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider
          theme={resolvedTheme === 'dark' ? darkTheme() : lightTheme()}
          modalSize="compact"
          showRecentTransactions={true}
        >
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
