export type LaneKey = 'GT' | 'NB' | 'PR' | 'DS' | 'SP' | 'AP';

export interface BpfStep {
  id: string;
  lane: string;
  band: string;
  slot: number;
  fn: string;
  title: string;
  read: string[];
  write: string[];
  ab: string[];
  next: string[];
}

export interface BpfFlow {
  id: string;
  title: string;
  desc: string;
  lanes: string[];
  bands: { id: string; label: string; slots: number }[];
  steps: BpfStep[];
}

export interface BpfAbnormality {
  id: string;
  flow: string;
  step: string;
  fn: string;
  condition: string;
  detection: string;
  system: string;
  pic: string;
  action: string;
}

export interface BpfData {
  lanes: Record<string, string>;
  flows: BpfFlow[];
  abnormality: BpfAbnormality[];
}
