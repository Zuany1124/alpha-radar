'use client';

import { useReadContract, useAccount } from 'wagmi';
import { formatUnits } from 'viem';
import type { Address } from 'viem';

/**
 * ERC20 ABI for balanceOf and decimals
 */
const erc20Abi = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: 'balance', type: 'uint256' }],
  },
  {
    name: 'decimals',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: 'decimals', type: 'uint8' }],
  },
  {
    name: 'symbol',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: 'symbol', type: 'string' }],
  },
] as const;

interface UseTokenBalanceOptions {
  /** Token contract address */
  tokenAddress: Address;
  /** Override account address (defaults to connected wallet) */
  account?: Address;
  /** Enable/disable the query */
  enabled?: boolean;
}

interface UseTokenBalanceResult {
  /** Raw balance in wei */
  balance: bigint | undefined;
  /** Formatted balance with decimals */
  formatted: string | undefined;
  /** Token decimals */
  decimals: number | undefined;
  /** Token symbol */
  symbol: string | undefined;
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  isError: boolean;
  /** Error object */
  error: Error | null;
  /** Refetch function */
  refetch: () => void;
}

/**
 * Hook to fetch ERC20 token balance
 *
 * @example
 * const { balance, formatted, symbol, isLoading } = useTokenBalance({
 *   tokenAddress: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // USDC
 * });
 *
 * if (isLoading) return <Spinner />;
 * return <p>{formatted} {symbol}</p>;
 */
export function useTokenBalance({
  tokenAddress,
  account: overrideAccount,
  enabled = true,
}: UseTokenBalanceOptions): UseTokenBalanceResult {
  const { address: connectedAddress } = useAccount();
  const account = overrideAccount ?? connectedAddress;

  // Fetch balance
  const {
    data: balance,
    isLoading: balanceLoading,
    isError: balanceError,
    error: balanceErrorObj,
    refetch: refetchBalance,
  } = useReadContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: account ? [account] : undefined,
    query: {
      enabled: enabled && Boolean(account),
    },
  });

  // Fetch decimals
  const { data: decimals, isLoading: decimalsLoading } = useReadContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: 'decimals',
    query: {
      enabled,
    },
  });

  // Fetch symbol
  const { data: symbol, isLoading: symbolLoading } = useReadContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: 'symbol',
    query: {
      enabled,
    },
  });

  // Format balance
  const formatted =
    balance !== undefined && decimals !== undefined
      ? formatUnits(balance, decimals)
      : undefined;

  return {
    balance,
    formatted,
    decimals,
    symbol,
    isLoading: balanceLoading || decimalsLoading || symbolLoading,
    isError: balanceError,
    error: balanceErrorObj,
    refetch: refetchBalance,
  };
}
