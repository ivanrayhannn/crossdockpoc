import { useCallback, useEffect, useState } from 'react';
import { AppShell } from './components/shell/AppShell';
import { Breadcrumb } from './components/shell/Breadcrumb';
import { CaseConsolidationPage } from './features/caseConsolidation/CaseConsolidationPage';
import { CrossdockMasterSettingPage } from './features/crossdock/CrossdockMasterSettingPage';
import { routeFromHash, hashForRoute } from './routes';
import type { RouteKey } from './routes';

function App() {
  const [route, setRoute] = useState<RouteKey>(() => routeFromHash(window.location.hash));

  useEffect(() => {
    const onHashChange = () => setRoute(routeFromHash(window.location.hash));
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigate = useCallback((next: RouteKey) => {
    window.location.hash = hashForRoute(next);
    setRoute(next);
  }, []);

  if (route === 'case-consolidation') {
    return (
      <AppShell activeItem="Case Consolidation Simulation" onNavigate={navigate} breadcrumb={<Breadcrumb group="ASN" label="Case Consolidation Simulation" />}>
        <CaseConsolidationPage />
      </AppShell>
    );
  }

  return <CrossdockMasterSettingPage onNavigate={navigate} />;
}

export default App;
