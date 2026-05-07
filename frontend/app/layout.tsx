import type { Metadata, Viewport } from 'next';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';

import { Providers } from '@/providers';
import { Navbar } from '@/components/layout/navbar';
import { Footer } from '@/components/layout/footer';

import './globals.css';

/**
 * Metadata Configuration
 * @see https://nextjs.org/docs/app/api-reference/functions/generate-metadata
 */
export const metadata: Metadata = {
  title: {
    default: 'Web3 dApp',
    template: '%s | Web3 dApp',
  },
  description: 'A modern Web3 decentralized application built with Next.js 15, React 19, and wagmi v2.',
  keywords: ['web3', 'dapp', 'ethereum', 'blockchain', 'defi', 'nft'],
  authors: [{ name: 'Your Name' }],
  creator: 'Your Name',
  metadataBase: new URL('https://your-domain.com'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://your-domain.com',
    title: 'Web3 dApp',
    description: 'A modern Web3 decentralized application',
    siteName: 'Web3 dApp',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Web3 dApp',
    description: 'A modern Web3 decentralized application',
    creator: '@yourhandle',
  },
  robots: {
    index: true,
    follow: true,
  },
};

/**
 * Viewport Configuration
 */
export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
  width: 'device-width',
  initialScale: 1,
};

/**
 * Root Layout
 *
 * This is the root layout for the entire application.
 * It wraps all pages with providers and common UI elements.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans antialiased">
        <Providers>
          <div className="relative flex min-h-screen flex-col">
            <Navbar />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}
