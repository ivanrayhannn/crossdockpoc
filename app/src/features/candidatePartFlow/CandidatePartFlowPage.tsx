import { useCallback, useEffect, useRef, useState } from 'react';

/** Standalone simulation page, shipped as a static file so it is deployed with the app (public/simulations). */
const SIMULATION_URL = `${import.meta.env.BASE_URL}simulations/candidate-part-flow.html?v=8`;

/**
 * Shows the Master Candidate Part batch-flow simulation (calculation batch, Part List upload, Mapping upload,
 * Excel export) inside the app shell. The iframe is sized to its content so the shell's page scroll is used
 * instead of a second, nested scrollbar.
 */
export function CandidatePartFlowPage() {
  const frameRef = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(1200);

  const fit = useCallback(() => {
    const doc = frameRef.current?.contentDocument;
    if (!doc) return;
    setHeight(Math.ceil(doc.documentElement.scrollHeight));
  }, []);

  useEffect(() => {
    const frame = frameRef.current;
    let observer: ResizeObserver | undefined;
    const onLoad = () => {
      fit();
      const doc = frame?.contentDocument;
      if (doc?.body) {
        observer = new ResizeObserver(fit);
        observer.observe(doc.body);
      }
    };
    frame?.addEventListener('load', onLoad);
    if (frame?.contentDocument?.readyState === 'complete') onLoad();
    return () => {
      frame?.removeEventListener('load', onLoad);
      observer?.disconnect();
    };
  }, [fit]);

  return (
    <iframe
      ref={frameRef}
      src={SIMULATION_URL}
      title="Candidate Part batch flow simulation"
      style={{ display: 'block', width: '100%', height, border: 0, background: '#eef1f5' }}
    />
  );
}
