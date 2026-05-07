/**
 * Request-based i18n Configuration
 *
 * This file is OPTIONAL. Uncomment and configure if you need i18n.
 *
 * @see https://next-intl.dev/docs/getting-started/app-router
 */

import { getRequestConfig } from 'next-intl/server';
import { routing, type Locale } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  // Validate that the incoming locale is valid
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale as Locale)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
