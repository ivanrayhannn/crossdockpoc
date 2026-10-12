import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import './batch-process.css';

type ProcessTab = 'overview' | 'upload' | 'rpa' | 'retrieve' | 'candidates';
type JobType = 'Upload' | 'RPA outbound' | 'Data retrieval';
type JobStatus = 'Completed' | 'Running' | 'Completed with warnings';

interface BatchJob {
  id: string;
  type: JobType;
  source: string;
  target: string;
  startedAt: string;
  status: JobStatus;
  records: number;
  result: string;
}

interface Candidate {
  id: string;
  partNo: string;
  partName: string;
  supplier: string;
  source: string;
  retrievedAt: string;
  status: string;
}

interface SourcePart {
  id: string;
  partNo: string;
  partName: string;
  supplier: string;
  destination: string;
  status: 'Ready' | 'Duplicate' | 'Needs data';
}

interface ActiveRun {
  id: string;
  kind: 'Upload' | 'RPA outbound';
  step: number;
  fileName?: string;
}

const PROCESS_TABS: { id: ProcessTab; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'upload', label: 'Upload batch' },
  { id: 'rpa', label: 'RPA outbound' },
  { id: 'retrieve', label: 'Data retrieval' },
  { id: 'candidates', label: 'Part Master Candidate' },
];

const UPLOAD_STEPS = ['File received', 'Rows validated', 'Candidate records created'];
const RPA_STEPS = ['Connecting to SAP S/4HANA', 'Signing in to target system', 'Sending part master records', 'Confirming transfer results'];

const INITIAL_JOBS: BatchJob[] = [
  { id: 'BCH-20261006-0042', type: 'RPA outbound', source: 'Crossdock Master Setting', target: 'SAP S/4HANA', startedAt: '06 Oct 2026, 09:42', status: 'Completed with warnings', records: 16, result: '14 sent · 2 need review' },
  { id: 'BCH-20261006-0041', type: 'Data retrieval', source: 'SAP S/4HANA', target: 'Part Master Candidate', startedAt: '06 Oct 2026, 09:18', status: 'Completed', records: 24, result: '24 candidates retrieved' },
  { id: 'BCH-20261006-0040', type: 'Upload', source: 'part_master_oct.xlsx', target: 'Part Master Candidate', startedAt: '06 Oct 2026, 08:56', status: 'Completed', records: 148, result: '142 imported · 6 rejected' },
  { id: 'BCH-20261005-0039', type: 'RPA outbound', source: 'Crossdock Master Setting', target: 'Supplier Portal', startedAt: '05 Oct 2026, 16:21', status: 'Completed', records: 32, result: '32 sent successfully' },
];

const INITIAL_CANDIDATES: Candidate[] = [
  { id: 'CND-000184', partNo: 'NP-44820-01', partName: 'Front brake pad assembly', supplier: 'Nusa Parts Indonesia', source: 'SAP S/4HANA', retrievedAt: '06 Oct 2026, 09:18', status: 'Pending review' },
  { id: 'CND-000183', partNo: 'NP-44819-02', partName: 'Rear brake disc', supplier: 'Nusa Parts Indonesia', source: 'SAP S/4HANA', retrievedAt: '06 Oct 2026, 09:18', status: 'Pending review' },
  { id: 'CND-000182', partNo: 'NP-77103-11', partName: 'Clutch plate kit', supplier: 'Daya Motor Works', source: 'Upload batch', retrievedAt: '06 Oct 2026, 08:56', status: 'Pending review' },
];

const INITIAL_SOURCE_PARTS: SourcePart[] = [
  { id: 'src-1', partNo: 'NP-99031-01', partName: 'Brake caliper assembly', supplier: 'Nusa Parts Indonesia', destination: 'JKT · Bekasi', status: 'Ready' },
  { id: 'src-2', partNo: 'NP-99031-02', partName: 'Brake piston set', supplier: 'Nusa Parts Indonesia', destination: 'JKT · Bekasi', status: 'Ready' },
  { id: 'src-3', partNo: 'NP-44820-01', partName: 'Front brake pad assembly', supplier: 'Nusa Parts Indonesia', destination: 'JKT · Bekasi', status: 'Duplicate' },
  { id: 'src-4', partNo: 'DM-77103-11', partName: 'Clutch plate kit', supplier: 'Daya Motor Works', destination: 'SBY · Waru', status: 'Ready' },
  { id: 'src-5', partNo: 'DM-77104-10', partName: 'Clutch release bearing', supplier: 'Daya Motor Works', destination: 'SBY · Waru', status: 'Needs data' },
];

function formatNow(date = new Date()) {
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Jakarta',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).format(date).replace(',', '');
}

function statusClass(status: JobStatus | SourcePart['status'] | string) {
  if (status === 'Completed') return 'bp-status bp-status--success';
  if (status === 'Completed with warnings' || status === 'Duplicate' || status === 'Needs data') return 'bp-status bp-status--warning';
  if (status === 'Running') return 'bp-status bp-status--running';
  return 'bp-status bp-status--neutral';
}

function Icon({ name, size = 18 }: { name: 'upload' | 'refresh' | 'download' | 'check' | 'arrow' | 'clock' | 'database' | 'external' | 'file' | 'play' | 'layers'; size?: number }) {
  const paths: Record<typeof name, ReactNode> = {
    upload: <><path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" /></>,
    refresh: <><path d="M20 7v5h-5" /><path d="M4 17v-5h5" /><path d="M5.6 9A7 7 0 0 1 18 6l2 6M4 12l2 6a7 7 0 0 0 12.4-3" /></>,
    download: <><path d="M12 4v12" /><path d="m7 11 5 5 5-5" /><path d="M5 20h14" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    database: <><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" /></>,
    external: <><path d="M14 3h7v7" /><path d="m21 3-9 9" /><path d="M19 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h6" /></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6M8 13h8M8 17h8" /></>,
    play: <><path d="m8 5 12 7-12 7z" /></>,
    layers: <><path d="m12 3 9 5-9 5-9-5 9-5z" /><path d="m3 12 9 5 9-5M3 16l9 5 9-5" /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

export function BatchProcessPage() {
  const [tab, setTab] = useState<ProcessTab>('overview');
  const [jobs, setJobs] = useState(INITIAL_JOBS);
  const [candidates, setCandidates] = useState(INITIAL_CANDIDATES);
  const [sourceParts, setSourceParts] = useState(INITIAL_SOURCE_PARTS);
  const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeRun, setActiveRun] = useState<ActiveRun | null>(null);
  const [message, setMessage] = useState('');
  const [candidateSearch, setCandidateSearch] = useState('');
  const [candidatePage, setCandidatePage] = useState(1);

  const readySourceParts = sourceParts.filter((part) => part.status === 'Ready');
  const matchingCandidates = useMemo(() => {
    const query = candidateSearch.trim().toLowerCase();
    if (!query) return candidates;
    return candidates.filter((candidate) => [candidate.partNo, candidate.partName, candidate.supplier, candidate.source].some((value) => value.toLowerCase().includes(query)));
  }, [candidateSearch, candidates]);
  const visibleCandidates = useMemo(() => matchingCandidates.slice((candidatePage - 1) * 10, candidatePage * 10), [candidatePage, matchingCandidates]);

  useEffect(() => {
    if (!activeRun) return undefined;
    const stepCount = activeRun.kind === 'Upload' ? UPLOAD_STEPS.length : RPA_STEPS.length;
    const timeout = window.setTimeout(() => {
      if (activeRun.step < stepCount - 1) {
        setActiveRun((current) => current?.id === activeRun.id ? { ...current, step: current.step + 1 } : current);
        return;
      }

      const isUpload = activeRun.kind === 'Upload';
      const total = isUpload ? 148 : 16;
      const accepted = isUpload ? 142 : 14;
      const rejected = total - accepted;
      if (isUpload) {
        const importedAt = formatNow();
        const importedCandidates = Array.from({ length: accepted }, (_, index): Candidate => ({
          id: `CND-${String(Date.now()).slice(-6)}-${String(index + 1).padStart(3, '0')}`,
          partNo: `UPL-${String(index + 1).padStart(5, '0')}`,
          partName: `Uploaded sample part ${String(index + 1).padStart(3, '0')}`,
          supplier: index % 2 === 0 ? 'Nusa Parts Indonesia' : 'Daya Motor Works',
          source: 'Upload batch',
          retrievedAt: importedAt,
          status: 'Pending review',
        }));
        setCandidates((current) => [...importedCandidates, ...current]);
      }
      setJobs((current) => current.map((job) => job.id === activeRun.id ? {
        ...job,
        status: rejected ? 'Completed with warnings' : 'Completed',
        records: total,
        result: isUpload ? `${accepted} imported · ${rejected} rejected` : `${accepted} sent · ${rejected} need review`,
      } : job));
      setActiveRun(null);
      setMessage(isUpload
        ? `${accepted} sample rows added to Part Master Candidate. ${rejected} rows need correction.`
        : `${accepted} part records synchronized to SAP S/4HANA. ${rejected} records need review.`);
    }, 780);
    return () => window.clearTimeout(timeout);
  }, [activeRun]);

  function beginRun(kind: ActiveRun['kind'], fileName?: string) {
    if (activeRun) return;
    const id = `BCH-${Date.now()}`;
    setJobs((current) => [{
      id,
      type: kind,
      source: kind === 'Upload' ? fileName ?? 'part_master_sample.xlsx' : 'Crossdock Master Setting',
      target: kind === 'Upload' ? 'Part Master Candidate' : 'SAP S/4HANA',
      startedAt: formatNow(),
      status: 'Running',
      records: 0,
      result: 'Process started',
    }, ...current]);
    setActiveRun({ id, kind, step: 0, fileName });
    setMessage('');
  }

  function retrieveSelected() {
    const selected = sourceParts.filter((part) => selectedSourceIds.includes(part.id) && part.status === 'Ready');
    if (!selected.length) return;
    const retrievedAt = formatNow();
    const added: Candidate[] = selected.map((part, index) => ({
      id: `CND-${String(Date.now() + index).slice(-6)}`,
      partNo: part.partNo,
      partName: part.partName,
      supplier: part.supplier,
      source: 'SAP S/4HANA',
      retrievedAt,
      status: 'Pending review',
    }));
    setCandidates((current) => [...added, ...current]);
    setSourceParts((current) => current.map((part) => selectedSourceIds.includes(part.id) ? { ...part, status: 'Duplicate' } : part));
    setSelectedSourceIds([]);
    const jobId = `BCH-${Date.now()}`;
    setJobs((current) => [{
      id: jobId,
      type: 'Data retrieval',
      source: 'SAP S/4HANA',
      target: 'Part Master Candidate',
      startedAt: retrievedAt,
      status: 'Completed',
      records: selected.length,
      result: `${selected.length} candidates retrieved`,
    }, ...current]);
    setMessage(`${selected.length} records retrieved to Part Master Candidate.`);
    setTab('candidates');
    setCandidatePage(1);
  }

  function handleFile(file?: File) {
    if (!file) return;
    const isSupported = /\.(xlsx|xls|csv)$/i.test(file.name);
    if (!isSupported) {
      setMessage('Choose an Excel or CSV file to continue.');
      return;
    }
    setSelectedFile(file);
    setMessage('');
  }

  const runningSteps = activeRun?.kind === 'Upload' ? UPLOAD_STEPS : RPA_STEPS;

  return (
    <div className="batch-page">
      <div className="bp-page-heading">
        <div>
          <div className="bp-eyebrow">COMMON / INTEGRATION OPERATIONS</div>
          <h1>Batch Process Simulation</h1>
          <p>Upload files, synchronize master data, and track records moving between systems.</p>
        </div>
        <span className="bp-prototype-pill"><span /> Prototype environment</span>
      </div>

      <div className="bp-tabs" role="tablist" aria-label="Batch process views">
        {PROCESS_TABS.map((item) => (
          <button key={item.id} className={`bp-tab ${tab === item.id ? 'is-active' : ''}`} role="tab" aria-selected={tab === item.id} onClick={() => { setTab(item.id); setMessage(''); }}>
            {item.label}{item.id === 'candidates' && <span className="bp-tab-count">{candidates.length}</span>}
          </button>
        ))}
      </div>

      {message && <div className={`bp-message ${message.startsWith('Choose') ? 'bp-message--error' : ''}`} role="status"><span className="bp-message-icon">{message.startsWith('Choose') ? '!' : '✓'}</span>{message}<button onClick={() => setMessage('')} aria-label="Dismiss message">×</button></div>}

      {tab === 'overview' && <OverviewTab jobs={jobs} candidateCount={candidates.length} setTab={setTab} />}
      {tab === 'upload' && (
        <UploadTab
          selectedFile={selectedFile}
          activeRun={activeRun?.kind === 'Upload' ? activeRun : null}
          onFile={handleFile}
          onStart={() => beginRun('Upload', selectedFile?.name)}
        />
      )}
      {tab === 'rpa' && <RpaTab activeRun={activeRun?.kind === 'RPA outbound' ? activeRun : null} onStart={() => beginRun('RPA outbound')} />}
      {tab === 'retrieve' && (
          <RetrieveTab
          sourceParts={sourceParts}
          selectedIds={selectedSourceIds}
          active={Boolean(activeRun)}
          onToggle={(id) => setSelectedSourceIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])}
          onToggleAll={() => setSelectedSourceIds(selectedSourceIds.length === readySourceParts.length ? [] : readySourceParts.map((part) => part.id))}
          onRetrieve={retrieveSelected}
          onRefresh={() => setMessage('Source preview refreshed from SAP S/4HANA sample data.')}
        />
      )}
      {tab === 'candidates' && <CandidatesTab candidates={visibleCandidates} total={candidates.length} matchingCount={matchingCandidates.length} page={candidatePage} pageCount={Math.max(1, Math.ceil(matchingCandidates.length / 10))} onPage={setCandidatePage} query={candidateSearch} onQuery={(query) => { setCandidateSearch(query); setCandidatePage(1); }} />}

      {activeRun && (
        <div className="bp-running-banner" role="status">
          <span className="bp-spinner" />
          <div className="bp-running-copy"><strong>{activeRun.kind} simulation in progress</strong><span>{runningSteps[activeRun.step]}</span></div>
          <span className="bp-running-id">{activeRun.id}</span>
        </div>
      )}
    </div>
  );
}

function OverviewTab({ jobs, candidateCount, setTab }: { jobs: BatchJob[]; candidateCount: number; setTab: (tab: ProcessTab) => void }) {
  const successful = jobs.filter((job) => job.status === 'Completed').length;
  const warnings = jobs.filter((job) => job.status === 'Completed with warnings').length;
  return (
    <div className="bp-content">
      <section className="bp-flow-card">
        <div className="bp-section-heading"><div><h2>Master data flows</h2><p>Run each path independently to move records between the upload, RPA, and candidate queues.</p></div><span className="bp-live-label"><span /> SIMULATION</span></div>
        <div className="bp-flow-lanes">
          <FlowLane label="FILE UPLOAD" source="Excel or CSV" sourceHint="Batch file" sourceIcon="upload" process="Validate and stage rows" target="Part Master Candidate" targetHint={`${candidateCount} awaiting review`} targetIcon="database" onClick={() => setTab('upload')} />
          <FlowLane label="RPA OUTBOUND" source="Crossdock Master" sourceHint="Approved part data" sourceIcon="layers" process="Bot transfers records" target="SAP S/4HANA" targetHint="External ERP" targetIcon="external" onClick={() => setTab('rpa')} />
          <FlowLane label="DATA RETRIEVAL" source="SAP S/4HANA" sourceHint="External ERP" sourceIcon="external" process="Review and retrieve" target="Part Master Candidate" targetHint="Candidate queue" targetIcon="database" onClick={() => setTab('retrieve')} />
        </div>
        <div className="bp-flow-footer"><span><i className="bp-dot bp-dot--blue" /> Outbound: NSP → SAP</span><span><i className="bp-dot bp-dot--green" /> Inbound: SAP → Candidate queue</span><button className="bp-flow-link" onClick={() => setTab('candidates')}>Open candidate queue <Icon name="arrow" size={14} /></button></div>
      </section>

      <div className="bp-overview-grid">
        <section className="bp-panel bp-quick-panel">
          <div className="bp-section-heading"><div><h2>Start a process</h2><p>Run a sample flow to see each batch update.</p></div></div>
          <button className="bp-action-card" onClick={() => setTab('upload')}><span className="bp-action-icon bp-action-icon--blue"><Icon name="upload" /></span><span><strong>Upload a batch file</strong><small>Validate rows and create candidate records</small></span><Icon name="arrow" size={16} /></button>
          <button className="bp-action-card" onClick={() => setTab('rpa')}><span className="bp-action-icon bp-action-icon--purple"><Icon name="refresh" /></span><span><strong>Run RPA outbound</strong><small>Send approved master data to SAP</small></span><Icon name="arrow" size={16} /></button>
          <button className="bp-action-card" onClick={() => setTab('retrieve')}><span className="bp-action-icon bp-action-icon--green"><Icon name="download" /></span><span><strong>Retrieve external data</strong><small>Bring SAP records into the candidate queue</small></span><Icon name="arrow" size={16} /></button>
        </section>

        <section className="bp-panel bp-activity-panel">
          <div className="bp-section-heading"><div><h2>Recent batch activity</h2><p>Latest upload and system-to-system runs.</p></div><button className="bp-text-button" onClick={() => setTab('upload')}>Run a batch <Icon name="arrow" size={14} /></button></div>
          <div className="bp-mini-stats"><div><span>Recent jobs</span><strong>{jobs.length}</strong></div><div><span>Completed</span><strong>{successful}</strong></div><div><span>Needs attention</span><strong className={warnings ? 'bp-warn-text' : ''}>{warnings}</strong></div></div>
          <JobTable jobs={jobs.slice(0, 4)} compact />
        </section>
      </div>
    </div>
  );
}

function FlowLane({ label, source, sourceHint, sourceIcon, process, target, targetHint, targetIcon, onClick }: { label: string; source: string; sourceHint: string; sourceIcon: 'upload' | 'layers' | 'external' | 'database'; process: string; target: string; targetHint: string; targetIcon: 'upload' | 'layers' | 'external' | 'database'; onClick: () => void }) {
  return (
    <button className="bp-flow-lane" onClick={onClick}>
      <span className="bp-lane-label">{label}</span>
      <span className="bp-lane-node"><i className="bp-lane-icon"><Icon name={sourceIcon} size={16} /></i><span><strong>{source}</strong><small>{sourceHint}</small></span></span>
      <span className="bp-lane-process"><i /><span>{process}</span><i /></span>
      <span className="bp-lane-node"><i className="bp-lane-icon"><Icon name={targetIcon} size={16} /></i><span><strong>{target}</strong><small>{targetHint}</small></span></span>
      <span className="bp-lane-open"><Icon name="arrow" size={15} /></span>
    </button>
  );
}

function UploadTab({ selectedFile, activeRun, onFile, onStart }: { selectedFile: File | null; activeRun: ActiveRun | null; onFile: (file?: File) => void; onStart: () => void }) {
  const currentStep = activeRun?.step ?? -1;
  return (
    <div className="bp-content bp-process-layout">
      <section className="bp-panel bp-process-main">
        <div className="bp-section-heading"><div><div className="bp-step-kicker">PROCESS 01 <span>·</span> FILE INGESTION</div><h2>Upload master data</h2><p>Submit a file to simulate validation and loading into the candidate queue.</p></div><span className="bp-system-tag">Destination <strong>Part Master Candidate</strong></span></div>
        <label className="bp-dropzone" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); onFile(event.dataTransfer.files[0]); }}>
          <input type="file" accept=".xlsx,.xls,.csv" onChange={(event) => onFile(event.target.files?.[0])} />
          <span className="bp-upload-icon"><Icon name="upload" size={22} /></span>
          <strong>{selectedFile ? selectedFile.name : 'Drop your batch file here'}</strong>
          <span>{selectedFile ? 'Ready for a sample validation run' : 'or browse from your computer'}</span>
          <small>Excel or CSV · .xlsx, .xls, .csv</small>
          {selectedFile && <em>{(selectedFile.size / 1024).toFixed(0)} KB · File selected</em>}
        </label>
        <div className="bp-demo-note"><span className="bp-note-info">i</span><span><strong>Prototype behavior</strong> The selected file name is recorded. Validation results use 148 sample rows; file contents are not uploaded to a server.</span></div>
        <div className="bp-process-actions"><button className="btn btn-secondary" onClick={() => onFile(new File(['part_no,part_name,supplier\nNP-99031-01,Brake caliper,Nusa Parts'], 'part_master_sample.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }))}>Use sample file</button><button className="btn btn-primary" disabled={!selectedFile || Boolean(activeRun)} onClick={onStart}><Icon name="play" size={15} /> Validate and upload</button></div>
      </section>
      <section className="bp-panel bp-process-side">
        <div className="bp-section-heading"><div><h2>Batch steps</h2><p>What happens after upload.</p></div></div>
        <StepList steps={UPLOAD_STEPS} activeStep={currentStep} complete={Boolean(activeRun && currentStep === UPLOAD_STEPS.length - 1)} />
        <div className="bp-side-divider" />
        <div className="bp-side-metric"><span>Previous sample</span><strong>142 <small>rows imported</small></strong><em>6 rows held for correction</em></div>
      </section>
    </div>
  );
}

function RpaTab({ activeRun, onStart }: { activeRun: ActiveRun | null; onStart: () => void }) {
  const currentStep = activeRun?.step ?? -1;
  return (
    <div className="bp-content bp-process-layout">
      <section className="bp-panel bp-process-main">
        <div className="bp-section-heading"><div><div className="bp-step-kicker">PROCESS 02 <span>·</span> OUTBOUND AUTOMATION</div><h2>RPA system transfer</h2><p>Simulate a robot session that sends master records to an external system.</p></div><span className="bp-status bp-status--neutral">Ready to run</span></div>
        <div className="bp-integration-map">
          <div className="bp-endpoint"><span className="bp-endpoint-symbol bp-endpoint-symbol--nsp">N</span><div><small>SOURCE SYSTEM</small><strong>New Service Part System</strong><span>Crossdock Master Setting</span></div><i className="bp-endpoint-ready" /></div>
          <div className="bp-integration-middle"><div className="bp-integration-line"><span /><i /><span /></div><small>RPA BOT · OUTBOUND</small></div>
          <div className="bp-endpoint"><span className="bp-endpoint-symbol bp-endpoint-symbol--sap">S</span><div><small>TARGET SYSTEM</small><strong>SAP S/4HANA</strong><span>External ERP · Production</span></div><Icon name="external" size={16} /></div>
        </div>
        <div className="bp-rpa-summary"><div><span>Records in queue</span><strong>16 <small>part records</small></strong></div><div><span>Last successful run</span><strong>06 Oct 2026 <small>09:42 WIB</small></strong></div><div><span>Automation account</span><strong>NSP_RPA_01 <small>Service user</small></strong></div></div>
        <div className="bp-demo-note"><span className="bp-note-info">i</span><span><strong>Prototype behavior</strong> No connection to SAP is made. A timed bot run updates the job log with sample transfer results.</span></div>
        <div className="bp-process-actions"><span className="bp-manual-run"><Icon name="clock" size={14} /> Manual trigger · no schedule</span><button className="btn btn-primary" disabled={Boolean(activeRun)} onClick={onStart}><Icon name="play" size={15} /> Run RPA simulation</button></div>
      </section>
      <section className="bp-panel bp-process-side">
        <div className="bp-section-heading"><div><h2>Bot activity</h2><p>{activeRun ? 'Current simulated session' : 'Session sequence'}</p></div></div>
        <StepList steps={RPA_STEPS} activeStep={currentStep} complete={Boolean(activeRun && currentStep === RPA_STEPS.length - 1)} />
        <div className="bp-side-divider" />
        <div className="bp-side-metric"><span>Latest result</span><strong>14 <small>sent to SAP</small></strong><em>2 records need review</em></div>
      </section>
    </div>
  );
}

function StepList({ steps, activeStep, complete }: { steps: string[]; activeStep: number; complete: boolean }) {
  return <div className="bp-step-list">{steps.map((step, index) => {
    const isDone = complete || index < activeStep;
    const isActive = !complete && index === activeStep;
    return <div key={step} className={`bp-step ${isDone ? 'is-done' : ''} ${isActive ? 'is-active' : ''}`}><span className="bp-step-marker">{isDone ? <Icon name="check" size={13} /> : isActive ? <i /> : String(index + 1).padStart(2, '0')}</span><span>{step}</span></div>;
  })}</div>;
}

function RetrieveTab({ sourceParts, selectedIds, active, onToggle, onToggleAll, onRetrieve, onRefresh }: { sourceParts: SourcePart[]; selectedIds: string[]; active: boolean; onToggle: (id: string) => void; onToggleAll: () => void; onRetrieve: () => void; onRefresh: () => void }) {
  const readyCount = sourceParts.filter((part) => part.status === 'Ready').length;
  return (
    <div className="bp-content">
      <section className="bp-panel bp-retrieve-panel">
        <div className="bp-section-heading"><div><div className="bp-step-kicker">PROCESS 03 <span>·</span> INBOUND DATA</div><h2>Retrieve from external system</h2><p>Review source records before copying them into Part Master Candidate.</p></div><button className="bp-btn-refresh" disabled={active} onClick={onRefresh}><Icon name="refresh" size={15} /> Refresh source preview</button></div>
        <div className="bp-source-banner"><span className="bp-source-logo">S</span><div><strong>SAP S/4HANA</strong><small>Mock connector · Last checked 06 Oct 2026, 09:18 WIB</small></div><span className="bp-connection-state"><i /> Connection simulated</span></div>
        <div className="bp-source-toolbar"><div><strong>{readyCount} records ready</strong><span> · {sourceParts.length} returned by the source system</span></div><button className="bp-text-button" onClick={onToggleAll}>{selectedIds.length === readyCount ? 'Clear selection' : 'Select all ready'}</button></div>
        <div className="bp-table-wrap"><table className="bp-table"><thead><tr><th className="bp-check-cell"><input type="checkbox" aria-label="Select all ready records" checked={readyCount > 0 && selectedIds.length === readyCount} onChange={onToggleAll} /></th><th>Part number</th><th>Part name</th><th>Supplier</th><th>Destination</th><th>Eligibility</th></tr></thead><tbody>{sourceParts.map((part) => <tr key={part.id}><td className="bp-check-cell"><input type="checkbox" aria-label={`Select ${part.partNo}`} checked={selectedIds.includes(part.id)} disabled={part.status !== 'Ready'} onChange={() => onToggle(part.id)} /></td><td className="bp-mono">{part.partNo}</td><td className="bp-part-name">{part.partName}</td><td>{part.supplier}</td><td>{part.destination}</td><td><span className={statusClass(part.status)}>{part.status}</span></td></tr>)}</tbody></table></div>
        <div className="bp-retrieve-footer"><span><strong>{selectedIds.length}</strong> selected for retrieval <span className="bp-muted">· Existing part numbers and incomplete records are held back.</span></span><button className="btn btn-primary" disabled={!selectedIds.length || active} onClick={onRetrieve}><Icon name="download" size={15} /> Retrieve selected <span className="bp-button-count">{selectedIds.length}</span></button></div>
      </section>
    </div>
  );
}

function CandidatesTab({ candidates, total, matchingCount, page, pageCount, onPage, query, onQuery }: { candidates: Candidate[]; total: number; matchingCount: number; page: number; pageCount: number; onPage: (page: number) => void; query: string; onQuery: (query: string) => void }) {
  return (
    <div className="bp-content">
      <section className="bp-panel bp-candidate-panel">
        <div className="bp-section-heading"><div><div className="bp-step-kicker">MASTER DATA WORKSPACE</div><h2>Part Master Candidate</h2><p>New records from uploads and external systems wait here for review.</p></div><span className="bp-queue-count"><strong>{total}</strong><span>pending review</span></span></div>
        <div className="bp-candidate-toolbar"><label className="bp-search"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></svg><input value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Search part number, name, supplier" /></label><span className="bp-candidate-total">Showing {candidates.length} of {matchingCount} matches · {total} total</span></div>
        {candidates.length ? <div className="bp-table-wrap"><table className="bp-table bp-candidate-table"><thead><tr><th>Candidate ID</th><th>Part number</th><th>Part name</th><th>Supplier</th><th>Source</th><th>Retrieved</th><th>Status</th></tr></thead><tbody>{candidates.map((candidate) => <tr key={candidate.id}><td className="bp-mono">{candidate.id}</td><td className="bp-mono">{candidate.partNo}</td><td className="bp-part-name">{candidate.partName}</td><td>{candidate.supplier}</td><td><span className="bp-source-cell"><i className={candidate.source === 'Upload batch' ? 'bp-source-icon bp-source-icon--upload' : 'bp-source-icon'}>{candidate.source === 'Upload batch' ? 'U' : 'S'}</i>{candidate.source}</span></td><td>{candidate.retrievedAt}</td><td><span className="bp-status bp-status--review">Pending review</span></td></tr>)}</tbody></table></div> : <div className="bp-empty-state"><span className="bp-empty-icon"><Icon name="layers" size={24} /></span><strong>No matching candidates</strong><span>Try a different part number, name, or supplier.</span></div>}
        <div className="bp-candidate-footer"><span><Icon name="clock" size={14} /> Candidate records are not added to the master until they are reviewed.</span><span className="bp-pagination"><button disabled={page <= 1} onClick={() => onPage(page - 1)} aria-label="Previous candidate page">‹</button>{page} <small>/ {pageCount}</small><button disabled={page >= pageCount} onClick={() => onPage(page + 1)} aria-label="Next candidate page">›</button></span></div>
      </section>
    </div>
  );
}

function JobTable({ jobs, compact = false }: { jobs: BatchJob[]; compact?: boolean }) {
  return <div className={`bp-table-wrap ${compact ? 'bp-table-wrap--compact' : ''}`}><table className="bp-table bp-job-table"><thead><tr><th>Batch ID</th><th>Process</th><th>Source → target</th><th>Started</th><th>Status</th><th>Records</th><th>Result</th></tr></thead><tbody>{jobs.map((job) => <tr key={job.id}><td className="bp-mono">{job.id}</td><td><span className={`bp-job-type bp-job-type--${job.type === 'Upload' ? 'upload' : job.type === 'RPA outbound' ? 'rpa' : 'retrieve'}`}>{job.type}</span></td><td>{job.source} <span className="bp-table-arrow">→</span> {job.target}</td><td>{job.startedAt}</td><td><span className={statusClass(job.status)}>{job.status}</span></td><td>{job.records || '—'}</td><td>{job.result}</td></tr>)}</tbody></table></div>;
}
