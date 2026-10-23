import { useCallback, useEffect, useState } from 'react';
import { AppShell } from './components/shell/AppShell';
import { Breadcrumb } from './components/shell/Breadcrumb';
import { AsnCrossdockCreationPage } from './features/asnCrossdock/AsnCrossdockCreationPage';
import { AsnInquiryPage } from './features/asnCrossdock/AsnInquiryPage';
import { ChangeOrderNumberPage } from './features/changeOrder/ChangeOrderNumberPage';
import { CaseConsolidationPage } from './features/caseConsolidation/CaseConsolidationPage';
import { CrossdockMasterSettingPage } from './features/crossdock/CrossdockMasterSettingPage';
import { BatchProcessPage } from './features/batchProcess/BatchProcessPage';
import { CandidatePartFlowPage } from './features/candidatePartFlow/CandidatePartFlowPage';
import { AsnBackendProcessPage } from './features/asnBackend/AsnBackendProcessPage';
import { CancelOrderSimulationPage } from './features/cancelSim/CancelOrderSimulationPage';
import { BusinessProcessFlowPage } from './features/bpf/BusinessProcessFlowPage';
import { ConfirmationPage } from './features/confirmation/ConfirmationPage';

import { LogMonitoringPage } from './features/logMonitoring/LogMonitoringPage';
import { MenuSettingsPage } from './features/menuSettings/MenuSettingsPage';
import { hashForRoute, routeFromHash } from './routes';
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

  if (route === 'asn-creation') {
    return (
      <AppShell activeItem="ASN Creation" onNavigate={navigate} breadcrumb={<Breadcrumb group="ASN" label="ASN Crossdock Creation" />}>
        <AsnCrossdockCreationPage />
      </AppShell>
    );
  }

  if (route === 'change-order') {
    return (
      <AppShell activeItem="Change Order Number" onNavigate={navigate} breadcrumb={<Breadcrumb group="ASN" label="Change Order Number" />}>
        <ChangeOrderNumberPage />
      </AppShell>
    );
  }

  if (route === 'asn-inquiry') {
    return (
      <AppShell activeItem="ASN Inquiry" onNavigate={navigate} breadcrumb={<Breadcrumb group="ASN" label="ASN Inquiry" />}>
        <AsnInquiryPage />
      </AppShell>
    );
  }

  if (route === 'batch-process') {
    return (
      <AppShell activeItem="Batch Process Simulation" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="Batch Process Simulation" />}>
        <BatchProcessPage />
      </AppShell>
    );
  }

  if (route === 'candidate-flow') {
    return (
      <AppShell activeItem="Candidate Part Batch Flow" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="Candidate Part Batch Flow" />}>
        <CandidatePartFlowPage />
      </AppShell>
    );
  }

  if (route === 'asn-backend') {
    return (
      <AppShell activeItem="ASN Backend Process" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="ASN Backend Process" />}>
        <AsnBackendProcessPage />
      </AppShell>
    );
  }

  if (route === 'cancel-simulation') {
    return (
      <AppShell activeItem="Cancel Order Simulation" onNavigate={navigate} breadcrumb={<Breadcrumb group="ASN" label="Cancel Order Simulation" />}>
        <CancelOrderSimulationPage />
      </AppShell>
    );
  }

  if (route === 'bpf') {
    return (
      <AppShell activeItem="Business Process Flow" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="Business Process Flow" />}>
        <BusinessProcessFlowPage />
      </AppShell>
    );
  }

  if (route === 'confirmation') {
    return (
      <AppShell activeItem="Confirmation Points" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="Confirmation Points" />}>
        <ConfirmationPage />
      </AppShell>
    );
  }

  if (route === 'menu-settings') {
    return (
      <AppShell activeItem="Menu Settings" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="Menu Settings" />}>
        <MenuSettingsPage />
      </AppShell>
    );
  }

  if (route === 'log-monitoring') {
    return (
      <AppShell activeItem="Log Monitoring" onNavigate={navigate} breadcrumb={<Breadcrumb group="Common" label="Log Monitoring" />}>
        <LogMonitoringPage />
      </AppShell>
    );
  }

  return <CrossdockMasterSettingPage onNavigate={navigate} />;
}

export default App;
