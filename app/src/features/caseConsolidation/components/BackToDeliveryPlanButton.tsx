export function BackToDeliveryPlanButton({ onClick }: { onClick: () => void }) {
  return (
    <button type="button" className="btn btn-outline-secondary btn-sm mr-3" onClick={onClick}>
      <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="15 6 9 12 15 18" />
      </svg>
      Back to Delivery Plan
    </button>
  );
}
