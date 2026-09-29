/* Minimal hash-based routing — the app has only two pages, so a full router is overkill. */

export type RouteKey = 'crossdock' | 'case-consolidation';

/** Sidebar nav items that actually navigate somewhere; everything else in the nav is inert. */
export const ROUTE_BY_NAV_ITEM: Record<string, RouteKey> = {
  'Crossdock Master Setting': 'crossdock',
  'Case Consolidation Simulation': 'case-consolidation',
};

export const DEFAULT_ROUTE: RouteKey = 'crossdock';

export function routeFromHash(hash: string): RouteKey {
  return hash.replace(/^#\/?/, '') === 'case-consolidation' ? 'case-consolidation' : DEFAULT_ROUTE;
}

export function hashForRoute(route: RouteKey): string {
  return route === DEFAULT_ROUTE ? '' : `#/${route}`;
}
