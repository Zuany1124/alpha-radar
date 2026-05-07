'use client';

import Link from 'next/link';
import { Menu } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { ThemeSwitcher } from './theme-switcher';
import { ConnectWalletButton } from '@/components/wallet/connect-button';
import { cn } from '@/lib/utils';

/**
 * Navigation Links
 */
const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/tokens', label: 'Tokens' },
  // Add more links as needed
];

/**
 * Navbar Component
 *
 * Responsive navigation bar with:
 * - Logo/brand
 * - Navigation links
 * - Theme switcher
 * - Wallet connect button
 */
export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-600 to-violet-600" />
          <span className="font-bold text-xl hidden sm:inline-block">
            Web3 dApp
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-6">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center space-x-4">
          <ThemeSwitcher />

          {/* Desktop Connect Button */}
          <div className="hidden sm:block">
            <ConnectWalletButton />
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle menu</span>
          </Button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        className={cn(
          'md:hidden border-t',
          mobileMenuOpen ? 'block' : 'hidden'
        )}
      >
        <div className="container mx-auto px-4 py-4 space-y-4">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="block text-sm font-medium text-muted-foreground hover:text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}

          {/* Mobile Connect Button */}
          <div className="pt-4 border-t">
            <ConnectWalletButton />
          </div>
        </div>
      </div>
    </header>
  );
}
