import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * A standalone simulation page (static file in public/simulations, deployed with the app) shown inside the app shell.
 * The iframe is sized to its content so the shell's page scroll is used instead of a second, nested scrollbar.
 */
export function SimulationFrame({ file, title }: { file: string; title: string }) {
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
      src={`${import.meta.env.BASE_URL}simulations/${file}`}
      title={title}
      style={{ display: 'block', width: '100%', height, border: 0, background: '#fff' }}
    />
  );
}
