'use client';

import { useEffect, useState } from 'react';

/**
 * Hook to check if component is mounted
 *
 * Useful for avoiding hydration mismatches with SSR.
 *
 * @example
 * const mounted = useMounted();
 * if (!mounted) return <Skeleton />;
 * return <ClientOnlyContent />;
 */
export function useMounted(): boolean {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return mounted;
}
