/**
 * Internationalization Routing Configuration
 *
 * This file is OPTIONAL. Uncomment and configure if you need i18n.
 *
 * @see https://next-intl.dev/docs/routing
 */

import { defineRouting } from 'next-intl/routing';

/**
 * Supported locales
 */
export const locales = ['en', 'zh', 'ja', 'ko'] as const;
export type Locale = (typeof locales)[number];

/**
 * Default locale
 */
export const defaultLocale: Locale = 'en';

/**
 * Routing configuration
 */
export const routing = defineRouting({
  locales,
  defaultLocale,
  // 'as-needed' - Only show locale prefix for non-default locales
  // 'always' - Always show locale prefix
  localePrefix: 'as-needed',
});
