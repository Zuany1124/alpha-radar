/**
 * Next.js Middleware
 *
 * This middleware handles:
 * - Internationalization routing (optional, uncomment to enable)
 * - Security headers
 * - Request logging (development only)
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Uncomment for i18n support:
// import createMiddleware from 'next-intl/middleware';
// import { routing } from './i18n/routing';

/**
 * i18n Middleware (Optional)
 *
 * Uncomment the following to enable internationalization:
 */
// const intlMiddleware = createMiddleware(routing);

export function middleware(request: NextRequest) {
  // For i18n, uncomment:
  // return intlMiddleware(request);

  // Default: pass through
  const response = NextResponse.next();

  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
}

/**
 * Middleware Matcher
 *
 * Configure which routes the middleware runs on.
 */
export const config = {
  matcher: [
    // Match all routes except:
    // - API routes
    // - Static files
    // - _next internals
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)',
  ],
};
