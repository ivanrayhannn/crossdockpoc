import { useCallback } from 'react';
import { AppShell } from '../../components/shell/AppShell';
import type { RouteKey } from '../../routes';
import { BreadcrumbBar } from '../../components/shell/BreadcrumbBar';
import { DestMappingTab, selectDestRows } from './components/DestMappingTab';
import { HistoryModal } from './components/HistoryModal';
import { PageHeader } from './components/PageHeader';
import { PartListTab } from './components/PartListTab';
import { PartModal } from './components/PartModal';
import { RoleGate } from './components/RoleGate';
import { SaveSuccessModal } from './components/SaveSuccessModal';
import { MappingUploadModal } from './components/MappingUploadModal';
import { UploadModal } from './components/UploadModal';
import { ViewTabs } from './components/ViewTabs';
import { exportMappingXlsx } from './mappingExport';
import { exportPartsXlsx, selectParts } from './partList';
import { CUR_PER, PAST_ROWS } from '../../data/seed';
import { useCrossdockState } from './useCrossdockState';

const SUB_MENU_LABEL = { procurement: 'Kanban Crossdock Master', ds: 'Export Crossdock Master' } as const;
const ACTIVE_ITEM = 'Crossdock Master Setting';

export function CrossdockMasterSettingPage({ onNavigate }: { onNavigate: (route: RouteKey) => void }) {
  const state = useCrossdockState();
  const { parts, pastRows, q, aq, setQ, runSearch, resetQ, ro, role, setRole, switchRole, view, modal, addPart, openUpload, openMappingUpload, openFor, notice, dismissNotice, dadRun, runCalc } = state;

  // Sheet 1 follows the Kanban Crossdock Master table (same filter and sort, all pages); sheet "Upload" holds every part.
  const exportExcel = useCallback(() => {
    exportPartsXlsx(selectParts(parts.concat(PAST_ROWS), aq), parts).catch((err) => {
      console.error('Export Excel failed', err);
      window.alert('Export Excel failed. Please try again.');
    });
  }, [parts, aq]);

  // Export Crossdock Master: sheet 1 = rows of the applied criteria (as the table), sheet "Upload" = the ongoing mapping.
  const exportMapping = useCallback(() => {
    exportMappingXlsx(selectDestRows(parts.concat(pastRows), aq), aq.per, parts).catch((err) => {
      console.error('Export Excel failed', err);
      window.alert('Export Excel failed. Please try again.');
    });
  }, [parts, pastRows, aq]);

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
      <PageHeader
        ro={ro}
        view={view}
        onAddPart={addPart}
        onOpenUpload={view === 'dest' ? openMappingUpload : openUpload}
        onExport={view === 'dest' ? exportMapping : exportExcel}
        uploadLocked={view === 'dest' && aq.per !== CUR_PER}
      />
      <ViewTabs view={view} />

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
          dadRun={dadRun}
          onRunCalc={() => runCalc('dad')}
        />
      )}
      {view === 'dest' && <DestMappingTab state={state} />}

      {modal === 'part' && <PartModal state={state} />}
      {modal === 'upload' && <UploadModal state={state} />}
      {modal === 'upload-mapping' && <MappingUploadModal state={state} />}
      {modal === 'history' && <HistoryModal state={state} />}
      {notice && <SaveSuccessModal notice={notice} onClose={dismissNotice} />}
    </AppShell>
  );
}
