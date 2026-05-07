'use client';

import { PrivyProvider as PrivyAuthProvider } from '@privy-io/react-auth';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { useState, type ReactNode } from 'react';

import { privyAppId, privyConfig } from '@/lib/config/privy';
import { wagmiConfig } from '@/lib/config/wagmi';

interface PrivyProviderProps {
  children: ReactNode;
}

/**
 * Privy Provider
 *
 * This provider sets up:
 * - Privy for authentication (embedded wallets + social login)
 * - wagmi for Ethereum interactions
 * - TanStack Query for async state management
 *
 * Privy automatically handles:
 * - Wallet creation for new users
 * - SIWE (Sign-In with Ethereum) flow
 * - Session management
 *
 * @see https://docs.privy.io/guide/react/quickstart
 */
export function PrivyProvider({ children }: PrivyProviderProps) {
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

  if (!privyAppId) {
    console.warn(
      '⚠️ NEXT_PUBLIC_PRIVY_APP_ID is not set. ' +
      'Privy authentication will not work. ' +
      'Get your app ID at https://dashboard.privy.io/'
    );
  }

  return (
    <PrivyAuthProvider
      appId={privyAppId}
      config={privyConfig}
    >
      <QueryClientProvider client={queryClient}>
        <WagmiProvider config={wagmiConfig}>
          {children}
        </WagmiProvider>
      </QueryClientProvider>
    </PrivyAuthProvider>
  );
}
