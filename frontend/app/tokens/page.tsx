import { Suspense } from 'react';
import { createPublicClient, http, formatEther } from 'viem';
import { mainnet } from 'viem/chains';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Create a public client for server-side chain data fetching
 *
 * This runs on the server and doesn't require wallet connection.
 */
const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
});

/**
 * Example: Fetch ETH price from a known address (Chainlink price feed)
 * This demonstrates Server Component data fetching.
 */
async function getEthBalance(address: `0x${string}`) {
  try {
    const balance = await publicClient.getBalance({ address });
    return formatEther(balance);
  } catch (error) {
    console.error('Failed to fetch balance:', error);
    return null;
  }
}

/**
 * Balance Display Component (Server Component)
 *
 * Fetches and displays balance for a given address.
 * Runs on the server, no client-side JavaScript needed.
 */
async function BalanceDisplay({ address, label }: { address: `0x${string}`; label: string }) {
  const balance = await getEthBalance(address);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{label}</CardTitle>
        <CardDescription className="font-mono text-xs">
          {address.slice(0, 10)}...{address.slice(-8)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-bold">
          {balance ? `${parseFloat(balance).toFixed(4)} ETH` : 'Error loading'}
        </p>
      </CardContent>
    </Card>
  );
}

/**
 * Loading Skeleton
 */
function BalanceSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="h-5 w-32 bg-muted animate-pulse rounded" />
        <div className="h-3 w-48 bg-muted animate-pulse rounded mt-2" />
      </CardHeader>
      <CardContent>
        <div className="h-8 w-24 bg-muted animate-pulse rounded" />
      </CardContent>
    </Card>
  );
}

/**
 * Tokens Page
 *
 * This is a Server Component that demonstrates:
 * - Server-side chain data fetching with viem
 * - Suspense boundaries for streaming
 * - Partial Prerendering (PPR)
 *
 * The static shell renders immediately, while balance data streams in.
 */
export default function TokensPage() {
  // Example addresses (well-known addresses for demonstration)
  const addresses = [
    {
      address: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045' as `0x${string}`,
      label: 'vitalik.eth',
    },
    {
      address: '0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8' as `0x${string}`,
      label: 'Binance Hot Wallet',
    },
    {
      address: '0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503' as `0x${string}`,
      label: 'Binance Cold Wallet',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">On-Chain Data</h1>
        <p className="text-muted-foreground mt-2">
          Server-side fetched balances using viem + Suspense
        </p>
      </div>

      {/* Static content (renders immediately) */}
      <div className="mb-8 p-4 bg-muted/50 rounded-lg">
        <h2 className="font-semibold mb-2">How This Works</h2>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>• This page uses Server Components to fetch chain data</li>
          <li>• No wallet connection required - data is fetched server-side</li>
          <li>• Suspense boundaries enable streaming for better UX</li>
          <li>• PPR serves static shell immediately, streams dynamic content</li>
        </ul>
      </div>

      {/* Dynamic content (streams in) */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {addresses.map(({ address, label }) => (
          <Suspense key={address} fallback={<BalanceSkeleton />}>
            <BalanceDisplay address={address} label={label} />
          </Suspense>
        ))}
      </div>

      {/* Code Example */}
      <div className="mt-12">
        <h2 className="text-xl font-bold mb-4">Code Example</h2>
        <Card>
          <CardContent className="pt-6">
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
              <code>{`// Server Component - No 'use client' directive
import { createPublicClient, http } from 'viem';
import { mainnet } from 'viem/chains';

const client = createPublicClient({
  chain: mainnet,
  transport: http(),
});

async function Balance({ address }) {
  // This runs on the server!
  const balance = await client.getBalance({ address });
  return <p>{formatEther(balance)} ETH</p>;
}

// Use with Suspense for streaming
<Suspense fallback={<Skeleton />}>
  <Balance address="0x..." />
</Suspense>`}</code>
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
