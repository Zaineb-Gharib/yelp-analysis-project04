export type View = 'chat' | 'explorer' | 'dashboard';

export type StreamlitArgs = {
  activeView?: View;
  messages?: unknown[];
  schemaTables?: unknown[];
  quickQueries?: unknown[];
  dashboardStats?: unknown;
  dashboardDetailsLoading?: boolean;
  isLoading?: boolean;
  frameHeight?: number;
  prompt?: string;
  theme?: string;
};

export type RenderEventDetail = {
  args?: StreamlitArgs;
  disabled?: boolean;
  theme?: unknown;
};

export const RENDER_EVENT = 'streamlit:render';

const COMPONENT_READY = 'streamlit:componentReady';
const SET_COMPONENT_VALUE = 'streamlit:setComponentValue';
const SET_FRAME_HEIGHT = 'streamlit:setFrameHeight';
const API_VERSION = 1;

export function getViewportHeight(fallback?: number) {
  try {
    const parentHeight = window.parent?.document?.documentElement?.clientHeight;
    if (typeof parentHeight === 'number' && parentHeight > 0) {
      return Math.max(320, Math.round(parentHeight));
    }
  } catch {
    // Ignore cross-frame access issues and fall back to local viewport metrics.
  }

  if (typeof window.visualViewport?.height === 'number' && window.visualViewport.height > 0) {
    return Math.max(320, Math.round(window.visualViewport.height));
  }

  if (typeof window.innerHeight === 'number' && window.innerHeight > 0) {
    return Math.max(320, Math.round(window.innerHeight));
  }

  if (typeof fallback === 'number' && fallback > 0) {
    return Math.max(320, Math.round(fallback));
  }

  return Math.max(320, document.body.scrollHeight);
}

export function setComponentReady() {
  window.parent.postMessage(
    {
      isStreamlitMessage: true,
      type: COMPONENT_READY,
      apiVersion: API_VERSION,
    },
    '*',
  );
}

export function setComponentValue(value: unknown) {
  window.parent.postMessage(
    {
      isStreamlitMessage: true,
      type: SET_COMPONENT_VALUE,
      value,
      dataType: 'json',
    },
    '*',
  );
}

export function setFrameHeight(height?: number) {
  const nextHeight =
    typeof height === 'number' && height > 0
      ? Math.round(height)
      : getViewportHeight(document.body.scrollHeight);
  window.parent.postMessage(
    {
      isStreamlitMessage: true,
      type: SET_FRAME_HEIGHT,
      height: nextHeight,
    },
    '*',
  );
}

export function addRenderListener(
  handler: (detail: RenderEventDetail) => void,
): () => void {
  const onMessage = (event: MessageEvent) => {
    const data = event.data;
    if (!data || data.type !== RENDER_EVENT) {
      return;
    }
    handler({
      args: data.args ?? {},
      disabled: Boolean(data.disabled),
      theme: data.theme,
    });
  };

  window.addEventListener('message', onMessage);
  return () => {
    window.removeEventListener('message', onMessage);
  };
}
