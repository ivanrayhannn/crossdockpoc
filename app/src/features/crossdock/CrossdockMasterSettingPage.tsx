import { AppShell } from '../../components/shell/AppShell';
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

export function CrossdockMasterSettingPage() {
  const state = useCrossdockState();
  const { parts, q, setQ, resetQ, ro, role, setRole, switchRole, view, modal, addPart, openUpload, openFor } = state;

  if (!role) {
    return (
      <AppShell roleLabel="Belum dipilih">
        <RoleGate onSelect={setRole} />
      </AppShell>
    );
  }

  const roleLabel = ROLE_LABEL[role];

  return (
    <AppShell roleLabel={roleLabel} onSwitchRole={switchRole}>
      <PageHeader roleLabel={roleLabel} ro={ro} showPartActions={view === 'part'} onAddPart={addPart} onOpenUpload={openUpload} />
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
