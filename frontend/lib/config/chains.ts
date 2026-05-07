import {
  mainnet,
  arbitrum,
  base,
  polygon,
  optimism,
  // Testnets (uncomment as needed)
  // sepolia,
  // arbitrumSepolia,
  // baseSepolia,
  // polygonAmoy,
  // optimismSepolia,
} from 'viem/chains';
import type { Chain } from 'viem/chains';

/**
 * Supported Chains Configuration
 *
 * Add or remove chains as needed for your dApp.
 * All chains must be imported from 'viem/chains'.
 *
 * @see https://viem.sh/docs/chains/introduction
 */
export const supportedChains = [
  mainnet,
  arbitrum,
  base,
  polygon,
  optimism,
  // Add testnets for development:
  // sepolia,
  // arbitrumSepolia,
  // baseSepolia,
] as const satisfies readonly [Chain, ...Chain[]];

/**
 * Type for supported chain IDs
 */
export type SupportedChainId = (typeof supportedChains)[number]['id'];

/**
 * Default chain for the application
 */
export const defaultChain = mainnet;

/**
 * Chain metadata for UI display
 */
export const chainMetadata: Record<SupportedChainId, {
  name: string;
  shortName: string;
  color: string;
  icon?: string;
}> = {
  [mainnet.id]: {
    name: 'Ethereum',
    shortName: 'ETH',
    color: '#627EEA',
  },
  [arbitrum.id]: {
    name: 'Arbitrum One',
    shortName: 'ARB',
    color: '#28A0F0',
  },
  [base.id]: {
    name: 'Base',
    shortName: 'BASE',
    color: '#0052FF',
  },
  [polygon.id]: {
    name: 'Polygon',
    shortName: 'MATIC',
    color: '#8247E5',
  },
  [optimism.id]: {
    name: 'Optimism',
    shortName: 'OP',
    color: '#FF0420',
  },
};

/**
 * Check if a chain ID is supported
 */
export function isSupportedChain(chainId: number): chainId is SupportedChainId {
  return supportedChains.some((chain) => chain.id === chainId);
}

/**
 * Get chain by ID
 */
export function getChainById(chainId: number): Chain | undefined {
  return supportedChains.find((chain) => chain.id === chainId);
}
