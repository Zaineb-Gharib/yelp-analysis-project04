import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Database,
  MessageSquare,
  Code,
  Table as TableIcon,
  BarChart3,
  Send,
  Loader2,
  ChevronRight,
  History,
  Trash2,
  Sparkles,
  Users,
  LayoutDashboard,
  Star,
} from 'lucide-react';
import {
  Bar,
  Doughnut,
  Line,
} from 'react-chartjs-2';
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import usStatesSvg from './assets/us-states.svg?raw';

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  Title,
);

type View = 'chat' | 'explorer' | 'dashboard';

type ResultRow = Record<string, unknown>;

type VizConfig = {
  type: 'bar' | 'pie' | 'line' | 'none';
  xAxis?: string;
  yAxis?: string;
  title?: string;
};

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  results?: ResultRow[];
  vizConfig?: VizConfig;
  error?: string | null;
};

type SchemaTable = {
  name: string;
  columns: string[];
};

type QuickQuery = {
  label: string;
  prompt: string;
};

type DashboardCategory = {
  categories: string;
  count: string | number;
};

type TopRatedBusiness = {
  name: string;
  stars: string | number;
  categories: string;
};

type CategoryRating = {
  categories: string;
  avg: string | number;
};

type ReviewTrend = {
  month: string;
  count: string | number;
};

type SentimentDatum = {
  name: string;
  value: number;
  color?: string;
};

type DemographicDatum = {
  age: string;
  count: number;
};

type BusinessLocation = {
  city: string;
  lat: string | number;
  lon: string | number;
  count: string | number;
};

type StateBusinessCount = {
  state: string;
  count: string | number;
};

type CityCount = {
  city: string;
  count: string | number;
};

type RatingBucket = {
  rating: string | number;
  count: string | number;
};

type DashboardStatus = {
  level: string;
  message: string;
};

type DashboardStats = {
  totalBusinesses: string | number;
  totalReviews: string | number;
  activeUsers: string | number;
  avgRating: string | number;
  topCategories: DashboardCategory[];
  topRated: TopRatedBusiness[];
  ratingByCategory: CategoryRating[];
  reviewTrends: ReviewTrend[];
  sentiment: SentimentDatum[];
  demographics: DemographicDatum[];
  businessLocations: BusinessLocation[];
  stateBusinessCounts: StateBusinessCount[];
  topStates: StateBusinessCount[];
  topCities: CityCount[];
  ratingDistribution: RatingBucket[];
  dataFreshness: string;
  snapshotGeneratedAt: string;
  status: DashboardStatus | null;
  detailsLoaded: boolean;
  detailsRequested: boolean;
};

type ComponentEventPayload =
  | { type: 'submit_prompt'; prompt: string }
  | { type: 'set_view'; view: View }
  | { type: 'reset_session' }
  | { type: 'refresh_dashboard' }
  | { type: 'load_dashboard_details' };

type ComponentEvent =
  | ({ type: 'submit_prompt'; prompt: string } & { eventId: string })
  | ({ type: 'set_view'; view: View } & { eventId: string })
  | ({ type: 'reset_session' } & { eventId: string })
  | ({ type: 'refresh_dashboard' } & { eventId: string })
  | ({ type: 'load_dashboard_details' } & { eventId: string });

type Props = {
  activeView: View;
  messages: unknown[];
  schemaTables: unknown[];
  quickQueries: unknown[];
  dashboardStats: unknown;
  dashboardDetailsLoading: boolean;
  isLoading: boolean;
  prompt: string;
  theme: string;
  disabled: boolean;
  onValueChange: (value: ComponentEvent) => void;
};

const COLORS = ['#d97706', '#92400e', '#451a03', '#f59e0b', '#78350f'];

function buildEvent(payload: ComponentEventPayload): ComponentEvent {
  return {
    ...payload,
    eventId: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  } as ComponentEvent;
}

function normalizeMessages(input: unknown[]): Message[] {
  return input.map((entry, index) => {
    const message = entry as Partial<Message>;
    return {
      id: message.id ?? `message-${index}`,
      role: message.role === 'user' ? 'user' : 'assistant',
      content: message.content ?? '',
      sql: message.sql,
      results: Array.isArray(message.results) ? message.results : [],
      vizConfig: message.vizConfig ?? { type: 'none' },
      error: message.error ?? null,
    };
  });
}

function normalizeSchemaTables(input: unknown[]): SchemaTable[] {
  return input.map((entry) => {
    const table = entry as Partial<SchemaTable>;
    return {
      name: table.name ?? '',
      columns: Array.isArray(table.columns)
        ? table.columns.map((column) => String(column))
        : [],
    };
  });
}

function normalizeQuickQueries(input: unknown[]): QuickQuery[] {
  return input.map((entry) => {
    const query = entry as Partial<QuickQuery>;
    return {
      label: query.label ?? '',
      prompt: query.prompt ?? '',
    };
  });
}

function normalizeDashboardStats(input: unknown): DashboardStats | null {
  if (!input || typeof input !== 'object') {
    return null;
  }

  const stats = input as Partial<DashboardStats>;
  return {
    totalBusinesses: stats.totalBusinesses ?? 0,
    totalReviews: stats.totalReviews ?? 0,
    activeUsers: stats.activeUsers ?? 0,
    avgRating: stats.avgRating ?? 0,
    topCategories: Array.isArray(stats.topCategories) ? stats.topCategories : [],
    topRated: Array.isArray(stats.topRated) ? stats.topRated : [],
    ratingByCategory: Array.isArray(stats.ratingByCategory)
      ? stats.ratingByCategory
      : [],
    reviewTrends: Array.isArray(stats.reviewTrends) ? stats.reviewTrends : [],
    sentiment: Array.isArray(stats.sentiment) ? stats.sentiment : [],
    demographics: Array.isArray(stats.demographics) ? stats.demographics : [],
    businessLocations: Array.isArray(stats.businessLocations)
      ? stats.businessLocations
      : [],
    stateBusinessCounts: Array.isArray(stats.stateBusinessCounts)
      ? stats.stateBusinessCounts
      : [],
    topStates: Array.isArray(stats.topStates) ? stats.topStates : [],
    topCities: Array.isArray(stats.topCities) ? stats.topCities : [],
    ratingDistribution: Array.isArray(stats.ratingDistribution)
      ? stats.ratingDistribution
      : [],
    dataFreshness: typeof stats.dataFreshness === 'string' ? stats.dataFreshness : '',
    snapshotGeneratedAt:
      typeof stats.snapshotGeneratedAt === 'string' ? stats.snapshotGeneratedAt : '',
    status:
      stats.status && typeof stats.status === 'object'
        ? (stats.status as DashboardStatus)
        : null,
    detailsLoaded: Boolean(stats.detailsLoaded),
    detailsRequested: Boolean(stats.detailsRequested),
  };
}

export default function EmbeddedApp({
  activeView,
  messages: rawMessages,
  schemaTables: rawSchemaTables,
  quickQueries: rawQuickQueries,
  dashboardStats: rawDashboardStats,
  dashboardDetailsLoading,
  isLoading,
  prompt,
  theme,
  disabled,
  onValueChange,
}: Props) {
  const [input, setInput] = useState(prompt);
  const [refreshRequested, setRefreshRequested] = useState(false);
  const [showAllQuickQueries, setShowAllQuickQueries] = useState(false);
  const [showAllSchemaTables, setShowAllSchemaTables] = useState(false);
  const [pendingPromptPreview, setPendingPromptPreview] = useState<string | null>(null);
  const [pendingMessageCount, setPendingMessageCount] = useState<number | null>(null);
  const [pendingStartedAt, setPendingStartedAt] = useState<number | null>(null);
  const [loadingTick, setLoadingTick] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const dashboardDetailsRequestedRef = useRef(false);
  const lastSnapshotRef = useRef('');

  const messages = useMemo(() => normalizeMessages(rawMessages), [rawMessages]);
  const schemaTables = useMemo(
    () => normalizeSchemaTables(rawSchemaTables),
    [rawSchemaTables],
  );
  const quickQueries = useMemo(
    () => normalizeQuickQueries(rawQuickQueries),
    [rawQuickQueries],
  );
  const visibleQuickQueries = useMemo(
    () => (showAllQuickQueries ? quickQueries : quickQueries.slice(0, 4)),
    [quickQueries, showAllQuickQueries],
  );
  const visibleSchemaTables = useMemo(
    () => (showAllSchemaTables ? schemaTables : schemaTables.slice(0, 3)),
    [schemaTables, showAllSchemaTables],
  );
  const dashboardStats = useMemo(
    () => normalizeDashboardStats(rawDashboardStats),
    [rawDashboardStats],
  );

  const lastAssistantMessage = useMemo(
    () =>
      [...messages]
        .reverse()
        .find(
          (message) =>
            message.role === 'assistant' && (message.results?.length ?? 0) > 0,
        ),
    [messages],
  );

  const explorerEnabled = Boolean(lastAssistantMessage);

  useEffect(() => {
    if (prompt) {
      setInput(prompt);
    }
  }, [prompt]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  useEffect(() => {
    if (pendingPromptPreview !== null && pendingMessageCount !== null && messages.length > pendingMessageCount) {
      setPendingPromptPreview(null);
      setPendingMessageCount(null);
      setPendingStartedAt(null);
    }
  }, [messages.length, pendingMessageCount, pendingPromptPreview]);

  useEffect(() => {
    if (pendingPromptPreview === null) {
      return;
    }
    const timer = window.setInterval(() => {
      setLoadingTick((value) => value + 1);
    }, 1200);
    return () => window.clearInterval(timer);
  }, [pendingPromptPreview]);

  useEffect(() => {
    const snapshot = dashboardStats?.snapshotGeneratedAt ?? '';
    if (snapshot && snapshot !== lastSnapshotRef.current) {
      lastSnapshotRef.current = snapshot;
      setRefreshRequested(false);
    }
  }, [dashboardStats?.snapshotGeneratedAt]);

  const emit = (event: ComponentEventPayload) => {
    onValueChange(buildEvent(event));
  };

  useEffect(() => {
    if (!dashboardStats) {
      dashboardDetailsRequestedRef.current = false;
      return;
    }
    if (activeView !== 'dashboard') {
      return;
    }
    if (dashboardStats.detailsLoaded || dashboardStats.detailsRequested) {
      dashboardDetailsRequestedRef.current = true;
      return;
    }
    if (!dashboardDetailsRequestedRef.current) {
      dashboardDetailsRequestedRef.current = true;
      emit({ type: 'load_dashboard_details' });
    }
  }, [activeView, dashboardStats]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const cleanPrompt = input.trim();
    if (!cleanPrompt || disabled) {
      return;
    }
    setPendingPromptPreview(cleanPrompt);
    setPendingMessageCount(messages.length);
    setPendingStartedAt(Date.now());
    setInput('');
    emit({ type: 'submit_prompt', prompt: cleanPrompt });
  };

  const submitPrompt = (promptText: string) => {
    const cleanPrompt = promptText.trim();
    if (!cleanPrompt || disabled) {
      return;
    }
    setPendingPromptPreview(cleanPrompt);
    setPendingMessageCount(messages.length);
    setPendingStartedAt(Date.now());
    emit({ type: 'submit_prompt', prompt: cleanPrompt });
  };

  const loadingCopy = useMemo(() => {
    if (pendingStartedAt === null) {
      return {
        title: 'Drafting Hive SQL...',
        detail: 'Understanding your question and preparing a safe query.',
      };
    }

    const elapsedSec = Math.max(Math.floor((Date.now() - pendingStartedAt) / 1000), 0);
    if (elapsedSec < 4) {
      return {
        title: 'Drafting Hive SQL...',
        detail: 'Understanding your question and preparing a safe query.',
      };
    }
    if (elapsedSec < 9) {
      return {
        title: 'Analyzing Yelp data...',
        detail: 'Matching your request to the warehouse tables and filters.',
      };
    }
    if (elapsedSec < 18) {
      return {
        title: 'Executing Hive query...',
        detail: 'Waiting for Hive and YARN to process the result set.',
      };
    }
    return {
      title: 'Still working on your query...',
      detail: 'Large Hive jobs can take a while on this machine. The result will appear here when ready.',
    };
  }, [pendingStartedAt, loadingTick]);

  return (
    <div
      className="flex h-screen bg-claude-bg text-claude-text font-sans overflow-hidden"
      data-theme={theme}
    >
      <aside className="w-64 border-r border-black/5 flex flex-col bg-claude-sidebar z-20">
        <div className="p-6 border-b border-black/5">
          <div className="flex items-center gap-2 mb-1">
            <Database className="w-5 h-5 text-claude-accent" />
            <h1 className="text-lg font-bold tracking-tight">Hive Copilot</h1>
          </div>
          <p className="text-[10px] font-sans opacity-40 uppercase tracking-widest font-bold">
            Warehouse SQL Assistant
          </p>
        </div>

        <div className="p-4 space-y-2">
          <TabButton
            active={activeView === 'chat'}
            onClick={() => emit({ type: 'set_view', view: 'chat' })}
            icon={<MessageSquare className="w-4 h-4" />}
            label="Conversational Chat"
          />
          <TabButton
            active={activeView === 'explorer'}
            onClick={() => emit({ type: 'set_view', view: 'explorer' })}
            icon={<BarChart3 className="w-4 h-4" />}
            label="Data Explorer"
            disabled={!explorerEnabled}
          />
          <TabButton
            active={activeView === 'dashboard'}
            onClick={() => emit({ type: 'set_view', view: 'dashboard' })}
            icon={<LayoutDashboard className="w-4 h-4" />}
            label="Hive Dashboard"
          />
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-6">
          <div>
            <h2 className="text-[11px] font-serif italic opacity-50 uppercase tracking-wider mb-3 px-2">
              Quick Queries
            </h2>
            <div className="space-y-1">
              {visibleQuickQueries.map((query) => (
                <ExampleQuery
                  key={query.label}
                  text={query.label}
                  onClick={() => submitPrompt(query.prompt)}
                />
              ))}
            </div>
            {quickQueries.length > 4 && (
              <button
                type="button"
                onClick={() => setShowAllQuickQueries((current) => !current)}
                className="mt-3 rounded-xl px-3 py-2 text-[11px] font-bold uppercase tracking-[0.14em] text-claude-muted hover:bg-black/5 hover:text-claude-text transition-colors cursor-pointer"
              >
                {showAllQuickQueries ? 'Show Less' : `Show More (${quickQueries.length - 4})`}
              </button>
            )}
          </div>

          <div>
            <h2 className="text-[11px] font-serif italic opacity-50 uppercase tracking-wider mb-3 px-2">
              Dataset Schema
            </h2>
            <div className="space-y-2">
              {visibleSchemaTables.map((table) => (
                <SchemaItem
                  key={table.name}
                  name={table.name}
                  columns={table.columns}
                />
              ))}
            </div>
            {schemaTables.length > 3 && (
              <button
                type="button"
                onClick={() => setShowAllSchemaTables((current) => !current)}
                className="mt-3 rounded-xl px-3 py-2 text-[11px] font-bold uppercase tracking-[0.14em] text-claude-muted hover:bg-black/5 hover:text-claude-text transition-colors cursor-pointer"
              >
                {showAllSchemaTables ? 'Show Less' : `Show More (${schemaTables.length - 3})`}
              </button>
            )}
          </div>
        </nav>

        <div className="p-4 border-t border-black/5">
          <button
            onClick={() => emit({ type: 'reset_session' })}
            className="w-full flex items-center justify-center gap-2 py-2 text-xs font-medium text-claude-muted hover:text-claude-text hover:bg-black/5 transition-all rounded-xl cursor-pointer"
            type="button"
          >
            <Trash2 className="w-4 h-4" />
            Reset Session
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col relative bg-claude-bg">
        {activeView === 'chat' && (
          <div className="flex-1 flex flex-col h-full items-center">
              <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto w-full max-w-3xl p-8 space-y-10"
              >
                {messages.length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto opacity-40">
                    <Sparkles className="w-12 h-12 mb-6 text-claude-accent" />
                    <h2 className="text-2xl font-serif font-bold mb-4">
                      How can I help you explore Hive data today?
                    </h2>
                    <p className="text-sm leading-relaxed">
                      Ask analytical questions about warehouse tables, review facts, or
                      user activity. Hive Copilot will draft SQL and show visual
                      summaries.
                    </p>
                  </div>
                )}

                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} onOpenExplorer={() => emit({ type: 'set_view', view: 'explorer' })} />
                ))}

                {pendingPromptPreview && (
                  <>
                    <ChatMessage
                      message={{
                        id: 'pending-user-message',
                        role: 'user',
                        content: pendingPromptPreview,
                        results: [],
                        vizConfig: { type: 'none' },
                        error: null,
                      }}
                      onOpenExplorer={() => emit({ type: 'set_view', view: 'explorer' })}
                    />
                    <div className="flex justify-start">
                      <div className="max-w-[85%] flex gap-4">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-claude-accent/10 text-claude-accent">
                          <Sparkles className="w-4 h-4" />
                        </div>
                        <div className="p-1">
                          <div className="rounded-2xl border border-black/5 bg-claude-sidebar/55 px-4 py-3">
                            <div className="flex items-center gap-3">
                              <Loader2 className="w-4 h-4 animate-spin text-claude-accent" />
                              <span className="text-sm font-serif italic text-claude-text/80">
                                {loadingCopy.title}
                              </span>
                            </div>
                            <p className="mt-2 pl-7 text-xs text-claude-muted">
                              {loadingCopy.detail}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>

              <div className="w-full max-w-3xl p-8 bg-claude-bg">
                <form onSubmit={handleSubmit} className="relative">
                  <input
                    type="text"
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    placeholder="Ask anything about your Hive warehouse..."
                    className="w-full bg-claude-sidebar border border-black/10 p-4 pr-16 rounded-2xl focus:outline-none focus:ring-2 focus:ring-claude-accent/20 transition-all text-claude-text placeholder:text-claude-muted/50"
                    disabled={disabled}
                  />
                  <button
                    type="submit"
                    disabled={disabled || !input.trim()}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-claude-text text-claude-bg rounded-xl hover:opacity-90 transition-all disabled:opacity-30 cursor-pointer"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </form>
                <p className="text-[10px] text-center mt-4 text-claude-muted opacity-50">
                  Hive Copilot can make mistakes. Verify important information.
                </p>
              </div>
          </div>
        )}

        {activeView === 'explorer' && (
          <div className="flex-1 flex flex-col h-full overflow-hidden">
              <div className="p-6 border-b border-black/5 bg-claude-bg flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold tracking-tight">Data Explorer</h2>
                  <p className="text-xs text-claude-muted font-sans uppercase tracking-widest mt-1">
                    Inspecting latest query results
                  </p>
                </div>
                <button
                  onClick={() => emit({ type: 'set_view', view: 'chat' })}
                  className="px-4 py-2 text-xs font-bold text-claude-muted border border-black/10 rounded-xl hover:bg-black/5 transition-all cursor-pointer"
                  type="button"
                >
                  Back to Chat
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-8 space-y-8">
                {lastAssistantMessage ? (
                  <div className="max-w-5xl mx-auto space-y-10">
                    <section>
                      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-claude-muted mb-4">
                        <Code className="w-4 h-4" />
                        Generated SQL
                      </div>
                      <div className="bg-claude-text rounded-2xl p-6 shadow-sm">
                        <pre className="text-claude-bg font-mono text-sm overflow-x-auto">
                          <code>{lastAssistantMessage.sql}</code>
                        </pre>
                      </div>
                    </section>

                    {lastAssistantMessage.vizConfig &&
                      lastAssistantMessage.vizConfig.type !== 'none' && (
                        <section>
                          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-claude-muted mb-4">
                            <BarChart3 className="w-4 h-4" />
                            Visualization
                          </div>
                          <div className="bg-white border border-black/5 rounded-2xl p-6 shadow-sm">
                            <div className="mb-6">
                              <h3 className="text-lg font-serif text-claude-text">
                                {formatChartTitle(lastAssistantMessage.vizConfig)}
                              </h3>
                              <p className="mt-2 text-[11px] text-claude-muted uppercase tracking-[0.14em]">
                                {describeChart(lastAssistantMessage.vizConfig)}
                              </p>
                            </div>
                            <ResultChart
                              results={lastAssistantMessage.results ?? []}
                              vizConfig={lastAssistantMessage.vizConfig}
                            />
                          </div>
                        </section>
                      )}

                    <section>
                      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-claude-muted mb-4">
                        <TableIcon className="w-4 h-4" />
                        Raw Results
                      </div>
                      <div className="bg-white border border-black/5 rounded-2xl overflow-hidden shadow-sm">
                        <div className="overflow-x-auto">
                          <table className="w-full text-left border-collapse">
                            <thead>
                              <tr className="bg-claude-sidebar text-claude-text">
                                {Object.keys(lastAssistantMessage.results?.[0] ?? {}).map(
                                  (key) => (
                                    <th
                                      key={key}
                                      className="p-4 text-[10px] font-bold uppercase tracking-widest"
                                    >
                                      {key}
                                    </th>
                                  ),
                                )}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-black/5">
                              {(lastAssistantMessage.results ?? []).map((row, index) => (
                                <tr
                                  key={`${lastAssistantMessage.id}-${index}`}
                                  className="hover:bg-claude-accent/5 transition-colors"
                                >
                                  {Object.values(row).map((value, cellIndex) => (
                                    <td
                                      key={`${lastAssistantMessage.id}-${index}-${cellIndex}`}
                                      className="p-4 text-sm text-claude-text"
                                    >
                                      {typeof value === 'object'
                                        ? JSON.stringify(value)
                                        : String(value)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </section>
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center opacity-30">
                    <History className="w-12 h-12 mb-4" />
                    <p className="font-serif italic">No query results to display yet.</p>
                  </div>
                )}
              </div>
          </div>
        )}

        {activeView === 'dashboard' && (
          <div className="flex-1 flex flex-col h-full overflow-hidden bg-claude-bg">
              <div className="p-6 border-b border-black/5 bg-claude-bg flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-claude-text">
                    Hive Analytics Dashboard
                  </h2>
                  <p className="text-xs text-claude-muted font-sans uppercase tracking-widest mt-1">
                    Aggregated Warehouse Insights
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => {
                      setRefreshRequested(true);
                      emit({ type: 'refresh_dashboard' });
                    }}
                    className="inline-flex items-center gap-2 rounded-xl border border-black/10 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-claude-muted hover:text-claude-text hover:bg-black/5 transition-colors cursor-pointer"
                    type="button"
                  >
                    <History className="w-4 h-4" />
                    <span>{refreshRequested ? 'Refreshing...' : 'Refresh Real Data'}</span>
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-8 space-y-8">
                {dashboardStats ? (
                  <div className="max-w-7xl mx-auto space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      <KPICard label="Total Businesses" value={dashboardStats.totalBusinesses} />
                      <KPICard label="Total Reviews" value={dashboardStats.totalReviews} />
                      <KPICard label="Active Users" value={dashboardStats.activeUsers} />
                      <KPICard label="Avg Rating" value={dashboardStats.avgRating} />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      <div className="lg:col-span-2">
                        <DashboardCard
                          title="USA Business Footprint"
                          subtitle={dashboardStats.status?.message || 'Hover a state to see its business count'}
                        >
                          <HeroMapCard states={dashboardStats.stateBusinessCounts} />
                        </DashboardCard>
                      </div>

                      <div className="space-y-8">
                        <DashboardCard title="Top Business Categories">
                          <CompactCategoryList categories={dashboardStats.topCategories} />
                        </DashboardCard>

                        <DashboardCard title="Highest Rated Businesses">
                          <TopBusinessRail businesses={dashboardStats.topRated} />
                        </DashboardCard>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      <DashboardCard title="Top States">
                        {dashboardStats.topStates.length > 0 ? (
                          <SimpleHorizontalBarChart
                            data={dashboardStats.topStates}
                            labelKey="state"
                            valueKey="count"
                            height={220}
                          />
                        ) : (
                          <DashboardPlaceholder
                            loading={false}
                            message="State rankings will appear when the snapshot returns state counts."
                          />
                        )}
                      </DashboardCard>

                      <DashboardCard title="Rating Distribution">
                        {dashboardStats.ratingDistribution.length > 0 ? (
                          <RatingDistributionChart
                            data={dashboardStats.ratingDistribution}
                            labelKey="rating"
                            valueKey="count"
                            height={220}
                          />
                        ) : (
                          <DashboardPlaceholder
                            loading={false}
                            message="Rating buckets are part of the summary snapshot and will appear here."
                          />
                        )}
                      </DashboardCard>

                      <DashboardCard title="Top Cities">
                        {dashboardStats.topCities.length > 0 ? (
                          <SimpleHorizontalBarChart
                            data={dashboardStats.topCities}
                            labelKey="city"
                            valueKey="count"
                            height={220}
                          />
                        ) : (
                          <DashboardPlaceholder
                            loading={false}
                            message="City rankings will appear when the snapshot returns city counts."
                          />
                        )}
                      </DashboardCard>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      <div className="lg:col-span-2">
                        <DashboardCard
                          title="Review Volume Trends"
                          subtitle={
                            dashboardStats.detailsLoaded
                              ? 'Loaded progressively after first paint'
                              : 'Optional secondary detail'
                          }
                        >
                          {dashboardStats.reviewTrends.length > 0 ? (
                            <div className="h-[240px]">
                              <SimpleLineAreaChart
                                data={dashboardStats.reviewTrends}
                                xKey="month"
                                yKey="count"
                                height={240}
                              />
                            </div>
                          ) : (
                            <DashboardPlaceholder
                              loading={dashboardDetailsLoading}
                              message="Review trends are secondary and load only after the summary snapshot is on screen."
                            />
                          )}
                        </DashboardCard>
                      </div>

                      <div className="space-y-8">
                        <DashboardCard title="Rating By Category">
                          {dashboardStats.ratingByCategory.length > 0 ? (
                            <div className="h-[220px]">
                              <SimpleHorizontalBarChart
                                data={dashboardStats.ratingByCategory}
                                labelKey="categories"
                                valueKey="avg"
                                height={220}
                              />
                            </div>
                          ) : (
                            <DashboardPlaceholder
                              loading={dashboardDetailsLoading}
                              message="Category ratings are deferred to keep the summary fast."
                            />
                          )}
                        </DashboardCard>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-claude-muted/20">
                    <Loader2 className="w-12 h-12 animate-spin mb-4" />
                    <p className="font-serif italic">Loading dashboard statistics...</p>
                  </div>
                )}
              </div>
          </div>
        )}
      </main>
    </div>
  );
}

function ResultChart({
  results,
  vizConfig,
}: {
  results: ResultRow[];
  vizConfig: VizConfig;
}) {
  if (!vizConfig.xAxis || !vizConfig.yAxis) {
    return null;
  }

  const chartModel = buildChartJsModel(results, vizConfig);
  if (!chartModel) {
    return null;
  }

  if (vizConfig.type === 'bar') {
    return (
      <div className="h-[360px] rounded-2xl border border-black/5 bg-[linear-gradient(180deg,rgba(249,248,246,0.96),rgba(255,255,255,1))] p-5">
        <Bar data={chartModel.data} options={chartModel.options} />
      </div>
    );
  }

  if (vizConfig.type === 'pie') {
    return (
      <div className="h-[360px] rounded-2xl border border-black/5 bg-[linear-gradient(180deg,rgba(249,248,246,0.96),rgba(255,255,255,1))] p-5">
        <Doughnut data={chartModel.data} options={chartModel.options} />
      </div>
    );
  }

  return (
    <div className="h-[360px] rounded-2xl border border-black/5 bg-[linear-gradient(180deg,rgba(249,248,246,0.96),rgba(255,255,255,1))] p-5">
      <Line data={chartModel.data} options={chartModel.options} />
    </div>
  );
}

function buildChartJsModel(results: ResultRow[], vizConfig: VizConfig) {
  const xAxis = vizConfig.xAxis;
  const yAxis = vizConfig.yAxis;
  if (!xAxis || !yAxis) {
    return null;
  }

  const rows = results.slice(0, vizConfig.type === 'pie' ? 6 : 10);
  const labels = rows.map((row) => toText(row[xAxis]));
  const values = rows.map((row) => toNumber(row[yAxis]));
  const horizontal = vizConfig.type === 'bar' && shouldUseHorizontalBarChart(results, xAxis, yAxis);
  const prettyXAxis = prettifyFieldName(xAxis);
  const prettyYAxis = prettifyFieldName(yAxis);
  const prettyTitle = formatChartTitle(vizConfig);

  if (vizConfig.type === 'pie') {
    return {
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: ['#d97706', '#f59e0b', '#fbbf24', '#ea580c', '#92400e', '#451a03'],
            borderColor: '#fff',
            borderWidth: 3,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '58%',
        plugins: {
          legend: {
            position: 'bottom' as const,
            labels: {
              color: '#6b7280',
              boxWidth: 12,
              padding: 16,
            },
          },
          title: {
            display: false,
            text: prettyTitle,
          },
          tooltip: {
            callbacks: {
              label: (context: any) => `${context.label}: ${formatMetric(context.parsed)}`,
            },
          },
        },
      },
    };
  }

  if (vizConfig.type === 'line') {
    return {
      data: {
        labels,
        datasets: [
          {
            label: prettyYAxis,
            data: values,
            borderColor: '#d97706',
            backgroundColor: 'rgba(217,119,6,0.15)',
            pointBackgroundColor: '#c2410c',
            pointBorderColor: '#fff',
            pointRadius: 4,
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: (context: any) => `${prettyYAxis}: ${formatMetric(context.parsed.y)}`,
            },
          },
        },
        scales: {
          x: {
            ticks: {
              color: '#6b7280',
            },
            grid: {
              display: false,
            },
          },
          y: {
            ticks: {
              color: '#6b7280',
            },
            grid: {
              color: 'rgba(0,0,0,0.06)',
            },
          },
        },
      },
    };
  }

  return {
    data: {
      labels,
      datasets: [
        {
          label: prettyYAxis,
          data: values,
          backgroundColor: horizontal
            ? 'rgba(217,119,6,0.86)'
            : ['#f59e0b', '#fbbf24', '#ea580c', '#d97706', '#c2410c', '#92400e', '#78350f', '#451a03'],
          borderRadius: 12,
          borderSkipped: false,
          maxBarThickness: horizontal ? 28 : 42,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: horizontal ? ('y' as const) : ('x' as const),
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: (context: any) =>
              horizontal
                ? `${prettyYAxis}: ${formatMetric(context.parsed.x)}`
                : `${prettyYAxis}: ${formatMetric(context.parsed.y)}`,
          },
        },
      },
      scales: horizontal
        ? {
            x: {
              ticks: {
                color: '#6b7280',
              },
              grid: {
                color: 'rgba(0,0,0,0.06)',
              },
              title: {
                display: true,
                text: prettyYAxis,
                color: '#6b7280',
              },
            },
            y: {
              ticks: {
                color: '#374151',
                font: {
                  size: 12,
                },
              },
              grid: {
                display: false,
              },
              title: {
                display: true,
                text: prettyXAxis,
                color: '#6b7280',
              },
            },
          }
        : {
            x: {
              ticks: {
                color: '#6b7280',
              },
              grid: {
                display: false,
              },
            },
            y: {
              ticks: {
                color: '#6b7280',
              },
              grid: {
                color: 'rgba(0,0,0,0.06)',
              },
            },
          },
    },
  };
}

function shouldUseHorizontalBarChart(
  results: ResultRow[],
  labelKey: string,
  valueKey: string,
): boolean {
  const sample = results.slice(0, 8);
  const normalizedLabel = labelKey.toLowerCase();
  const normalizedValue = valueKey.toLowerCase();
  const averageLabelLength =
    sample.reduce((total, row) => total + toText(row[labelKey]).length, 0) /
      Math.max(sample.length, 1);

  return (
    sample.length <= 10 &&
    (averageLabelLength > 8 ||
      /city|state|category|categories|name/.test(normalizedLabel) ||
      /count|total|review|business/.test(normalizedValue))
  );
}

function prettifyFieldName(value: string | undefined): string {
  const text = String(value || '').trim();
  if (!text) {
    return '';
  }
  return text
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatChartTitle(vizConfig: VizConfig): string {
  const title = prettifyFieldName(vizConfig.title);
  if (title) {
    return title;
  }
  const yAxis = prettifyFieldName(vizConfig.yAxis);
  return yAxis || 'Query Visualization';
}

function describeChart(vizConfig: VizConfig): string {
  const xAxis = prettifyFieldName(vizConfig.xAxis);
  const yAxis = prettifyFieldName(vizConfig.yAxis);
  const chartType =
    vizConfig.type === 'pie'
      ? 'Donut Chart'
      : vizConfig.type === 'line'
        ? 'Trend Chart'
        : 'Bar Chart';
  if (xAxis && yAxis) {
    return `${chartType} · ${yAxis} by ${xAxis}`;
  }
  return chartType;
}

function ChatMessage({
  message,
  onOpenExplorer,
}: {
  message: Message;
  onOpenExplorer: () => void;
}) {
  const hasResults = Boolean(message.results && message.results.length > 0);
  const previewResults = (message.results || []).slice(0, 5);
  const previewColumns = Object.keys(previewResults[0] || {}).slice(0, 4);

  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
      >
        <div
          className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${message.role === 'user' ? 'bg-claude-text text-claude-bg' : 'bg-claude-accent/10 text-claude-accent'}`}
        >
          {message.role === 'user' ? (
            <Users className="w-4 h-4" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
        </div>
        <div className={`p-1 ${message.role === 'user' ? 'bg-transparent' : ''}`}>
          <div
            className={`${message.role === 'assistant' ? 'font-serif text-lg leading-relaxed text-claude-text' : 'bg-claude-sidebar px-4 py-3 rounded-2xl text-claude-text font-medium'} whitespace-pre-wrap`}
          >
            {message.content}
          </div>
          {message.role === 'assistant' && message.sql && (
            <div className="mt-4 rounded-2xl border border-black/5 bg-[#171717] p-4 shadow-sm">
              <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/55">
                <Code className="w-3.5 h-3.5" />
                Generated SQL
              </div>
              <pre className="overflow-x-auto whitespace-pre-wrap break-words text-xs leading-relaxed text-[#f6f3ed]">
                <code>{message.sql}</code>
              </pre>
            </div>
          )}
          {message.role === 'assistant' &&
            message.vizConfig &&
            message.vizConfig.type !== 'none' &&
            hasResults && (
              <div className="mt-4">
                <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-claude-muted">
                  <BarChart3 className="w-3.5 h-3.5" />
                  Visualization
                </div>
                <ResultChart results={message.results || []} vizConfig={message.vizConfig} />
              </div>
            )}
          {message.role === 'assistant' && hasResults && (
            <div className="mt-4 rounded-2xl border border-black/5 bg-white shadow-sm overflow-hidden">
              <div className="flex items-center justify-between gap-3 border-b border-black/5 px-4 py-3">
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-claude-muted">
                    Result Preview
                  </div>
                  <div className="mt-1 text-xs text-claude-muted">
                    Showing {previewResults.length} of {message.results?.length || 0} rows in chat
                  </div>
                </div>
                <button
                  onClick={onOpenExplorer}
                  className="rounded-xl border border-black/10 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.14em] text-claude-accent hover:bg-claude-accent/5 transition-colors cursor-pointer"
                  type="button"
                >
                  Open Explorer
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-left">
                  <thead className="bg-claude-sidebar/70">
                    <tr>
                      {previewColumns.map((column) => (
                        <th
                          key={`${message.id}-${column}`}
                          className="px-4 py-3 text-[10px] font-bold uppercase tracking-[0.14em] text-claude-muted"
                        >
                          {prettifyFieldName(column)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-black/5">
                    {previewResults.map((row, rowIndex) => (
                      <tr key={`${message.id}-preview-${rowIndex}`} className="bg-white">
                        {previewColumns.map((column) => (
                          <td
                            key={`${message.id}-preview-${rowIndex}-${column}`}
                            className="max-w-[220px] truncate px-4 py-3 text-sm text-claude-text"
                            title={String(row[column] ?? '')}
                          >
                            {String(row[column] ?? '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {message.sql && (
            <button
              onClick={onOpenExplorer}
              className="mt-4 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-claude-accent hover:opacity-80 transition-opacity cursor-pointer"
              type="button"
            >
              <BarChart3 className="w-3 h-3" />
              View Full Results in Explorer
            </button>
          )}
          {message.error && (
            <div className="mt-2 text-xs text-red-500 font-mono bg-red-50 p-2 rounded border border-red-100">
              {message.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CompactCategoryList({
  categories,
}: {
  categories: DashboardCategory[];
}) {
  if (categories.length === 0) {
    return <DashboardPlaceholder loading={false} message="Category summaries are not available yet." />;
  }

  return (
    <div className="space-y-3">
      {categories.slice(0, 5).map((category, index) => (
        <div
          key={`${category.categories}-${index}`}
          className="flex items-center justify-between gap-3 rounded-xl bg-black/5 px-3 py-3"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-claude-accent/10 text-claude-accent flex items-center justify-center text-[10px] font-bold">
              {index + 1}
            </div>
            <span className="text-sm text-claude-text truncate">{category.categories}</span>
          </div>
          <span className="text-xs font-bold text-claude-accent">{category.count}</span>
        </div>
      ))}
    </div>
  );
}

function TopBusinessRail({
  businesses,
}: {
  businesses: TopRatedBusiness[];
}) {
  if (businesses.length === 0) {
    return <DashboardPlaceholder loading={false} message="Top businesses will appear when Hive returns summary rows." />;
  }

  return (
    <div className="space-y-3">
      {businesses.slice(0, 5).map((business, index) => (
        <div
          key={`${business.name}-${index}`}
          className="rounded-xl border border-black/5 bg-black/5 px-3 py-3"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h4 className="truncate text-sm font-bold text-claude-text">{business.name}</h4>
              <p className="mt-1 truncate text-[10px] italic text-claude-muted">
                {business.categories || 'Uncategorized'}
              </p>
            </div>
            <div className="flex items-center gap-1 text-claude-accent shrink-0">
              <Star className="w-3 h-3 fill-current" />
              <span className="text-xs font-bold">{business.stars}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function DashboardPlaceholder({
  loading,
  message,
}: {
  loading: boolean;
  message: string;
}) {
  return (
    <div className="flex min-h-[180px] flex-col items-center justify-center gap-3 rounded-2xl bg-black/5 text-center">
      {loading ? (
        <Loader2 className="w-6 h-6 animate-spin text-claude-accent" />
      ) : (
        <History className="w-6 h-6 text-claude-muted opacity-60" />
      )}
      <p className="max-w-sm text-xs leading-relaxed text-claude-muted">{message}</p>
    </div>
  );
}

function HeroMapCard({
  states,
}: {
  states: StateBusinessCount[];
}) {
  return (
    <div className="rounded-2xl border border-black/5 bg-[radial-gradient(circle_at_top_left,_rgba(217,119,6,0.16),_transparent_45%),linear-gradient(135deg,_rgba(240,239,235,0.85),_rgba(249,248,246,1))] p-4">
      {states.length > 0 ? (
        <USASvgChoropleth states={states} />
      ) : (
        <div className="flex h-[360px] items-center justify-center rounded-xl border border-dashed border-black/10 bg-white/60">
          <p className="max-w-xs text-center text-sm text-claude-muted">
            State-level business counts are unavailable, so the dashboard will fall back to ranked states once summary data returns.
          </p>
        </div>
      )}
    </div>
  );
}

function stateFillColor(count: number, maxCount: number): string {
  if (maxCount <= 0 || count <= 0) {
    return 'rgba(255,255,255,0.68)';
  }
  const ratio = Math.min(Math.max(count / maxCount, 0), 1);
  const alpha = 0.18 + ratio * 0.72;
  return `rgba(217,119,6,${alpha.toFixed(3)})`;
}

function USASvgChoropleth({
  states,
}: {
  states: StateBusinessCount[];
}) {
  const items = useMemo(
    () =>
      states
        .filter((entry) => entry.state)
        .map((entry) => ({
          state: toText(entry.state).toUpperCase(),
          count: toNumber(entry.count),
        })),
    [states],
  );

  const topStates = useMemo(
    () => [...items].sort((left, right) => right.count - left.count).slice(0, 5),
    [items],
  );

  const mapMarkup = useMemo(() => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(usStatesSvg, 'image/svg+xml');
    const svg = doc.querySelector('svg');
    if (!svg) {
      return '';
    }

    const byState = new Map(items.map((entry) => [entry.state.toLowerCase(), entry.count]));
    const maxCount = Math.max(...items.map((entry) => entry.count), 1);
    const width = svg.getAttribute('width') || '959';
    const height = svg.getAttribute('height') || '593';

    if (!svg.getAttribute('viewBox')) {
      svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    }
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.setAttribute('role', 'img');
    svg.setAttribute('style', 'display: block; max-width: 100%; max-height: 100%; margin: 0 auto; overflow: visible;');
    svg.classList.add('usa-choropleth-svg');

    svg.querySelectorAll('path, circle, polygon').forEach((element) => {
      const match = Array.from(element.classList).find((token) => /^[a-z]{2}$/.test(token));
      if (!match) {
        return;
      }

      const count = byState.get(match) ?? 0;
      const fill = stateFillColor(count, maxCount);
      const stroke = count > 0 ? 'rgba(120,53,15,0.45)' : 'rgba(26,26,26,0.14)';

      element.setAttribute('fill', fill);
      element.setAttribute('stroke', stroke);
      element.setAttribute('stroke-width', count > 0 ? '1.3' : '0.9');
      element.setAttribute('style', 'transition: fill 180ms ease, stroke 180ms ease; cursor: pointer;');

      const titleNode = element.querySelector('title');
      const stateName = titleNode?.textContent?.trim() || match.toUpperCase();
      if (titleNode) {
        titleNode.textContent = `${stateName}: ${formatMetric(count)} businesses`;
      } else {
        const title = doc.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${stateName}: ${formatMetric(count)} businesses`;
        element.appendChild(title);
      }
    });

    return svg.outerHTML;
  }, [items]);

  return (
    <div className="space-y-3">
      <div className="rounded-xl bg-white/70 p-2 shadow-[inset_0_1px_0_rgba(255,255,255,0.75)]">
        <div
          className="flex h-[430px] w-full items-center justify-center overflow-hidden [&_.borders]:pointer-events-none [&_.borders]:fill-none [&_.borders]:stroke-[rgba(26,26,26,0.16)] [&_.borders]:stroke-[1.1] [&_.usa-choropleth-svg]:h-full [&_.usa-choropleth-svg]:w-full"
          dangerouslySetInnerHTML={{ __html: mapMarkup }}
        />
      </div>
      <div className="flex flex-col gap-3 rounded-xl bg-white/55 px-3 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] text-claude-muted">
          <div className="flex items-center gap-2">
            <span>Lower</span>
            <div className="flex items-center gap-1">
              {[0.18, 0.34, 0.52, 0.7, 0.9].map((alpha) => (
                <span
                  key={alpha}
                  className="h-3 w-6 rounded-full border border-black/5"
                  style={{ backgroundColor: `rgba(217,119,6,${alpha})` }}
                />
              ))}
            </div>
            <span>Higher</span>
          </div>
          <span>{formatMetric(items.length)} states in snapshot</span>
        </div>
        <p className="text-xs text-claude-muted">
          Hover any state on the map to read its exact business count.
        </p>

        <div className="flex flex-wrap gap-2">
          {topStates.map((entry, index) => (
            <div
              key={`${entry.state}-${index}`}
              className="inline-flex items-center gap-2 rounded-full border border-black/8 bg-black/5 px-3 py-1.5"
            >
              <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-claude-muted">
                #{index + 1} {entry.state}
              </span>
              <span className="text-xs font-bold text-claude-accent">{formatMetric(entry.count)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function toNumber(value: unknown): number {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : 0;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function toText(value: unknown): string {
  if (value === null || value === undefined) {
    return '';
  }
  return String(value);
}

function scaleValue(
  value: number,
  min: number,
  max: number,
  targetMin: number,
  targetMax: number,
) {
  if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(max) || min === max) {
    return (targetMin + targetMax) / 2;
  }
  return targetMin + ((value - min) / (max - min)) * (targetMax - targetMin);
}

function formatMetric(value: unknown): string {
  const numeric = toNumber(value);
  if (!Number.isFinite(numeric)) {
    return toText(value);
  }
  if (Math.abs(numeric) >= 1000) {
    return numeric.toLocaleString();
  }
  if (numeric % 1 !== 0) {
    return numeric.toFixed(1);
  }
  return numeric.toString();
}

function buildLinePath(
  values: number[],
  width: number,
  height: number,
  padding: number,
): { linePath: string; areaPath: string } {
  if (values.length === 0) {
    return { linePath: '', areaPath: '' };
  }

  const maxValue = Math.max(...values, 1);
  const usableWidth = width - padding * 2;
  const usableHeight = height - padding * 2;
  const denominator = Math.max(values.length - 1, 1);

  const points = values.map((value, index) => {
    const x = padding + (usableWidth * index) / denominator;
    const y = height - padding - (value / maxValue) * usableHeight;
    return { x, y };
  });

  const linePath = points
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ');

  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`;

  return { linePath, areaPath };
}

function SimpleVerticalBarChart({
  data,
  labelKey,
  valueKey,
  height,
}: {
  data: ResultRow[];
  labelKey: string;
  valueKey: string;
  height: number;
}) {
  const items = data.slice(0, 8);
  const values = items.map((item) => toNumber(item[valueKey]));
  const maxValue = Math.max(...values, 1);

  return (
    <div className="flex h-full flex-col justify-between gap-4" style={{ minHeight: `${height}px` }}>
      <div className="flex h-full items-end gap-3">
        {items.map((item, index) => {
          const value = toNumber(item[valueKey]);
          const percent = Math.max((value / maxValue) * 100, 4);
          return (
            <div key={`${labelKey}-${index}`} className="flex flex-1 flex-col items-center gap-2">
              <div className="text-[10px] font-bold text-claude-accent">
                {formatMetric(value)}
              </div>
              <div className="flex h-full w-full items-end">
                <div
                  className="w-full rounded-t-xl bg-claude-accent/80"
                  style={{ height: `${percent}%`, minHeight: '8px' }}
                  title={`${toText(item[labelKey])}: ${formatMetric(value)}`}
                />
              </div>
              <div className="w-full text-center text-[10px] text-claude-muted truncate">
                {toText(item[labelKey])}
              </div>
            </div>
          );
        })}
      </div>
      <div className="text-right text-[10px] font-bold text-claude-muted">
        Max {formatMetric(maxValue)}
      </div>
    </div>
  );
}

function RatingDistributionChart({
  data,
  labelKey,
  valueKey,
  height,
}: {
  data: ResultRow[];
  labelKey: string;
  valueKey: string;
  height: number;
}) {
  const items = data
    .slice()
    .sort((left, right) => toNumber(left[labelKey]) - toNumber(right[labelKey]))
    .slice(0, 8);
  const total = items.reduce((sum, item) => sum + toNumber(item[valueKey]), 0);
  const maxValue = Math.max(...items.map((item) => toNumber(item[valueKey])), 1);

  return (
    <div className="flex h-full flex-col gap-4" style={{ minHeight: `${height}px` }}>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-black/5 bg-white/70 px-4 py-3">
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-claude-muted">
            Total Sampled
          </p>
          <p className="mt-1 text-2xl font-serif font-bold text-claude-text">
            {formatMetric(total)}
          </p>
        </div>
        <div className="rounded-2xl border border-black/5 bg-white/70 px-4 py-3">
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-claude-muted">
            Most Common Rating
          </p>
          <p className="mt-1 text-2xl font-serif font-bold text-claude-text">
            {toText(
              items.reduce<ResultRow | null>((best, item) => {
                if (!best || toNumber(item[valueKey]) > toNumber(best[valueKey])) {
                  return item;
                }
                return best;
              }, null)?.[labelKey],
            )}
            <span className="ml-1 text-base font-sans font-semibold text-claude-accent">
              stars
            </span>
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {items.map((item, index) => {
          const label = toText(item[labelKey]);
          const value = toNumber(item[valueKey]);
          const share = total > 0 ? (value / total) * 100 : 0;
          const relativeWidth = Math.max((value / maxValue) * 100, 6);
          return (
            <div
              key={`${labelKey}-distribution-${index}`}
              className="grid grid-cols-[72px_1fr_auto] items-center gap-3 rounded-2xl border border-black/5 bg-white px-4 py-3 shadow-[0_8px_24px_rgba(15,23,42,0.04)]"
            >
              <div className="text-sm font-bold text-claude-text">
                {label}
                <span className="ml-1 text-[10px] uppercase tracking-[0.12em] text-claude-muted">
                  stars
                </span>
              </div>
              <div>
                <div className="relative h-4 overflow-hidden rounded-full bg-black/5">
                  <div
                    className="h-4 rounded-full bg-gradient-to-r from-[#fbbf24] via-[#f59e0b] to-[#d97706]"
                    style={{ width: `${relativeWidth}%` }}
                    title={`${label} stars: ${formatMetric(value)} businesses (${share.toFixed(1)}%)`}
                  />
                </div>
                <div className="mt-1 flex items-center justify-between text-[10px] text-claude-muted">
                  <span>{share.toFixed(1)}% of sampled businesses</span>
                  <span>{Math.round(relativeWidth)}% of highest bucket</span>
                </div>
              </div>
              <div className="rounded-full bg-claude-accent/10 px-3 py-1 text-sm font-bold text-claude-accent">
                {formatMetric(value)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function SimpleHorizontalBarChart({
  data,
  labelKey,
  valueKey,
  height,
}: {
  data: ResultRow[];
  labelKey: string;
  valueKey: string;
  height: number;
}) {
  const items = data.slice(0, 8);
  const values = items.map((item) => toNumber(item[valueKey]));
  const maxValue = Math.max(...values, 1);

  return (
    <div className="flex h-full flex-col justify-center gap-4" style={{ minHeight: `${height}px` }}>
      {items.map((item, index) => {
        const value = toNumber(item[valueKey]);
        const percent = Math.max((value / maxValue) * 100, 6);
        return (
          <div
            key={`${labelKey}-${index}`}
            className="grid grid-cols-[128px_1fr_64px] items-center gap-3"
          >
            <div className="truncate text-xs font-medium text-claude-text" title={toText(item[labelKey])}>
              {toText(item[labelKey])}
            </div>
            <div className="h-5 rounded-full bg-black/5 overflow-hidden">
              <div
                className="flex h-5 items-center justify-end rounded-full bg-gradient-to-r from-[#f59e0b] to-[#d97706] pr-2 text-[10px] font-bold text-white"
                style={{ width: `${percent}%` }}
                title={`${toText(item[labelKey])}: ${formatMetric(value)}`}
              >
                {percent > 24 ? formatMetric(value) : ''}
              </div>
            </div>
            <div className="text-right text-xs font-bold text-claude-accent">
              {formatMetric(value)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function RankedBarPanel({
  data,
  labelKey,
  valueKey,
  height,
}: {
  data: ResultRow[];
  labelKey: string;
  valueKey: string;
  height: number;
}) {
  const items = data.slice(0, 8);
  const values = items.map((item) => toNumber(item[valueKey]));
  const maxValue = Math.max(...values, 1);

  return (
    <div className="flex h-full flex-col gap-4" style={{ minHeight: `${height}px` }}>
      <div className="grid grid-cols-[1fr_auto] gap-4 rounded-2xl border border-black/5 bg-white/80 px-4 py-3">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-claude-muted">
            Ranked Overview
          </p>
          <p className="mt-1 text-sm text-claude-muted">
            Clearer comparison of the strongest groups returned by this query.
          </p>
        </div>
        <div className="text-right">
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-claude-muted">
            Highest Value
          </p>
          <p className="mt-1 text-lg font-serif font-bold text-claude-text">
            {formatMetric(maxValue)}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {items.map((item, index) => {
          const value = toNumber(item[valueKey]);
          const percent = Math.max((value / maxValue) * 100, 6);
          return (
            <div
              key={`${labelKey}-ranked-${index}`}
              className="grid grid-cols-[36px_140px_1fr_auto] items-center gap-3 rounded-2xl border border-black/5 bg-white px-4 py-3 shadow-[0_8px_24px_rgba(15,23,42,0.04)]"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-claude-accent/10 text-sm font-bold text-claude-accent">
                {index + 1}
              </div>
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-claude-text" title={toText(item[labelKey])}>
                  {toText(item[labelKey])}
                </div>
                <div className="mt-1 text-[10px] uppercase tracking-[0.12em] text-claude-muted">
                  {Math.round(percent)}% of leader
                </div>
              </div>
              <div className="relative h-4 overflow-hidden rounded-full bg-black/5">
                <div
                  className="h-4 rounded-full bg-gradient-to-r from-[#f59e0b] via-[#ea580c] to-[#c2410c]"
                  style={{ width: `${percent}%` }}
                  title={`${toText(item[labelKey])}: ${formatMetric(value)}`}
                />
              </div>
              <div className="rounded-full bg-claude-accent/10 px-3 py-1 text-sm font-bold text-claude-accent">
                {formatMetric(value)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function SimpleLineAreaChart({
  data,
  xKey,
  yKey,
  height,
}: {
  data: ResultRow[];
  xKey: string;
  yKey: string;
  height: number;
}) {
  const items = data.slice(0, 12);
  const values = items.map((item) => toNumber(item[yKey]));
  const width = 720;
  const svgHeight = Math.max(height - 36, 180);
  const padding = 24;
  const { linePath, areaPath } = buildLinePath(values, width, svgHeight, padding);

  return (
    <div className="flex h-full flex-col gap-3">
      <svg viewBox={`0 0 ${width} ${svgHeight}`} className="h-full w-full overflow-visible">
        <path d={areaPath} fill="rgba(217, 119, 6, 0.16)" />
        <path d={linePath} fill="none" stroke="#d97706" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
        {items.map((item, index) => {
          const denominator = Math.max(items.length - 1, 1);
          const x = padding + ((width - padding * 2) * index) / denominator;
          const maxValue = Math.max(...values, 1);
          const y = svgHeight - padding - (toNumber(item[yKey]) / maxValue) * (svgHeight - padding * 2);
          return <circle key={`${xKey}-${index}`} cx={x} cy={y} r="4" fill="#d97706" />;
        })}
      </svg>
      <div className="grid grid-cols-6 gap-2 text-[10px] text-claude-muted">
        {items.slice(0, 6).map((item, index) => (
          <div key={`${xKey}-label-${index}`} className="truncate">
            {toText(item[xKey])}
          </div>
        ))}
      </div>
    </div>
  );
}

function SimpleDonutChart({
  data,
  labelKey,
  valueKey,
  colorKey,
  height,
}: {
  data: ResultRow[];
  labelKey: string;
  valueKey: string;
  colorKey?: string;
  height: number;
}) {
  const items = data.slice(0, 5);
  const total = items.reduce((sum, item) => sum + toNumber(item[valueKey]), 0) || 1;
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="flex h-full flex-col items-center justify-center gap-4" style={{ minHeight: `${height}px` }}>
      <svg viewBox="0 0 160 160" className="h-[150px] w-[150px]">
        <circle cx="80" cy="80" r={radius} fill="none" stroke="rgba(0,0,0,0.06)" strokeWidth="22" />
        {items.map((item, index) => {
          const value = toNumber(item[valueKey]);
          const segment = (value / total) * circumference;
          const strokeDasharray = `${segment} ${circumference - segment}`;
          const strokeDashoffset = -offset;
          offset += segment;
          const color = colorKey ? toText(item[colorKey]) : COLORS[index % COLORS.length];
          return (
            <circle
              key={`${labelKey}-${index}`}
              cx="80"
              cy="80"
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth="22"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="butt"
              transform="rotate(-90 80 80)"
            />
          );
        })}
        <text x="80" y="76" textAnchor="middle" fontSize="12" fill="#6b7280">
          Total
        </text>
        <text x="80" y="94" textAnchor="middle" fontSize="18" fontWeight="700" fill="#1a1a1a">
          {formatMetric(total)}
        </text>
      </svg>
      <div className="grid w-full gap-2">
        {items.map((item, index) => {
          const color = colorKey ? toText(item[colorKey]) : COLORS[index % COLORS.length];
          return (
            <div key={`${labelKey}-legend-${index}`} className="flex items-center justify-between gap-3 text-[10px]">
              <div className="flex items-center gap-2 truncate text-claude-muted">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                <span className="truncate">{toText(item[labelKey])}</span>
              </div>
              <span className="font-bold text-claude-accent">{formatMetric(item[valueKey])}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function KPICard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white border border-black/5 p-6 rounded-2xl shadow-sm">
      <p className="text-[10px] uppercase tracking-[0.1em] text-claude-muted font-bold mb-2">
        {label}
      </p>
      <span className="text-3xl font-serif font-bold text-claude-text">{value}</span>
    </div>
  );
}

function DashboardCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white border border-black/5 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b border-black/5">
        <h3 className="text-[10px] font-bold text-claude-muted uppercase tracking-widest">
          {title}
        </h3>
        {subtitle ? (
          <p className="mt-2 text-[11px] text-claude-muted">{subtitle}</p>
        ) : null}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
  disabled = false,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      type="button"
      className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
        active
          ? 'bg-claude-accent/10 text-claude-accent'
          : 'text-claude-muted hover:bg-black/5 hover:text-claude-text'
      } ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      {icon}
      {label}
    </button>
  );
}

function SchemaItem({ name, columns }: { name: string; columns: string[] }) {
  return (
    <div className="px-3 py-2 rounded-xl hover:bg-black/5 transition-colors cursor-default">
      <div className="flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-claude-accent" />
        <span className="text-xs font-bold text-claude-text">{name}</span>
      </div>
      <div className="mt-1 ml-3.5 flex flex-wrap gap-1">
        {columns.map((column) => (
          <span key={column} className="text-[9px] font-sans text-claude-muted">
            {column}
          </span>
        ))}
      </div>
    </div>
  );
}

function ExampleQuery({ text, onClick }: { text: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      type="button"
      className="w-full text-left px-3 py-1.5 text-[11px] text-claude-muted hover:text-claude-text hover:bg-black/5 rounded-lg transition-all flex items-center justify-between group cursor-pointer"
    >
      <span className="truncate">{text}</span>
      <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all transform group-hover:translate-x-0.5" />
    </button>
  );
}
