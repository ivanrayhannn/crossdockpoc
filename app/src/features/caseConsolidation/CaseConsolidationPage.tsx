import 'bootstrap/dist/css/bootstrap.min.css';
import './bootstrap-overrides.css';
import { DeliveryPlanTab } from './components/DeliveryPlanTab';
import { AsnDraftTab } from './components/AsnDraftTab';
import { OptionsBar } from './components/OptionsBar';
import { VisualSimulationTab } from './components/VisualSimulationTab';
import { useCaseSimulation } from './useCaseSimulation';
import type { ViewKey } from './useCaseSimulation';

const VIEW_TABS: [ViewKey, string][] = [
  ['dp', 'Delivery Plan'],
  ['sim', 'Visual simulation'],
];

export function CaseConsolidationPage() {
  const state = useCaseSimulation();
  const { view, setView } = state;

  return (
    <div className="bs4" style={{ background: 'transparent' }}>
      <div style={{ padding: '18px 24px 8px' }}>
        <h1 className="h3 mb-1">Case consolidation simulation</h1>
        <p className="small text-muted mb-2" style={{ maxWidth: 1000 }}>
          Customer orders released on an order date are always a multiple of pcs/case per destination, and a case never mixes destinations. Every day one supplier PO is
          released automatically with PO Date = Order Date + 1, holding all destinations. A PO can take at most Max Case/Day cases. Cases that do not fit wait in a FIFO
          backlog and go into the next PO first, so they use up the quota of later orders. Changing Max Case/Day does not add cases to a PO that is already released; it
          only applies to the next PO. Whatever is left at the end is shown as remaining and can be handled with a manual PO.
        </p>

        <OptionsBar state={state} />

        <ul className="nav nav-tabs mt-2 mb-2" role="tablist">
          {VIEW_TABS.map(([k, label]) => (
            <li key={k} className="nav-item">
              <a
                href="#"
                role="tab"
                aria-selected={view === k}
                className={`nav-link${view === k ? ' active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  setView(k);
                }}
              >
                {label}
              </a>
            </li>
          ))}
        </ul>

        {view === 'sim' ? <VisualSimulationTab state={state} /> : view === 'asn' ? <AsnDraftTab state={state} /> : <DeliveryPlanTab state={state} />}
      </div>
    </div>
  );
}
