/**
 * Feature Flags Configuration
 *
 * Enable or disable features across the application.
 * This allows for easy customization without code changes.
 */
export const features = {
  /**
   * Use Privy for authentication
   * When enabled, provides embedded wallets + social login
   * When disabled, falls back to RainbowKit wallet-only auth
   */
  privy: Boolean(process.env['NEXT_PUBLIC_PRIVY_APP_ID']),

  /**
   * Enable internationalization with next-intl
   * Requires message files in /messages directory
   */
  i18n: false,

  /**
   * Use Zustand for complex UI state
   * Most state should use wagmi hooks + React Context
   */
  zustand: false,

  /**
   * Enable analytics tracking
   * Implement your preferred analytics provider
   */
  analytics: false,

  /**
   * Show testnet chains in chain selector
   */
  testnets: process.env.NODE_ENV === 'development',

  /**
   * Enable debug mode
   * Shows additional logging and dev tools
   */
  debug: process.env.NODE_ENV === 'development',
} as const;

/**
 * Type for feature flags
 */
export type FeatureFlags = typeof features;

/**
 * Check if a feature is enabled
 */
export function isFeatureEnabled<K extends keyof FeatureFlags>(
  feature: K
): boolean {
  return features[feature];
}
