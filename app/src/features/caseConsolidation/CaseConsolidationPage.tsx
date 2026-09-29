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
    <div style={{ padding: '18px 24px 28px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22 }}>Case consolidation simulation</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3, maxWidth: 820, textWrap: 'pretty' }}>
          Customer orders released on an order date are always a multiple of pcs/case per destination, and a case never mixes destinations. Every day one supplier PO is
          released automatically with PO Date = Order Date + 1, holding all destinations. A PO can take at most Max Case/Day cases. Cases that do not fit wait in a FIFO
          backlog and go into the next PO first, so they use up the quota of later orders. Changing Max Case/Day does not add cases to a PO that is already released; it
          only applies to the next PO. Whatever is left at the end is shown as remaining and can be handled with a manual PO.
        </div>
      </div>

      <OptionsBar state={state} />

      <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--color-divider)' }}>
        {VIEW_TABS.map(([k, label]) => (
          <button
            key={k}
            onClick={() => setView(k)}
            style={{
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              flex: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 13,
              fontWeight: 600,
              padding: '9px 14px',
              marginBottom: -1,
              background: 'transparent',
              border: 0,
              borderBottom: `2px solid ${view === k ? 'var(--color-accent)' : 'transparent'}`,
              color: view === k ? 'var(--color-accent-800)' : 'var(--color-neutral-700)',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {view === 'sim' ? <VisualSimulationTab state={state} /> : view === 'asn' ? <AsnDraftTab state={state} /> : <DeliveryPlanTab state={state} />}
    </div>
  );
}
