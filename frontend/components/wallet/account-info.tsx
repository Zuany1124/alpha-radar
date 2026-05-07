'use client';

import { useAccount, useBalance, useEnsName, useEnsAvatar } from 'wagmi';
import { mainnet } from 'viem/chains';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatAddress, formatEthBalance } from '@/lib/utils';

/**
 * Account Info Component
 *
 * Displays connected wallet information:
 * - ENS name and avatar (if available)
 * - Wallet address
 * - ETH balance
 */
export function AccountInfo() {
  const { address, isConnected } = useAccount();

  const { data: ensName } = useEnsName({
    address,
    chainId: mainnet.id,
  });

  const { data: ensAvatar } = useEnsAvatar({
    name: ensName ?? undefined,
    chainId: mainnet.id,
  });

  const { data: balance } = useBalance({
    address,
  });

  if (!isConnected || !address) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Connect your wallet to view account details.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Avatar and Name */}
        <div className="flex items-center gap-4">
          {ensAvatar ? (
            <img
              src={ensAvatar}
              alt={ensName ?? 'Avatar'}
              className="h-12 w-12 rounded-full"
            />
          ) : (
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-violet-500" />
          )}

          <div>
            {ensName && (
              <p className="font-medium">{ensName}</p>
            )}
            <p className="text-sm text-muted-foreground font-mono">
              {formatAddress(address)}
            </p>
          </div>
        </div>

        {/* Balance */}
        {balance && (
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground">Balance</p>
            <p className="text-2xl font-bold">
              {formatEthBalance(balance.value)}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
