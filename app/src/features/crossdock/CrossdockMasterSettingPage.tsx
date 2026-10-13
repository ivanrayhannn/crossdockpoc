import { useCallback } from 'react';
import { AppShell } from '../../components/shell/AppShell';
import type { RouteKey } from '../../routes';
import { BreadcrumbBar } from '../../components/shell/BreadcrumbBar';
import { DestMappingTab } from './components/DestMappingTab';
import { HistoryModal } from './components/HistoryModal';
import { PageHeader } from './components/PageHeader';
import { PartDetailTab } from './components/PartDetailTab';
import { PartListTab } from './components/PartListTab';
import { PartModal } from './components/PartModal';
import { RoleGate } from './components/RoleGate';
import { SaveSuccessModal } from './components/SaveSuccessModal';
import { MappingUploadModal } from './components/MappingUploadModal';
import { UploadModal } from './components/UploadModal';
import { ViewTabs } from './components/ViewTabs';
import { exportPartsXlsx, selectParts } from './partList';
import { useCrossdockState } from './useCrossdockState';
import { usePartDetail } from './usePartDetail';

const SUB_MENU_LABEL = { procurement: 'Part List / Part Detail', ds: 'Mapping per Destination' } as const;
const ACTIVE_ITEM = 'Crossdock Master Setting';

export function CrossdockMasterSettingPage({ onNavigate }: { onNavigate: (route: RouteKey) => void }) {
  const state = useCrossdockState();
  const { parts, q, aq, setQ, runSearch, resetQ, ro, role, setRole, switchRole, view, setProcView, modal, addPart, openUpload, openFor, notice, dismissNotice } = state;
  const detail = usePartDetail(parts);

  // Sheet 1 follows the Part List table (same filter and sort, all pages); sheet "Upload" holds every part.
  const exportExcel = useCallback(() => {
    exportPartsXlsx(selectParts(parts, aq), parts).catch((err) => {
      console.error('Export Excel failed', err);
      window.alert('Export Excel failed. Please try again.');
    });
  }, [parts, aq]);

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
      <ViewTabs view={view} onChange={setProcView} />

      {view === 'part' && (
        <PartListTab
          parts={parts}
          q={q}
          aq={aq}
          setQ={setQ}
          onSearch={runSearch}
          resetQ={resetQ}
          ro={ro}
          onOpenPart={(id) => openFor(id, 'part')}
          onOpenHistory={(id) => openFor(id, 'history')}
          onAddPart={addPart}
          onOpenUpload={openUpload}
        />
      )}
      {view === 'detail' && <PartDetailTab parts={parts} ro={ro} detail={detail} />}
      {view === 'dest' && <DestMappingTab state={state} />}

      {modal === 'part' && <PartModal state={state} />}
      {modal === 'upload' && <UploadModal state={state} />}
      {modal === 'upload-mapping' && <MappingUploadModal state={state} />}
      {modal === 'history' && <HistoryModal state={state} />}
      {notice && <SaveSuccessModal notice={notice} onClose={dismissNotice} />}
    </AppShell>
  );
}
