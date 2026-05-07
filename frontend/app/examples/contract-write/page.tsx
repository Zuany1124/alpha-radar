'use client';

import { useState } from 'react';
import { useAccount } from 'wagmi';
import { parseEther } from 'viem';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ConnectWalletButton } from '@/components/wallet/connect-button';
import { useContractWrite } from '@/hooks/use-contract-write';

/**
 * Example ERC20 ABI (minimal for transfer)
 */
const erc20Abi = [
  {
    name: 'transfer',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'to', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ name: 'success', type: 'bool' }],
  },
] as const;

/**
 * Contract Write Example Page
 *
 * Demonstrates the best practice pattern for contract writes:
 * 1. Simulate transaction first
 * 2. Write to contract
 * 3. Wait for confirmation
 * 4. Show toast notifications throughout
 */
export default function ContractWriteExamplePage() {
  const { isConnected } = useAccount();
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');

  // Example: USDC on Ethereum mainnet
  const tokenAddress = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48';

  const {
    execute,
    isPending,
    isConfirming,
    isSuccess,
    canExecute,
    simulationError,
    reset,
  } = useContractWrite({
    address: tokenAddress as `0x${string}`,
    abi: erc20Abi,
    functionName: 'transfer',
    args: recipient && amount ? [recipient as `0x${string}`, parseEther(amount)] : undefined,
    simulateEnabled: Boolean(recipient && amount),
    toasts: {
      pending: 'Sending tokens...',
      success: 'Tokens sent successfully!',
      error: 'Failed to send tokens',
    },
  });

  if (!isConnected) {
    return (
      <div className="container mx-auto px-4 py-16">
        <Card className="max-w-md mx-auto">
          <CardHeader className="text-center">
            <CardTitle>Connect Your Wallet</CardTitle>
            <CardDescription>
              Connect your wallet to try the contract write example
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ConnectWalletButton />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Contract Write Example</h1>
        <p className="text-muted-foreground mt-2">
          Demonstrates the simulate → write → wait pattern with toast notifications
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Send Tokens</CardTitle>
            <CardDescription>
              Example ERC20 transfer (simulation only - won&apos;t actually send)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Recipient Address</label>
              <input
                type="text"
                placeholder="0x..."
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md bg-background"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Amount</label>
              <input
                type="text"
                placeholder="0.0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md bg-background"
              />
            </div>

            {simulationError && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                Simulation failed: {simulationError.message.slice(0, 100)}
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={execute}
                disabled={!canExecute || isPending || isConfirming}
                className="flex-1"
              >
                {isPending
                  ? 'Confirming...'
                  : isConfirming
                  ? 'Processing...'
                  : 'Send Tokens'}
              </Button>

              {isSuccess && (
                <Button variant="outline" onClick={reset}>
                  Reset
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Code Example */}
        <Card>
          <CardHeader>
            <CardTitle>Code</CardTitle>
            <CardDescription>
              Using the useContractWrite hook
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
              <code>{`const { execute, isPending, isConfirming } = useContractWrite({
  address: tokenAddress,
  abi: erc20Abi,
  functionName: 'transfer',
  args: [recipient, amount],
  toasts: {
    pending: 'Sending tokens...',
    success: 'Tokens sent!',
    error: 'Failed to send',
  },
});

// The hook automatically:
// 1. Simulates the transaction
// 2. Shows pending toast
// 3. Waits for confirmation
// 4. Shows success/error toast

<Button onClick={execute} disabled={isPending}>
  {isPending ? 'Confirming...' : 'Send'}
</Button>`}</code>
            </pre>
          </CardContent>
        </Card>
      </div>

      {/* Best Practices */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Best Practices</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-green-500">✓</span>
              <span>
                <strong>Always simulate first:</strong> Use{' '}
                <code className="bg-muted px-1 rounded">useSimulateContract</code> to catch errors
                before sending transactions
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500">✓</span>
              <span>
                <strong>Wait for confirmation:</strong> Use{' '}
                <code className="bg-muted px-1 rounded">useWaitForTransactionReceipt</code> to
                confirm the transaction was mined
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500">✓</span>
              <span>
                <strong>Show feedback:</strong> Use toast notifications to keep users informed
                throughout the transaction lifecycle
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500">✓</span>
              <span>
                <strong>Handle errors gracefully:</strong> Catch and display simulation errors
                before the user submits
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
