import type { PrivyClientConfig } from '@privy-io/react-auth';
import { supportedChains, defaultChain } from './chains';

/**
 * Privy App ID
 * Get yours at https://dashboard.privy.io/
 */
export const privyAppId = process.env['NEXT_PUBLIC_PRIVY_APP_ID'] ?? '';

/**
 * Check if Privy is enabled
 */
export const isPrivyEnabled = Boolean(privyAppId);

/**
 * Privy Configuration
 *
 * Privy provides:
 * - Embedded wallets (no browser extension needed)
 * - Social login (Google, Apple, Twitter, Discord, etc.)
 * - Email/SMS authentication
 * - Automatic SIWE handling
 *
 * @see https://docs.privy.io/guide/react/configuration
 */
export const privyConfig: PrivyClientConfig = {
  // Appearance
  appearance: {
    // Theme follows system preference, or set to 'light' | 'dark'
    theme: 'dark',
    // Accent color for buttons and highlights
    accentColor: '#6366f1', // Indigo
    // Logo displayed in the modal
    logo: '/logo.svg',
    // Show wallet address in the modal
    showWalletLoginFirst: false,
  },

  // Login methods to display
  loginMethods: [
    'email',
    'wallet',
    'google',
    'apple',
    'twitter',
    // 'discord',
    // 'github',
    // 'linkedin',
    // 'sms',
    // 'farcaster',
  ],

  // Embedded wallet configuration
  embeddedWallets: {
    // Automatically create wallet on login for users without one
    ethereum: {
      createOnLogin: 'users-without-wallets',
    },
    // Show wallet UI in the Privy modal
    showWalletUIs: true,
  },

  // External wallet configuration
  externalWallets: {
    // Supported chains for external wallets
    // @ts-expect-error - Privy types may not match viem chains exactly
    ethereum: {
      chains: supportedChains,
      defaultChain: defaultChain,
    },
  },

  // Legal links (optional)
  legal: {
    termsAndConditionsUrl: '/terms',
    privacyPolicyUrl: '/privacy',
  },
};

/**
 * Privy wallet configuration for wagmi integration
 */
export const privyWagmiConfig = {
  // Chains to support
  chains: supportedChains,
};
