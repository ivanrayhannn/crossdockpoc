/* Minimal hash-based routing — the app has only a few pages, so a full router is overkill. */

export type RouteKey = 'crossdock' | 'case-consolidation' | 'asn-creation' | 'candidate-flow';

/** Sidebar nav items that actually navigate somewhere; everything else in the nav is inert. */
export const ROUTE_BY_NAV_ITEM: Record<string, RouteKey> = {
  'Crossdock Master Setting': 'crossdock',
  'Case Consolidation Simulation': 'case-consolidation',
  'ASN Creation': 'asn-creation',
  'Candidate Part Batch Flow': 'candidate-flow',
};

export const DEFAULT_ROUTE: RouteKey = 'crossdock';

const ROUTE_KEYS: RouteKey[] = ['case-consolidation', 'asn-creation', 'candidate-flow'];

export function routeFromHash(hash: string): RouteKey {
  const key = hash.replace(/^#\/?/, '');
  return (ROUTE_KEYS as string[]).includes(key) ? (key as RouteKey) : DEFAULT_ROUTE;
}

export function hashForRoute(route: RouteKey): string {
  return route === DEFAULT_ROUTE ? '' : `#/${route}`;
}
