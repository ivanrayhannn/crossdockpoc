import type { ReactNode } from 'react';
import { BreadcrumbBar } from './BreadcrumbBar';
import { Footer } from './Footer';
import { Sidebar } from './Sidebar';
import { TopHeader } from './TopHeader';

interface AppShellProps {
  roleLabel: string;
  onSwitchRole?: () => void;
  children: ReactNode;
}

export function AppShell({ roleLabel, onSwitchRole, children }: AppShellProps) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#eef1f5' }}>
      <Sidebar />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        <TopHeader />
        <BreadcrumbBar roleLabel={roleLabel} onSwitchRole={onSwitchRole} />
        <main style={{ flex: 1, background: '#eef1f5', paddingBottom: 8 }}>{children}</main>
        <Footer />
      </div>
    </div>
  );
}
