# next-web3-pure-frontend

> 🚀 Production-ready, pure frontend Web3 dApp starter for 2026 — No backend, no database, just modern Web3.

A lightweight, highly customizable Next.js 16 Web3 scaffold featuring React 19, wagmi v2, viem v2, RainbowKit 2.x, and Privy authentication. Built with 2026 best practices including React Compiler, Tailwind CSS v4, and shadcn/ui.

## ✨ Features

### Core Stack
- **Next.js 16** with App Router and React Compiler
- **React 19** with Server Components and Suspense for optimal data fetching
- **TypeScript 5.9+** for type safety
- **Tailwind CSS v4** with CSS-first configuration
- **shadcn/ui** component system (beautifully designed, accessible)

### Web3 Infrastructure
- **wagmi v2** + **viem v2** — Modern Ethereum interaction library
- **@tanstack/react-query v5** — Powerful async state management
- **RainbowKit 2.x** — Beautiful wallet connection UI with EIP-6963 support
- **Privy** — Embedded wallets + social/email login for seamless onboarding

### DX & UX
- **sonner** — Elegant toast notifications for transaction states
- **next-themes** — Dark/light mode with system preference detection
- **next-intl v4** (optional) — Type-safe internationalization
- **zustand v5** (optional) — Lightweight state management

### Best Practices
- ✅ Server Components for read-only chain data (balance, ENS, tokens)
- ✅ Client Components only for wallet interactions
- ✅ Simulate → Write → Wait pattern for all contract writes
- ✅ Unified error handling with toast feedback
- ✅ Client-only Web3 providers for build stability with Turbopack
- ✅ Zero backend dependencies

## 🚀 Quick Start

### Option 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-username/next-web3-pure-frontend.git
cd next-web3-pure-frontend

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env.local

# Start development server (Turbopack)
pnpm dev
```

### Option 2: Create from Scratch

```bash
# Create Next.js app
pnpm create next-app@latest my-web3-app --typescript --tailwind --eslint --app --src-dir=false

cd my-web3-app

# Install Web3 dependencies
pnpm add wagmi viem @tanstack/react-query @rainbow-me/rainbowkit

# Install Privy (recommended)
pnpm add @privy-io/react-auth @privy-io/wagmi

# Install UI dependencies
pnpm add sonner next-themes class-variance-authority clsx tailwind-merge lucide-react

# Install dev dependencies
pnpm add -D @tailwindcss/postcss babel-plugin-react-compiler
```

### Environment Variables

Create `.env.local` with:

```env
# WalletConnect Project ID (required)
# Get yours at https://cloud.walletconnect.com/
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your_project_id

# Privy App ID (optional, for Privy auth)
# Get yours at https://dashboard.privy.io/
NEXT_PUBLIC_PRIVY_APP_ID=your_privy_app_id

# RPC URLs (optional, uses public RPCs by default)
NEXT_PUBLIC_ALCHEMY_ID=your_alchemy_id
```

## 📁 Project Structure

```
project/
├── app/
│   ├── [locale]/               # Optional i18n routes
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── globals.css             # Tailwind v4 imports + theme
│   ├── layout.tsx              # Root layout with Providers
│   └── page.tsx                # Home page
├── components/
│   ├── ui/                     # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── layout/                 # Layout components
│   │   ├── navbar.tsx
│   │   ├── footer.tsx
│   │   └── theme-switcher.tsx
│   └── wallet/                 # Wallet components
│       ├── connect-button.tsx
│       ├── chain-switcher.tsx
│       └── account-info.tsx
├── hooks/                      # Custom React hooks
│   ├── use-token-balance.ts
│   ├── use-contract-write.ts
│   └── use-mounted.ts
├── lib/
│   ├── config/                 # Configuration
│   │   ├── chains.ts           # Supported chains
│   │   ├── wagmi.ts            # wagmi + RainbowKit config
│   │   └── privy.ts            # Privy config
│   ├── empty-module.ts         # Turbopack empty alias target
│   └── utils/                  # Utility functions
│       ├── cn.ts               # Class name merger
│       ├── format.ts           # formatAddress, formatBalance
│       └── index.ts
├── providers/                  # React Providers
│   ├── providers.tsx           # Combined providers wrapper
│   ├── wagmi-provider.tsx      # WagmiProvider + RainbowKit
│   ├── privy-provider.tsx      # PrivyProvider (optional)
│   └── theme-provider.tsx      # next-themes provider
├── stores/                     # Zustand stores (optional)
│   └── ui-store.ts
├── messages/                   # i18n messages (optional)
│   ├── en.json
│   └── zh.json
├── public/
│   └── ...
├── .env.example
├── .env.local
├── next.config.ts
├── package.json
├── postcss.config.js
├── tailwind.config.ts          # Minimal (v4 uses CSS)
└── tsconfig.json
```

## 🔧 Configuration

### Enabling React Compiler

In `next.config.ts`:

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Enable React Compiler
  reactCompiler: true,
};

export default nextConfig;
```

If you need advanced rendering strategies, prefer route-level caching and streaming instead of experimental PPR flags.

### Turbopack Settings

This project builds with Turbopack by default. Node-only modules used by some Web3 libraries are aliased to an empty module:

```typescript
const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      fs: './lib/empty-module.ts',
      net: './lib/empty-module.ts',
      tls: './lib/empty-module.ts',
      '@react-native-async-storage/async-storage': './lib/empty-module.ts',
    },
  },
};
```

### Adding shadcn/ui Components

```bash
# Initialize shadcn/ui (first time)
pnpm dlx shadcn@latest init

# Add components
pnpm dlx shadcn@latest add button card dialog dropdown-menu
```

### Authentication Strategy

#### Default: Privy (Recommended)

Privy provides the best onboarding experience with:
- Embedded wallets (no extension needed)
- Social login (Google, Apple, Twitter)
- Email/SMS authentication
- Automatic SIWE handling

To use Privy, set `NEXT_PUBLIC_PRIVY_APP_ID` in your `.env.local`.

#### Fallback: RainbowKit Only

If you prefer traditional wallet-only auth:

1. Remove or comment out `PrivyProvider` in `providers/providers.tsx`
2. Use `<ConnectButton />` from RainbowKit directly
3. Implement manual SIWE if needed (see `hooks/use-siwe.ts`)

### Supported Chains

Default chains in `lib/config/chains.ts`:
- Ethereum Mainnet
- Arbitrum One
- Base
- Polygon
- Optimism

To add more chains:

```typescript
// lib/config/chains.ts
import { mainnet, arbitrum, base, polygon, optimism, sepolia } from 'viem/chains';

export const supportedChains = [
  mainnet,
  arbitrum,
  base,
  polygon,
  optimism,
  sepolia, // Add testnet
] as const;
```

## 📝 Code Examples

### Server Component: Reading Chain Data

```typescript
// app/balance/page.tsx
import { createPublicClient, http, formatEther } from 'viem';
import { mainnet } from 'viem/chains';
import { Suspense } from 'react';

const client = createPublicClient({
  chain: mainnet,
  transport: http(),
});

async function Balance({ address }: { address: `0x${string}` }) {
  const balance = await client.getBalance({ address });
  return <p>Balance: {formatEther(balance)} ETH</p>;
}

export default function BalancePage() {
  return (
    <Suspense fallback={<p>Loading balance...</p>}>
      <Balance address="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" />
    </Suspense>
  );
}
```

### Client Component: Writing to Contract

```typescript
'use client';

import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { parseEther } from 'viem';
import { toast } from 'sonner';
import { useEffect } from 'react';

export function SendTransaction() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  useEffect(() => {
    if (isPending) toast.loading('Waiting for approval...', { id: 'tx' });
    if (hash) toast.loading('Transaction pending...', { id: 'tx' });
    if (isSuccess) toast.success('Transaction confirmed!', { id: 'tx' });
    if (error) toast.error(error.message, { id: 'tx' });
  }, [isPending, hash, isSuccess, error]);

  const handleSend = async () => {
    writeContract({
      address: '0x...',
      abi: [...],
      functionName: 'transfer',
      args: ['0x...', parseEther('1')],
    });
  };

  return (
    <button onClick={handleSend} disabled={isPending || isConfirming}>
      {isPending ? 'Confirming...' : isConfirming ? 'Processing...' : 'Send'}
    </button>
  );
}
```

### Best Practice: Simulate → Write → Wait

```typescript
'use client';

import { useSimulateContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { toast } from 'sonner';

const abi = [...] as const;

export function useContractAction() {
  // 1. Simulate first
  const { data: simulation, error: simError } = useSimulateContract({
    address: '0x...',
    abi,
    functionName: 'mint',
    args: [1n],
  });

  // 2. Write with simulated request
  const { writeContract, data: hash, isPending } = useWriteContract();

  // 3. Wait for confirmation
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const execute = () => {
    if (simError) {
      toast.error('Simulation failed: ' + simError.message);
      return;
    }
    if (!simulation?.request) {
      toast.error('Unable to simulate transaction');
      return;
    }

    toast.loading('Sending transaction...', { id: 'mint' });
    writeContract(simulation.request, {
      onSuccess: () => toast.loading('Waiting for confirmation...', { id: 'mint' }),
      onError: (err) => toast.error(err.message, { id: 'mint' }),
    });
  };

  return { execute, isPending, isConfirming, isSuccess };
}
```

## 🌐 Internationalization (Optional)

To enable i18n with next-intl:

1. Uncomment i18n code in `middleware.ts`
2. Create message files in `messages/`
3. Use the `[locale]` route structure

```typescript
// Using translations
import { useTranslations } from 'next-intl';

export function MyComponent() {
  const t = useTranslations('common');
  return <h1>{t('welcome')}</h1>;
}
```

## 🎨 Theming

Theme switching is handled by `next-themes`:

```typescript
import { useTheme } from 'next-themes';

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      Toggle Theme
    </button>
  );
}
```

## 📦 Feature Flags

Enable/disable features by modifying `lib/config/features.ts`:

```typescript
export const features = {
  privy: true,           // Use Privy for auth
  i18n: false,           // Enable internationalization
  zustand: false,        // Use Zustand for state
  analytics: false,      // Enable analytics
} as const;
```

## 🔍 FAQ

### Why no backend/database?

This scaffold is designed for pure frontend dApps where:
- All data comes from the blockchain
- Authentication is wallet-based (SIWE)
- No server-side state is needed

For apps needing a backend, consider adding tRPC, Prisma, or a BaaS.

### Why Privy over other auth solutions?

Privy offers:
- Embedded wallets (users don't need MetaMask)
- Social login with automatic wallet creation
- Built-in SIWE handling
- Best-in-class onboarding UX

### Can I use ethers.js instead of viem?

We strongly recommend viem for:
- Smaller bundle size
- Better TypeScript support
- Modern ESM-first design
- Active maintenance

### How do I add a new chain?

1. Import the chain from `viem/chains`
2. Add to `supportedChains` in `lib/config/chains.ts`
3. Add transport in `lib/config/wagmi.ts`

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ for the Web3 community.
