'use client';

import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { http } from 'wagmi';
import { supportedChains, defaultChain } from './chains';

/**
 * WalletConnect Project ID
 * Get yours at https://cloud.walletconnect.com/
 */
const walletConnectProjectId = process.env['NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID'];

if (!walletConnectProjectId) {
  console.warn(
    '⚠️ NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID is not set. ' +
    'Get your project ID at https://cloud.walletconnect.com/'
  );
}

/**
 * Optional: Alchemy API Key for better RPC performance
 */
const alchemyId = process.env['NEXT_PUBLIC_ALCHEMY_ID'];

/**
 * RPC Transports Configuration
 *
 * Uses Alchemy if API key is provided, otherwise falls back to public RPCs.
 * For production, always use a dedicated RPC provider.
 */
const transports = {
  // Ethereum Mainnet
  1: alchemyId
    ? http(`https://eth-mainnet.g.alchemy.com/v2/${alchemyId}`)
    : http(),
  // Arbitrum One
  42161: alchemyId
    ? http(`https://arb-mainnet.g.alchemy.com/v2/${alchemyId}`)
    : http(),
  // Base
  8453: alchemyId
    ? http(`https://base-mainnet.g.alchemy.com/v2/${alchemyId}`)
    : http(),
  // Polygon
  137: alchemyId
    ? http(`https://polygon-mainnet.g.alchemy.com/v2/${alchemyId}`)
    : http(),
  // Optimism
  10: alchemyId
    ? http(`https://opt-mainnet.g.alchemy.com/v2/${alchemyId}`)
    : http(),
} as const;

/**
 * Wagmi + RainbowKit Configuration
 *
 * This uses RainbowKit's getDefaultConfig which:
 * - Sets up wagmi with sensible defaults
 * - Configures wallet connectors (injected, WalletConnect, etc.)
 * - Enables EIP-6963 wallet discovery
 * - Sets up multichain support
 *
 * @see https://rainbowkit.com/docs/installation
 */
export const wagmiConfig = getDefaultConfig({
  appName: 'Web3 dApp',
  projectId: walletConnectProjectId ?? 'YOUR_PROJECT_ID',
  chains: supportedChains,
  transports,
  // Disable SSR to avoid browser-only APIs during build
  ssr: false,
});

/**
 * Export for use in other parts of the app
 */
export { defaultChain, supportedChains };
