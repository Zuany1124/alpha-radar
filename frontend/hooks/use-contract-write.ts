'use client';

import {
  useSimulateContract,
  useWriteContract,
  useWaitForTransactionReceipt,
} from 'wagmi';
import { toast } from 'sonner';
import { useEffect, useCallback } from 'react';
import type { Abi, Address, ContractFunctionArgs, ContractFunctionName } from 'viem';

type WriteFunctionName<TAbi extends Abi> = ContractFunctionName<TAbi, 'nonpayable' | 'payable'>;
type WriteArgs<TAbi extends Abi, TFunctionName extends WriteFunctionName<TAbi>> =
  ContractFunctionArgs<TAbi, 'nonpayable' | 'payable', TFunctionName>;

interface UseContractWriteOptions<TAbi extends Abi, TFunctionName extends WriteFunctionName<TAbi>> {
  /** Contract address */
  address: Address;
  /** Contract ABI */
  abi: TAbi;
  /** Function name to call */
  functionName: TFunctionName;
  /** Function arguments */
  args?: WriteArgs<TAbi, TFunctionName>;
  /** Value to send (in wei) */
  value?: bigint;
  /** Enable simulation */
  simulateEnabled?: boolean;
  /** Toast messages */
  toasts?: {
    pending?: string;
    success?: string;
    error?: string;
  };
  /** Callbacks */
  onSuccess?: (hash: `0x${string}`) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook for contract writes with best practices
 *
 * Implements the recommended pattern:
 * 1. Simulate transaction first
 * 2. Write to contract
 * 3. Wait for confirmation
 * 4. Show toast notifications throughout
 *
 * @example
 * const { execute, isPending, isConfirming, isSuccess } = useContractWrite({
 *   address: '0x...',
 *   abi: myContractAbi,
 *   functionName: 'mint',
 *   args: [1n],
 *   toasts: {
 *     pending: 'Minting NFT...',
 *     success: 'NFT minted successfully!',
 *     error: 'Failed to mint NFT',
 *   },
 * });
 */
export function useContractWrite<TAbi extends Abi, TFunctionName extends WriteFunctionName<TAbi>>({
  address,
  abi,
  functionName,
  args,
  value,
  simulateEnabled = true,
  toasts = {},
  onSuccess,
  onError,
}: UseContractWriteOptions<TAbi, TFunctionName>) {
  const toastId = `contract-write-${address}-${functionName}`;

  // 1. Simulate the transaction
  const simulateParams = {
    address,
    abi,
    functionName,
    args,
    ...(value !== undefined ? { value } : {}),
    query: {
      enabled: simulateEnabled,
    },
  } as Parameters<typeof useSimulateContract>[0];

  const simulateResult = useSimulateContract(simulateParams);
  const simulation = simulateResult.data as
    | { request?: Parameters<typeof writeContract>[0] }
    | undefined;
  const { error: simulationError, isLoading: isSimulating } = simulateResult;

  // 2. Write to contract
  const {
    writeContract,
    data: hash,
    isPending,
    error: writeError,
    reset,
  } = useWriteContract();

  // 3. Wait for confirmation
  const {
    isLoading: isConfirming,
    isSuccess,
    error: confirmError,
  } = useWaitForTransactionReceipt({
    hash,
  });

  // Combined error
  const error = simulationError ?? writeError ?? confirmError;

  // Handle toast notifications
  useEffect(() => {
    if (isPending) {
      toast.loading(toasts.pending ?? 'Waiting for wallet approval...', {
        id: toastId,
      });
    }
  }, [isPending, toasts.pending, toastId]);

  useEffect(() => {
    if (hash && isConfirming) {
      toast.loading('Transaction pending...', {
        id: toastId,
        description: `Hash: ${hash.slice(0, 10)}...`,
      });
    }
  }, [hash, isConfirming, toastId]);

  useEffect(() => {
    if (isSuccess && hash) {
      toast.success(toasts.success ?? 'Transaction confirmed!', {
        id: toastId,
        description: `Hash: ${hash.slice(0, 10)}...`,
      });
      onSuccess?.(hash);
    }
  }, [isSuccess, hash, toasts.success, toastId, onSuccess]);

  useEffect(() => {
    if (error) {
      toast.error(toasts.error ?? 'Transaction failed', {
        id: toastId,
        description: error.message.slice(0, 100),
      });
      onError?.(error);
    }
  }, [error, toasts.error, toastId, onError]);

  // Execute function
  const execute = useCallback(() => {
    if (simulateEnabled && simulationError) {
      toast.error('Simulation failed', {
        id: toastId,
        description: simulationError.message.slice(0, 100),
      });
      return;
    }

    if (simulateEnabled && !simulation?.request) {
      toast.error('Unable to simulate transaction', { id: toastId });
      return;
    }

    // Use simulated request if available, otherwise construct manually
    if (simulation?.request) {
      writeContract(simulation.request);
    } else {
      writeContract({
        address,
        abi,
        functionName,
        args,
        value,
      } as Parameters<typeof writeContract>[0]);
    }
  }, [
    simulateEnabled,
    simulationError,
    simulation,
    writeContract,
    address,
    abi,
    functionName,
    args,
    value,
    toastId,
  ]);

  return {
    /** Execute the contract write */
    execute,
    /** Transaction hash (after submission) */
    hash,
    /** Simulation is running */
    isSimulating,
    /** Waiting for wallet approval */
    isPending,
    /** Waiting for block confirmation */
    isConfirming,
    /** Transaction confirmed */
    isSuccess,
    /** Any error that occurred */
    error,
    /** Simulation error specifically */
    simulationError,
    /** Reset the hook state */
    reset,
    /** Whether simulation passed */
    canExecute: !simulationError && Boolean(simulation?.request),
  };
}
