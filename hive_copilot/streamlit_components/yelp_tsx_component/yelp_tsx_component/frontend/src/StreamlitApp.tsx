import React, { useEffect, useMemo, useState } from 'react';
import EmbeddedApp from './EmbeddedApp';
import {
  addRenderListener,
  getViewportHeight,
  setComponentReady,
  setComponentValue,
  setFrameHeight,
  type StreamlitArgs,
  type View,
} from './streamlitBridge';

const DEFAULT_ARGS: Required<StreamlitArgs> = {
  activeView: 'chat',
  messages: [],
  schemaTables: [],
  quickQueries: [],
  dashboardStats: null,
  dashboardDetailsLoading: false,
  isLoading: false,
  frameHeight: 0,
  prompt: '',
  theme: 'light',
};

export default function StreamlitApp() {
  const [args, setArgs] = useState<Required<StreamlitArgs>>(DEFAULT_ARGS);
  const [disabled, setDisabled] = useState(false);

  useEffect(() => {
    const removeListener = addRenderListener((detail) => {
      const nextArgs = detail.args ?? {};
      setArgs({
        activeView: (nextArgs.activeView ?? DEFAULT_ARGS.activeView) as View,
        messages: Array.isArray(nextArgs.messages) ? nextArgs.messages : [],
        schemaTables: Array.isArray(nextArgs.schemaTables)
          ? nextArgs.schemaTables
          : [],
        quickQueries: Array.isArray(nextArgs.quickQueries)
          ? nextArgs.quickQueries
          : [],
        dashboardStats: nextArgs.dashboardStats ?? null,
        dashboardDetailsLoading: Boolean(nextArgs.dashboardDetailsLoading),
        isLoading: Boolean(nextArgs.isLoading),
        frameHeight:
          typeof nextArgs.frameHeight === 'number'
            ? nextArgs.frameHeight
            : DEFAULT_ARGS.frameHeight,
        prompt: nextArgs.prompt ?? '',
        theme: nextArgs.theme ?? DEFAULT_ARGS.theme,
      });
      setDisabled(Boolean(detail.disabled));
    });

    setComponentReady();
    setFrameHeight(getViewportHeight(DEFAULT_ARGS.frameHeight));

    const handleResize = () => {
      setFrameHeight(getViewportHeight(args.frameHeight));
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      removeListener();
    };
  }, [args.frameHeight]);

  const frameHeight = useMemo(
    () => getViewportHeight(args.frameHeight),
    [args.frameHeight],
  );

  useEffect(() => {
    window.requestAnimationFrame(() => {
      setFrameHeight(frameHeight);
    });
  }, [frameHeight, args.activeView, args.messages.length]);

  return (
    <EmbeddedApp
      activeView={args.activeView as View}
      messages={args.messages}
      schemaTables={args.schemaTables}
      quickQueries={args.quickQueries}
      dashboardStats={args.dashboardStats}
      dashboardDetailsLoading={args.dashboardDetailsLoading}
      isLoading={args.isLoading}
      prompt={args.prompt}
      theme={args.theme}
      disabled={disabled}
      onValueChange={setComponentValue}
    />
  );
}
