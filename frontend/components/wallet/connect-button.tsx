'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import { usePrivy } from '@privy-io/react-auth';
import { useAccount } from 'wagmi';

import { Button } from '@/components/ui/button';
import { isPrivyEnabled } from '@/lib/config/privy';
import { formatAddress } from '@/lib/utils';

/**
 * Connect Wallet Button
 *
 * Renders the appropriate connect button based on auth strategy:
 * - Privy: Uses Privy's login modal (embedded wallet + social)
 * - RainbowKit: Uses RainbowKit's connect modal
 */
export function ConnectWalletButton() {
  if (isPrivyEnabled) {
    return <PrivyConnectButton />;
  }

  return <RainbowKitConnectButton />;
}

/**
 * Privy Connect Button
 *
 * Uses Privy for authentication with embedded wallets and social login.
 */
function PrivyConnectButton() {
  const { login, logout, authenticated, user, ready } = usePrivy();
  const { address, isConnected } = useAccount();

  if (!ready) {
    return (
      <Button disabled>
        Loading...
      </Button>
    );
  }

  if (authenticated && user) {
    return (
      <Button
        variant="outline"
        onClick={logout}
        className="gap-2"
      >
        <span className="h-2 w-2 rounded-full bg-green-500" />
        {address ? formatAddress(address) : user.email?.address ?? 'Connected'}
      </Button>
    );
  }

  return (
    <Button onClick={login}>
      Connect Wallet
    </Button>
  );
}

/**
 * RainbowKit Connect Button
 *
 * Custom styled RainbowKit connect button.
 */
function RainbowKitConnectButton() {
  return (
    <ConnectButton.Custom>
      {({
        account,
        chain,
        openAccountModal,
        openChainModal,
        openConnectModal,
        mounted,
      }) => {
        const ready = mounted;
        const connected = ready && account && chain;

        return (
          <div
            {...(!ready && {
              'aria-hidden': true,
              style: {
                opacity: 0,
                pointerEvents: 'none',
                userSelect: 'none',
              },
            })}
          >
            {(() => {
              if (!connected) {
                return (
                  <Button onClick={openConnectModal}>
                    Connect Wallet
                  </Button>
                );
              }

              if (chain.unsupported) {
                return (
                  <Button variant="destructive" onClick={openChainModal}>
                    Wrong Network
                  </Button>
                );
              }

              return (
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={openChainModal}
                    className="gap-2"
                  >
                    {chain.hasIcon && chain.iconUrl && (
                      <img
                        alt={chain.name ?? 'Chain icon'}
                        src={chain.iconUrl}
                        className="h-4 w-4 rounded-full"
                      />
                    )}
                    <span className="hidden sm:inline">{chain.name}</span>
                  </Button>

                  <Button
                    variant="outline"
                    onClick={openAccountModal}
                    className="gap-2"
                  >
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    {account.displayName}
                    {account.displayBalance && (
                      <span className="hidden sm:inline text-muted-foreground">
                        ({account.displayBalance})
                      </span>
                    )}
                  </Button>
                </div>
              );
            })()}
          </div>
        );
      }}
    </ConnectButton.Custom>
  );
}
