/* Mock route master for the ASN draft: which rits (trips) run on a delivery date and which
   route each one belongs to. Sunday has no route, Saturday has a single rit. */

export interface Rit {
  no: string;
  route: string;
}

const RITS: Rit[] = [
  { no: 'Rit 1', route: 'SD01' },
  { no: 'Rit 2', route: 'SD02' },
  { no: 'Rit 3', route: 'SD03' },
];

export function ritsFor(deliveryDate: string): Rit[] {
  if (!deliveryDate) return [];
  const day = new Date(`${deliveryDate}T00:00:00Z`).getUTCDay();
  if (day === 0) return [];
  return day === 6 ? RITS.slice(0, 1) : RITS;
}
