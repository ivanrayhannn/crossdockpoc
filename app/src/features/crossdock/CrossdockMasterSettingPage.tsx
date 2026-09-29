import { AppShell } from '../../components/shell/AppShell';
import type { RouteKey } from '../../routes';
import { BreadcrumbBar } from '../../components/shell/BreadcrumbBar';
import { DestMappingTab } from './components/DestMappingTab';
import { HistoryModal } from './components/HistoryModal';
import { PageHeader } from './components/PageHeader';
import { PartListTab } from './components/PartListTab';
import { PartModal } from './components/PartModal';
import { RoleGate } from './components/RoleGate';
import { UploadModal } from './components/UploadModal';
import { ViewTabs } from './components/ViewTabs';
import { useCrossdockState } from './useCrossdockState';

const ROLE_LABEL = { procurement: 'Procurement', ds: 'Tim D/S' } as const;
const ACTIVE_ITEM = 'Crossdock Master Setting';

export function CrossdockMasterSettingPage({ onNavigate }: { onNavigate: (route: RouteKey) => void }) {
  const state = useCrossdockState();
  const { parts, q, setQ, resetQ, ro, role, setRole, switchRole, view, modal, addPart, openUpload, openFor, syncAll } = state;

  if (!role) {
    return (
      <AppShell activeItem={ACTIVE_ITEM} onNavigate={onNavigate} breadcrumb={<BreadcrumbBar roleLabel="Belum dipilih" />}>
        <RoleGate onSelect={setRole} />
      </AppShell>
    );
  }

  const roleLabel = ROLE_LABEL[role];

  return (
    <AppShell activeItem={ACTIVE_ITEM} onNavigate={onNavigate} breadcrumb={<BreadcrumbBar roleLabel={roleLabel} onSwitchRole={switchRole} />}>
      <PageHeader roleLabel={roleLabel} ro={ro} view={view} onAddPart={addPart} onOpenUpload={openUpload} onSync={syncAll} />
      <ViewTabs view={view} />

      {view === 'part' && (
        <PartListTab
          parts={parts}
          q={q}
          setQ={setQ}
          resetQ={resetQ}
          ro={ro}
          onOpenPart={(id) => openFor(id, 'part')}
          onOpenHistory={(id) => openFor(id, 'history')}
          onAddPart={addPart}
          onOpenUpload={openUpload}
        />
      )}
      {view === 'dest' && <DestMappingTab state={state} />}

      {modal === 'part' && <PartModal state={state} />}
      {modal === 'upload' && <UploadModal state={state} />}
      {modal === 'history' && <HistoryModal state={state} />}
    </AppShell>
  );
}
