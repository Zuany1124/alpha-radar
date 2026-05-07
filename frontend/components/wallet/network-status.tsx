'use client';

import { useAccount, useChainId, useBlockNumber } from 'wagmi';
import { useEffect, useState } from 'react';

import { chainMetadata, type SupportedChainId } from '@/lib/config/chains';

/**
 * Network Status Component
 *
 * Displays current network information when connected:
 * - Chain name
 * - Latest block number
 * - Connection status indicator
 */
export function NetworkStatus() {
  const { isConnected } = useAccount();
  const chainId = useChainId();
  const { data: blockNumber } = useBlockNumber({ watch: true });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  if (!isConnected) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="h-2 w-2 rounded-full bg-gray-400" />
        Not connected
      </div>
    );
  }

  const metadata = chainMetadata[chainId as SupportedChainId];

  return (
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-2">
        <span
          className="h-2 w-2 rounded-full animate-pulse"
          style={{ backgroundColor: metadata?.color ?? '#22c55e' }}
        />
        <span className="text-muted-foreground">
          {metadata?.name ?? `Chain ${chainId}`}
        </span>
      </div>

      {blockNumber && (
        <div className="text-muted-foreground">
          Block: {blockNumber.toLocaleString()}
        </div>
      )}
    </div>
  );
}
