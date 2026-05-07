import { formatEther, formatUnits } from 'viem';

/**
 * Format an Ethereum address for display
 *
 * @example
 * formatAddress('0x1234567890abcdef1234567890abcdef12345678')
 * // => '0x1234...5678'
 */
export function formatAddress(
  address: string,
  startLength = 6,
  endLength = 4
): string {
  if (!address) return '';
  if (address.length < startLength + endLength) return address;
  return `${address.slice(0, startLength)}...${address.slice(-endLength)}`;
}

/**
 * Format a balance for display with appropriate decimals
 *
 * @example
 * formatBalance(1234567890000000000n) // => '1.2346'
 * formatBalance(1234567890000000000n, 18, 2) // => '1.23'
 */
export function formatBalance(
  balance: bigint,
  decimals = 18,
  displayDecimals = 4
): string {
  const formatted = formatUnits(balance, decimals);
  const [whole, fraction = ''] = formatted.split('.');

  if (displayDecimals === 0) return whole ?? '0';

  const truncatedFraction = fraction.slice(0, displayDecimals);
  const paddedFraction = truncatedFraction.padEnd(displayDecimals, '0');

  return `${whole}.${paddedFraction}`;
}

/**
 * Format ETH balance with symbol
 *
 * @example
 * formatEthBalance(1234567890000000000n) // => '1.2346 ETH'
 */
export function formatEthBalance(
  balance: bigint,
  displayDecimals = 4
): string {
  return `${formatBalance(balance, 18, displayDecimals)} ETH`;
}

/**
 * Format a number with commas for thousands
 *
 * @example
 * formatNumber(1234567.89) // => '1,234,567.89'
 */
export function formatNumber(
  value: number | string,
  maximumFractionDigits = 2
): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits,
  }).format(num);
}

/**
 * Format USD value
 *
 * @example
 * formatUsd(1234.56) // => '$1,234.56'
 */
export function formatUsd(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

/**
 * Format a transaction hash for display
 *
 * @example
 * formatTxHash('0x1234567890abcdef...')
 * // => '0x1234...cdef'
 */
export function formatTxHash(hash: string): string {
  return formatAddress(hash, 10, 8);
}

/**
 * Parse a string to bigint with decimals
 *
 * @example
 * parseTokenAmount('1.5', 18) // => 1500000000000000000n
 */
export function parseTokenAmount(
  amount: string,
  decimals = 18
): bigint {
  const [whole, fraction = ''] = amount.split('.');
  const paddedFraction = fraction.padEnd(decimals, '0').slice(0, decimals);
  return BigInt(whole + paddedFraction);
}
