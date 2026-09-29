import type { ReactNode } from 'react';
import type { RouteKey } from '../../routes';
import { Footer } from './Footer';
import { Sidebar } from './Sidebar';
import { TopHeader } from './TopHeader';

interface AppShellProps {
  activeItem: string;
  onNavigate: (route: RouteKey) => void;
  breadcrumb: ReactNode;
  children: ReactNode;
}

export function AppShell({ activeItem, onNavigate, breadcrumb, children }: AppShellProps) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#eef1f5' }}>
      <Sidebar activeItem={activeItem} onNavigate={onNavigate} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        <TopHeader />
        {breadcrumb}
        <main style={{ flex: 1, background: '#eef1f5', paddingBottom: 8 }}>{children}</main>
        <Footer />
      </div>
    </div>
  );
}
