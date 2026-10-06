import { useCallback } from 'react';
import { AppShell } from '../../components/shell/AppShell';
import type { RouteKey } from '../../routes';
import { BreadcrumbBar } from '../../components/shell/BreadcrumbBar';
import { DestMappingTab } from './components/DestMappingTab';
import { HistoryModal } from './components/HistoryModal';
import { PageHeader } from './components/PageHeader';
import { PartListTab } from './components/PartListTab';
import { PartModal } from './components/PartModal';
import { RoleGate } from './components/RoleGate';
import { SaveSuccessModal } from './components/SaveSuccessModal';
import { UploadModal } from './components/UploadModal';
import { ViewTabs } from './components/ViewTabs';
import { exportPartsXlsx, selectParts } from './partList';
import { useCrossdockState } from './useCrossdockState';

const SUB_MENU_LABEL = { procurement: 'Part List', ds: 'Mapping per Destination' } as const;
const ACTIVE_ITEM = 'Crossdock Master Setting';

export function CrossdockMasterSettingPage({ onNavigate }: { onNavigate: (route: RouteKey) => void }) {
  const state = useCrossdockState();
  const { parts, q, setQ, resetQ, ro, role, setRole, switchRole, view, modal, addPart, openUpload, openFor, notice, dismissNotice } = state;

  // Export what the Part List table shows: same filter and sort, all pages.
  const exportExcel = useCallback(() => {
    exportPartsXlsx(selectParts(parts, q)).catch((err) => {
      console.error('Export Excel failed', err);
      window.alert('Export Excel failed. Please try again.');
    });
  }, [parts, q]);

  if (!role) {
    return (
      <AppShell activeItem={ACTIVE_ITEM} onNavigate={onNavigate} breadcrumb={<BreadcrumbBar simLabel="none" />}>
        <RoleGate onSelect={setRole} />
      </AppShell>
    );
  }

  const simLabel = SUB_MENU_LABEL[role];

  return (
    <AppShell activeItem={ACTIVE_ITEM} onNavigate={onNavigate} breadcrumb={<BreadcrumbBar simLabel={simLabel} onSwitch={switchRole} />}>
      <PageHeader ro={ro} view={view} onAddPart={addPart} onOpenUpload={openUpload} onExport={exportExcel} />
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
      {notice && <SaveSuccessModal notice={notice} onClose={dismissNotice} />}
    </AppShell>
  );
}
