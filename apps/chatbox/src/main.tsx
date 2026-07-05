import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertCircle,
  Archive,
  BarChart3,
  BriefcaseBusiness,
  CheckCircle2,
  Database,
  Download,
  Eye,
  FileCog,
  FileText,
  FileUp,
  Globe2,
  Layers,
  ListChecks,
  MapPin,
  MessageSquare,
  Mic,
  Minus,
  Navigation,
  Plus,
  Puzzle,
  RefreshCcw,
  Route,
  Send,
  Server,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  X,
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type DataMode = "example" | "my_data";
type ProviderPreset = "" | "minimax" | "deepseek";
type P8Tool = "none" | "materials" | "jd" | "jobs" | "resume";

type ProviderStatus = {
  provider: string;
  configured?: boolean;
  external_calls_enabled: boolean;
  model?: string | null;
  preset?: ProviderPreset;
  base_url?: string;
  api_key_configured?: boolean;
  timeout_seconds?: number;
  max_retries?: number;
  runtime_only?: boolean;
  p6_state?: "mock_default" | "configured" | "consented" | "called" | "failed" | "fallback" | "policy_denied";
  configured_is_called?: boolean;
  called_in_workspace?: boolean;
  called_in_session?: boolean;
  consented?: boolean;
  consent?: {
    consent_id: string;
    scope: string;
    allowed_data_classes: string[];
    expires_at: string;
  } | null;
  last_error?: string | null;
  fallback_used?: boolean;
  external_call_requires_consent?: boolean;
  api_key_redacted?: boolean;
};

type ProviderRuntimeConfig = {
  provider: "mock" | "openai_compatible";
  preset: ProviderPreset;
  base_url: string;
  api_key: string;
  model: string;
  timeout_seconds: number;
  max_retries: number;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  tone?: "normal" | "notice" | "error" | "plan";
  artifacts?: unknown[];
};

type ChatContext = {
  recent_count: number;
  total_message_count: number;
  rolling_summary: {
    summary_text: string;
    covered_message_count: number;
    source_digest: string;
  };
  workspace_snapshot: {
    latest_job?: { title?: string; company?: string } | null;
    latest_package?: unknown | null;
    artifact_count: number;
    pending_confirmation_count: number;
    artifact_types: string[];
  };
  retrieved_blocks: Array<{ artifact_type?: string; redacted_excerpt?: string; risk_label?: string }>;
  privacy_boundary: {
    contains_api_key: boolean;
    raw_provider_response_included: boolean;
    full_history_included: boolean;
    redacted: boolean;
  };
};

type CandidateProfile = {
  empty?: boolean;
  profile_summary?: {
    target_roles?: string[];
    background_summary?: string;
    transition_goal?: string;
    current_level?: string;
    source_refs?: unknown[];
  };
  capability_matrix?: Array<{
    skill: string;
    category?: string;
    evidence_level: "strong" | "usable" | "weak" | "missing";
    target_role_relevance?: string;
    source_refs?: unknown[];
    questions_to_confirm?: unknown[];
  }>;
  project_credibility?: Array<{
    project_name: string;
    credibility_label: "verified" | "plausible" | "needs_evidence" | "risky";
    evidence_gaps?: string[];
    source_refs?: unknown[];
    questions_to_confirm?: unknown[];
  }>;
  job_gaps?: Array<{
    requirement: string;
    requirement_type?: "must" | "nice";
    gap_level: "covered" | "partial" | "missing";
    impact?: string;
    next_action?: string;
    source_refs?: unknown[];
  }>;
  source_refs?: unknown[];
  questions_to_confirm?: unknown[];
  artifact_ref?: {
    artifact_id?: string;
    artifact_type?: string;
    status?: string;
    current_version_id?: string;
  } | null;
  next_actions?: string[];
  unverified_scope?: string[];
};

type LifecycleResult = {
  kind: "backup" | "cleanup" | "migration" | "diagnostics";
  title: string;
  summary: string;
  detail: string;
  status: "safe" | "warning";
};

type StoredChatMessage = {
  role: string;
  content: string;
  artifact_refs?: string;
};

type StoredArtifact = {
  id: string;
  artifact_type: string;
  status?: string;
  current_version_id?: string;
  content_json?: string;
  source_refs?: string;
  questions_to_confirm?: string;
};

type WorkflowStep = {
  key: string;
  title: string;
  status: string;
  summary: string;
  metrics?: Record<string, unknown>;
};

type WorkflowResult = {
  data_mode?: string;
  data_source?: string;
  steps: WorkflowStep[];
  summary: {
    headline: string;
    facts: number;
    fit_label?: string;
    package_id?: string;
    exports?: string[];
    training_tasks: number;
  };
  key_outputs?: Record<string, any>;
  exports?: Array<{ format: string; path: string }>;
};

type MaterialKind = "resume" | "project" | "portfolio" | "preference" | "jd" | "upload";

type JobListItem = {
  job_id: string;
  title?: string;
  company?: string;
  source_url?: string;
  platform?: string;
  user_notes?: string;
  parse_status?: "parsed" | "needs_review" | string;
  is_current_target?: boolean;
  jd_summary?: string;
  requirements?: { must_have?: string[]; nice_to_have?: string[]; responsibilities?: string[] };
  tech_stack?: string[];
  match?: {
    fit_label?: string;
    fit_score_optional?: number;
    strengths?: string[];
    gaps?: string[];
    next_actions?: string[];
  } | null;
  created_at?: string;
};

type ResumeGenerationResult = {
  job_id: string;
  resume_version_id?: string;
  package_id?: string;
  resume_markdown?: string;
  source_refs?: unknown[];
  pending_confirmations?: unknown[];
  questions_to_confirm?: unknown[];
  export_preflight?: { can_export_without_confirmation?: boolean; blocking_count?: number; message?: string };
  artifact_ref?: unknown;
};

type AgentPhase = "initializing" | "ready" | "chatting" | "executing" | "needs_confirmation" | "completed" | "error";

type AgentStatus = {
  phase: AgentPhase;
  label: string;
  headline: string;
  detail: string;
  nextAction: string;
  progress: number;
  steps: Array<{ label: string; state: "done" | "active" | "idle" | "blocked" }>;
};

type P9IntelligenceTab = "market" | "match" | "pipeline";

type ServiceState = "connected" | "configured" | "local" | "disabled" | "requires_confirmation" | "unavailable";

type ServiceStatusItem = {
  key: string;
  label: string;
  state: ServiceState;
  detail: string;
  icon: React.ReactNode;
};

type MarketCity = {
  city: string;
  x: number;
  y: number;
  jobs: number;
  salary: string;
  remote: string;
  competition: "低" | "中" | "高";
  tech: string[];
  source: string;
};

type SearchRun = {
  query: string;
  city: string;
  salary: string;
  sourceMode: string;
  resultCount: number;
  generatedAt: string;
  refs: string[];
};

type PipelineStage = "待评估" | "待投递" | "已投递" | "HR 沟通" | "笔试" | "面试" | "Offer" | "拒绝" | "搁置";

type PipelineItem = {
  id: string;
  company: string;
  role: string;
  city: string;
  stage: PipelineStage;
  statusTone: "idle" | "active" | "action" | "done" | "risk";
  nextAction: string;
  updatedAt: string;
  sourceRef: string;
};

type StoryDraft = {
  title: string;
  summary: string;
  evidence: string;
  status: "draft" | "needs_evidence" | "ready";
};

class ApiError extends Error {
  errorCode?: string;
  suggestedAction?: string;
  recoverable?: boolean;

  constructor(message: string, options?: { errorCode?: string; suggestedAction?: string; recoverable?: boolean }) {
    super(message);
    this.name = "ApiError";
    this.errorCode = options?.errorCode;
    this.suggestedAction = options?.suggestedAction;
    this.recoverable = options?.recoverable;
  }
}

const marketCities: MarketCity[] = [
  { city: "北京", x: 56, y: 34, jobs: 18, salary: "22-35k", remote: "12%", competition: "高", tech: ["LLM", "React", "Python"], source: "本地示例 + 手动 JD" },
  { city: "上海", x: 68, y: 55, jobs: 14, salary: "20-32k", remote: "18%", competition: "高", tech: ["前端", "数据可视化", "AI 应用"], source: "fixture" },
  { city: "深圳", x: 61, y: 76, jobs: 11, salary: "18-30k", remote: "10%", competition: "中", tech: ["ToB", "React", "Node"], source: "fixture" },
  { city: "杭州", x: 64, y: 59, jobs: 9, salary: "18-28k", remote: "16%", competition: "中", tech: ["电商", "低代码", "前端"], source: "fixture" },
  { city: "成都", x: 38, y: 63, jobs: 7, salary: "14-24k", remote: "22%", competition: "低", tech: ["企业应用", "Vue", "测试"], source: "fixture" },
];

const initialPipelineItems: PipelineItem[] = [
  {
    id: "pipeline-bj-ai",
    company: "北辰智能",
    role: "LLM 应用前端工程师",
    city: "北京",
    stage: "待评估",
    statusTone: "action",
    nextAction: "补充 AI 工具链项目故事后生成定制简历",
    updatedAt: "本地示例",
    sourceRef: "examples/jds/junior_frontend_jd.md",
  },
  {
    id: "pipeline-sh-data",
    company: "海石数据",
    role: "数据可视化前端",
    city: "上海",
    stage: "待投递",
    statusTone: "active",
    nextAction: "确认 ECharts / 地图可视化证据",
    updatedAt: "本地示例",
    sourceRef: "examples/p5_synthetic_personas/qa_to_fullstack/jd.md",
  },
  {
    id: "pipeline-sz-saas",
    company: "湾区协同",
    role: "SaaS 前端工程师",
    city: "深圳",
    stage: "HR 沟通",
    statusTone: "action",
    nextAction: "准备项目复盘和薪资区间说明",
    updatedAt: "本地示例",
    sourceRef: "examples/p5_synthetic_personas/ops_to_frontend/jd.md",
  },
];

const initialStoryDrafts: StoryDraft[] = [
  {
    title: "复杂工作台重构",
    summary: "围绕 Chatbox-first 信息架构，说明如何把表单向导改为对话主路径。",
    evidence: "apps/chatbox/src/main.tsx + P8.1/P9 文档",
    status: "draft",
  },
  {
    title: "求职材料事实边界",
    summary: "强调 source refs、pending confirmations 和不编造经历。",
    evidence: "P5.5 Candidate Profile / P8 resume generation",
    status: "needs_evidence",
  },
];

async function api<T>(path: string, body?: unknown, method?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: method ?? (body ? "POST" : "GET"),
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await response.json();
  if (!response.ok || json.ok === false) {
    const detail = json.detail ?? json;
    throw new ApiError(detail.message ?? "API request failed", {
      errorCode: detail.error_code,
      suggestedAction: detail.suggested_action,
      recoverable: detail.recoverable,
    });
  }
  return json.data ?? json;
}

function formatError(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    const code = error.errorCode ? `错误码：${error.errorCode}。` : "";
    const action = error.suggestedAction ? ` 下一步：${error.suggestedAction}` : "";
    return `${code}${error.message}${action}`;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}

function parseJson<T>(value: unknown, fallback: T): T {
  if (!value || typeof value !== "string") return fallback;
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
}

function compactFileName(path: string, maxLength = 30) {
  const name = path.split("/").pop() ?? path;
  if (name.length <= maxLength) return name;
  const dotIndex = name.lastIndexOf(".");
  const extension = dotIndex > 0 ? name.slice(dotIndex) : "";
  const base = dotIndex > 0 ? name.slice(0, dotIndex) : name;
  const available = Math.max(12, maxLength - extension.length - 1);
  return `${base.slice(0, available)}…${extension}`;
}

function providerLabel(providerStatus: ProviderStatus | null) {
  if (!providerStatus) return "Provider 检查中";
  if (providerStatus.p6_state === "called") return "本会话已发生外部 provider 调用";
  if (providerStatus.p6_state === "fallback") return "Provider 已降级到本地回复";
  if (providerStatus.p6_state === "policy_denied") return "外部调用被策略拦截";
  if (providerStatus.p6_state === "failed") return "外部 provider 调用失败，可本地降级";
  if (providerStatus.p6_state === "consented") return "已授权本轮外呼（未必已调用）";
  if (providerStatus.provider === "mock" || providerStatus.p6_state === "mock_default") return "Mock 本地模式（不外呼）";
  if (providerStatus.configured || providerStatus.external_calls_enabled) {
    const preset = providerStatus.preset ? `${providerStatus.preset} · ` : "";
    return `${preset}${providerStatus.model ?? "OpenAI-compatible"} 已配置，待授权`;
  }
  if (providerStatus.provider === "openai_compatible") return "外部 provider 未配置完整";
  return "外部模型未调用（隐私安全）";
}

function providerTone(providerStatus: ProviderStatus | null): "ok" | "warning" | "neutral" {
  if (!providerStatus) return "neutral";
  if (providerStatus.p6_state === "failed" || providerStatus.p6_state === "configured" || providerStatus.p6_state === "fallback" || providerStatus.p6_state === "policy_denied") return "warning";
  if (providerStatus.p6_state === "called" || providerStatus.p6_state === "consented") return "ok";
  return "neutral";
}

function defaultProviderConfig(preset: ProviderPreset = ""): ProviderRuntimeConfig {
  if (preset === "minimax") {
    return {
      provider: "openai_compatible",
      preset: "minimax",
      base_url: "https://api.minimaxi.com/v1",
      api_key: "",
      model: "MiniMax-M3",
      timeout_seconds: 30,
      max_retries: 1,
    };
  }
  if (preset === "deepseek") {
    return {
      provider: "openai_compatible",
      preset: "deepseek",
      base_url: "https://api.deepseek.com/v1",
      api_key: "",
      model: "deepseek-chat",
      timeout_seconds: 30,
      max_retries: 1,
    };
  }
  return {
    provider: "mock",
    preset: "",
    base_url: "",
    api_key: "",
    model: "",
    timeout_seconds: 30,
    max_retries: 1,
  };
}

function configFromStatus(status: ProviderStatus | null): ProviderRuntimeConfig {
  if (!status || status.provider === "mock") return defaultProviderConfig();
  const preset = status.preset ?? "";
  const defaults = defaultProviderConfig(preset);
  return {
    provider: "openai_compatible",
    preset,
    base_url: status.base_url || defaults.base_url,
    api_key: "",
    model: status.model || defaults.model,
    timeout_seconds: status.timeout_seconds ?? defaults.timeout_seconds,
    max_retries: status.max_retries ?? defaults.max_retries,
  };
}

function modeLabel(mode: DataMode) {
  return mode === "example" ? "示例模式" : "我的资料";
}

function artifactFromStored(row: StoredArtifact) {
  const content = parseJson<Record<string, unknown>>(row.content_json, {});
  const sourceRefs = parseJson<unknown[]>(row.source_refs, []);
  const questionsToConfirm = parseJson<unknown[]>(row.questions_to_confirm, []);
  return {
    type: row.artifact_type,
    data: {
      ...content,
      artifact_ref: {
        artifact_id: row.id,
        artifact_type: row.artifact_type,
        status: row.status ?? "needs_confirmation",
        current_version_id: row.current_version_id,
        source_refs: sourceRefs,
        questions_to_confirm: questionsToConfirm,
      },
      source_refs: (content as any).source_refs ?? sourceRefs,
      questions_to_confirm: (content as any).questions_to_confirm ?? questionsToConfirm,
    },
  };
}

function restoreMessages(rows: StoredChatMessage[], artifacts: StoredArtifact[]): Message[] {
  const artifactsById = new Map(artifacts.map((artifact) => [artifact.id, artifactFromStored(artifact)]));
  return rows.map((row) => {
    const refs = parseJson<Array<{ artifact_id?: string }>>(row.artifact_refs, []);
    const restoredArtifacts = refs.map((ref) => (ref.artifact_id ? artifactsById.get(ref.artifact_id) : undefined)).filter(Boolean);
    return {
      role: row.role === "user" ? "user" : "assistant",
      content: row.content,
      artifacts: restoredArtifacts,
    };
  });
}

function readableType(type: string) {
  const map: Record<string, string> = {
    job: "岗位解析",
    match_report: "匹配报告",
    application_package: "申请包草稿",
    career_facts: "职业事实",
    candidate_profile: "候选人画像",
    interview_prep: "面试准备",
    document: "资料文件",
  };
  return map[type] ?? "求职产物";
}

function artifactSummary(type: string, data: any) {
  if (type === "application_package") {
    return data?.project_description ?? data?.recruiter_message ?? "申请包草稿已生成，建议先检查待确认事实，再导出。";
  }
  if (type === "match_report") {
    const strengths = Array.isArray(data?.strengths) ? data.strengths.slice(0, 2).join("；") : "";
    const gaps = Array.isArray(data?.gaps) ? data.gaps.slice(0, 2).join("；") : "";
    return [data?.fit_label ? `匹配结论：${data.fit_label}` : "", strengths ? `优势：${strengths}` : "", gaps ? `缺口：${gaps}` : ""]
      .filter(Boolean)
      .join("。");
  }
  if (type === "job") {
    const stack = Array.isArray(data?.tech_stack) ? data.tech_stack.slice(0, 5).join(" / ") : "";
    return stack ? `核心技术栈：${stack}` : "岗位要求已解析，可继续生成匹配报告。";
  }
  if (type === "career_facts") {
    const facts = Array.isArray(data?.facts) ? data.facts : [];
    return facts.length > 0 ? `已抽取 ${facts.length} 条职业事实，建议先确认低置信内容。` : "职业事实已准备。";
  }
  if (type === "candidate_profile") {
    const matrix = Array.isArray(data?.capability_matrix) ? data.capability_matrix.length : 0;
    const gaps = Array.isArray(data?.job_gaps) ? data.job_gaps.length : 0;
    return `画像已生成：能力矩阵 ${matrix} 项，岗位短板 ${gaps} 项。`;
  }
  if (type === "interview_prep") {
    return `问题 ${data?.questions?.length ?? 0} 个，故事卡 ${data?.story_cards?.length ?? 0} 张。`;
  }
  return "产物已生成，可在此检查来源、确认项和后续操作。";
}

function artifactHighlights(type: string, data: any) {
  if (type === "job") {
    const stack = Array.isArray(data?.tech_stack) ? data.tech_stack.slice(0, 4).map((item: unknown) => String(item)) : [];
    const title = data?.title || data?.job_title || data?.role;
    const company = data?.company || data?.company_name;
    return [
      title ? { label: "岗位", value: String(title) } : undefined,
      company ? { label: "公司", value: String(company) } : undefined,
      stack.length ? { label: "技术栈", value: stack.join(" / ") } : undefined,
    ].filter(Boolean) as Array<{ label: string; value: string }>;
  }
  if (type === "match_report") {
    const strengths = Array.isArray(data?.strengths) ? data.strengths.length : 0;
    const gaps = Array.isArray(data?.gaps) ? data.gaps.length : 0;
    return [
      data?.fit_label ? { label: "匹配", value: String(data.fit_label) } : undefined,
      strengths ? { label: "优势", value: `${strengths} 项` } : undefined,
      gaps ? { label: "缺口", value: `${gaps} 项` } : undefined,
    ].filter(Boolean) as Array<{ label: string; value: string }>;
  }
  if (type === "application_package") {
    return [
      data?.package_id ? { label: "申请包", value: String(data.package_id) } : undefined,
      data?.resume_title ? { label: "简历标题", value: String(data.resume_title) } : undefined,
      data?.recruiter_message ? { label: "沟通稿", value: "已生成" } : undefined,
    ].filter(Boolean) as Array<{ label: string; value: string }>;
  }
  if (type === "candidate_profile") {
    return [
      { label: "能力", value: `${data?.capability_matrix?.length ?? 0} 项` },
      { label: "项目", value: `${data?.project_credibility?.length ?? 0} 个` },
      { label: "短板", value: `${data?.job_gaps?.length ?? 0} 项` },
    ];
  }
  if (type === "interview_prep") {
    return [
      { label: "问题", value: `${data?.questions?.length ?? 0} 个` },
      { label: "故事卡", value: `${data?.story_cards?.length ?? 0} 张` },
    ];
  }
  return [];
}

function inferAssistantTone(message: string, artifacts?: unknown[]): Message["tone"] {
  const text = message.trim();
  if ((artifacts?.length ?? 0) > 0) return "plan";
  if (text.includes("请先") || text.includes("请输入") || text.includes("失败") || text.includes("错误")) return "error";
  return "notice";
}

function guidanceForConfirmation(item: any) {
  const text = String(item?.question ?? item ?? "");
  if (!text) return "为了让申请材料更可信，建议补充这条事实的来源或数字证据。";
  if (text.includes("性能") || text.includes("%") || text.includes("提升")) {
    return `为了让简历更具说服力，建议补充具体指标证据：${text}`;
  }
  if (text.includes("上线") || text.includes("演示") || text.includes("链接")) {
    return `这会影响项目可信度，建议确认后再导出：${text}`;
  }
  return text;
}

function artifactStateMeta(status: string | undefined, hasConfirmations: boolean) {
  if (status === "exported") {
    return { className: "state-exported", label: "已导出" };
  }
  if (status === "confirmed") {
    return { className: "state-confirmed", label: "已确认" };
  }
  if (hasConfirmations || status === "needs_confirmation") {
    return { className: "state-needs-confirmation", label: "需确认" };
  }
  if (status === "failed") {
    return { className: "state-error", label: "需处理" };
  }
  if (status === "draft") {
    return { className: "state-draft", label: "草稿" };
  }
  return { className: "state-ready", label: "已就绪" };
}

function artifactNeedsConfirmation(artifact: any) {
  const data = artifact?.data ?? artifact;
  const ref = data?.artifact_ref;
  const confirmations = data?.questions_to_confirm ?? ref?.questions_to_confirm ?? [];
  const status = ref?.status;
  if (status === "confirmed" || status === "exported") return false;
  return status === "needs_confirmation" || (Array.isArray(confirmations) && confirmations.length > 0);
}

function countPendingConfirmations(artifacts: any[]) {
  return artifacts.filter(artifactNeedsConfirmation).length;
}

function buildStateSteps(activeIndex: number, blocked = false): AgentStatus["steps"] {
  return ["理解任务", "读取资料", "生成材料", "确认导出"].map((label, index) => ({
    label,
    state: blocked && index === activeIndex ? "blocked" : index < activeIndex ? "done" : index === activeIndex ? "active" : "idle",
  }));
}

function deriveAgentStatus({
  appReady,
  busy,
  dataMode,
  workflowResult,
  artifactCount,
  pendingConfirmationCount,
  lastMessageTone,
}: {
  appReady: boolean;
  busy: boolean;
  dataMode: DataMode;
  workflowResult: WorkflowResult | null;
  artifactCount: number;
  pendingConfirmationCount: number;
  lastMessageTone?: Message["tone"];
}): AgentStatus {
  if (!appReady) {
    return {
      phase: "initializing",
      label: "初始化中",
      headline: "正在准备本地工作区",
      detail: "会话、workspace 和本地隐私边界正在初始化。",
      nextAction: "初始化完成后即可上传资料或自由追问。",
      progress: 8,
      steps: buildStateSteps(0),
    };
  }
  if (busy) {
    return {
      phase: "executing",
      label: "执行中",
      headline: "Agent 正在处理当前任务",
      detail: "正在检查上下文、理解意图，并准备本地工具执行结果。",
      nextAction: "等待当前任务完成，避免重复发送。",
      progress: 56,
      steps: buildStateSteps(2),
    };
  }
  if (lastMessageTone === "error") {
    return {
      phase: "error",
      label: "需恢复",
      headline: "当前任务需要补充信息",
      detail: "最近一次请求没有顺利完成，可以补充 JD、重新上传资料或运行示例路径。",
      nextAction: "优先按错误气泡中的恢复动作继续。",
      progress: 30,
      steps: buildStateSteps(1, true),
    };
  }
  if (pendingConfirmationCount > 0) {
    return {
      phase: "needs_confirmation",
      label: "待确认",
      headline: `${pendingConfirmationCount} 个产物需要补充事实`,
      detail: "申请材料已经生成，但导出前建议先确认关键指标、链接或项目事实。",
      nextAction: "到右侧推进台处理待确认项。",
      progress: 78,
      steps: buildStateSteps(3, true),
    };
  }
  if ((workflowResult?.exports?.length ?? 0) > 0) {
    return {
      phase: "completed",
      label: "可导出",
      headline: "示例求职材料闭环已生成",
      detail: `已完成 ${workflowResult?.steps?.length ?? 0} 个步骤，右侧可查看产物、版本和导出文件。`,
      nextAction: dataMode === "example" ? "检查示例产物，或切换到我的资料继续。" : "确认事实后导出申请包。",
      progress: 92,
      steps: buildStateSteps(4),
    };
  }
  if (artifactCount > 0 || workflowResult) {
    return {
      phase: "chatting",
      label: "可继续",
      headline: "已沉淀部分求职上下文",
      detail: "可以继续追问、补充偏好，或明确要求生成下一类材料。",
      nextAction: "继续对话，或在输入区选择下一步任务。",
      progress: 62,
      steps: buildStateSteps(2),
    };
  }
  return {
    phase: "ready",
    label: "可开始",
    headline: "准备开始求职材料整理",
    detail: dataMode === "example" ? "当前使用匿名示例数据，可以自由聊，也可以运行示例路径。" : "当前使用本地上传资料，默认不会调用真实外部 provider。",
    nextAction: "从输入框上方选择上传、粘贴 JD 或自由聊。",
    progress: 18,
    steps: buildStateSteps(0),
  };
}

function CollapsibleText({ children, lines = 5, showToggle = true }: { children: React.ReactNode; lines?: number; showToggle?: boolean }) {
  const [expanded, setExpanded] = useState(false);
  if (!showToggle) return <>{children}</>;
  return (
    <div className={`collapsible-text ${expanded ? "is-expanded" : ""}`} style={{ ["--line-count" as string]: lines }}>
      <div className="collapsible-content">{children}</div>
      <button type="button" className="text-toggle" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>
        {expanded ? "收起" : "展开"}
      </button>
    </div>
  );
}

function StatusBadge({ tone = "neutral", children, shield = false }: { tone?: "ok" | "warning" | "neutral"; children: React.ReactNode; shield?: boolean }) {
  return <span className={`status-badge ${tone} ${shield ? "shield" : ""}`}>{children}</span>;
}

function serviceStateLabel(state: ServiceState) {
  const map: Record<ServiceState, string> = {
    connected: "已连通",
    configured: "已配置",
    local: "本地可用",
    disabled: "未启用",
    requires_confirmation: "需确认",
    unavailable: "不可用",
  };
  return map[state];
}

function buildServiceItems(providerStatus: ProviderStatus | null, workspaceId: string): ServiceStatusItem[] {
  const providerState: ServiceState = !providerStatus
    ? "disabled"
    : providerStatus.p6_state === "called"
      ? "connected"
      : providerStatus.provider === "mock"
        ? "local"
        : providerStatus.configured || providerStatus.api_key_configured
          ? "requires_confirmation"
          : "disabled";
  return [
    {
      key: "provider",
      label: "LLM Provider",
      state: providerState,
      detail: providerLabel(providerStatus),
      icon: <Server size={15} />,
    },
    {
      key: "search",
      label: "JD 信息源",
      state: "local",
      detail: "仅本地示例、用户粘贴和已导入 JD，不抓取平台",
      icon: <Globe2 size={15} />,
    },
    {
      key: "asr",
      label: "ASR",
      state: "requires_confirmation",
      detail: "仅 opt-in 状态入口，未采集麦克风",
      icon: <Mic size={15} />,
    },
    {
      key: "mcp",
      label: "MCP / Skill",
      state: "unavailable",
      detail: "P9 只展示状态，不建设平台连通",
      icon: <Puzzle size={15} />,
    },
    {
      key: "workspace",
      label: "Workspace",
      state: workspaceId ? "local" : "disabled",
      detail: workspaceId ? "本地 workspace 已初始化" : "初始化中",
      icon: <Database size={15} />,
    },
  ];
}

function TopServiceCenter({
  providerStatus,
  workspaceId,
  dataMode,
  onOpenSettings,
}: {
  providerStatus: ProviderStatus | null;
  workspaceId: string;
  dataMode: DataMode;
  onOpenSettings: () => void;
}) {
  const services = buildServiceItems(providerStatus, workspaceId);
  return (
    <section className="top-service-center" aria-label="顶部服务中心">
      <div className="service-center-title">
        <span className="eyebrow">Service Center</span>
        <strong>本地优先 · 高风险需确认</strong>
      </div>
      <div className="service-pill-row">
        {services.map((item) => (
          <span key={item.key} className={`service-pill service-${item.state}`} title={item.detail}>
            {item.icon}
            <span>
              <strong>{item.label}</strong>
              <small>{serviceStateLabel(item.state)}</small>
            </span>
          </span>
        ))}
      </div>
      <div className="service-actions">
        <span>{dataMode === "example" ? "匿名示例/fixture 验收" : "本地资料模式"}</span>
        <button className="provider-settings-button provider-settings-button-primary" type="button" onClick={onOpenSettings}>
          <Settings size={15} /> 配置
        </button>
      </div>
    </section>
  );
}

function MarketMapView({
  searchRun,
  onPrompt,
}: {
  searchRun: SearchRun | null;
  onPrompt: (text: string, autoSubmit?: boolean) => void;
}) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragStart, setDragStart] = useState<{ x: number; y: number; panX: number; panY: number } | null>(null);
  const [selectedCity, setSelectedCity] = useState<MarketCity>(marketCities[0]);

  function startDrag(event: React.PointerEvent<SVGSVGElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    setDragStart({ x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y });
  }

  function moveDrag(event: React.PointerEvent<SVGSVGElement>) {
    if (!dragStart) return;
    setPan({
      x: Math.max(-32, Math.min(32, dragStart.panX + (event.clientX - dragStart.x) / 5)),
      y: Math.max(-24, Math.min(24, dragStart.panY + (event.clientY - dragStart.y) / 5)),
    });
  }

  return (
    <div className="market-map-view">
      <div className="map-toolbar" aria-label="地图控制">
        <button type="button" onClick={() => setZoom((value) => Math.min(1.8, Number((value + 0.15).toFixed(2))))} aria-label="放大地图">
          <Plus size={14} />
        </button>
        <button type="button" onClick={() => setZoom((value) => Math.max(0.75, Number((value - 0.15).toFixed(2))))} aria-label="缩小地图">
          <Minus size={14} />
        </button>
        <button type="button" onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }} aria-label="重置地图">
          <Navigation size={14} />
        </button>
        <span>{Math.round(zoom * 100)}%</span>
      </div>
      <svg className="market-map" viewBox="0 0 100 88" role="img" aria-label="岗位城市地图图钉" onPointerDown={startDrag} onPointerMove={moveDrag} onPointerUp={() => setDragStart(null)}>
        <defs>
          <radialGradient id="p9Hotspot" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#2f7d6f" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#2f7d6f" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g transform={`translate(${pan.x} ${pan.y}) scale(${zoom}) translate(${(1 - zoom) * 50} ${(1 - zoom) * 44})`}>
          <path d="M18 24 C28 8 52 5 68 18 C84 31 84 56 66 72 C48 88 21 77 13 58 C8 45 10 33 18 24Z" fill="#eef5f1" stroke="#bad0c7" strokeWidth="1.2" />
          <path d="M30 28 C42 20 56 22 68 35 M25 51 C39 45 56 48 74 58 M37 72 C42 58 44 43 43 25" fill="none" stroke="#d0ddd7" strokeWidth="0.8" strokeLinecap="round" />
          {marketCities.map((city) => {
            const radius = 5 + Math.min(city.jobs, 20) / 4;
            return (
              <g key={city.city} className={`city-pin ${selectedCity.city === city.city ? "is-selected" : ""}`} transform={`translate(${city.x} ${city.y})`} onClick={(event) => { event.stopPropagation(); setSelectedCity(city); onPrompt(`帮我解释${city.city}的岗位机会、薪资区间和下一步求职动作。`); }}>
                <circle r={radius + 9} fill="url(#p9Hotspot)" />
                <circle r={radius} />
                <text y={-radius - 5}>{city.city}</text>
              </g>
            );
          })}
        </g>
      </svg>
      <div className="city-insight-card">
        <div>
          <span className="eyebrow">Selected City</span>
          <h3>{selectedCity.city}</h3>
        </div>
        <dl>
          <div><dt>岗位</dt><dd>{selectedCity.jobs} 个</dd></div>
          <div><dt>薪资</dt><dd>{selectedCity.salary}</dd></div>
          <div><dt>远程</dt><dd>{selectedCity.remote}</dd></div>
          <div><dt>竞争</dt><dd>{selectedCity.competition}</dd></div>
        </dl>
        <p>{selectedCity.tech.join(" / ")} · {selectedCity.source}</p>
      </div>
      {searchRun && (
        <div className="search-run-card">
          <span className="eyebrow">Search Run</span>
          <strong>{searchRun.query}</strong>
          <p>{searchRun.city} · {searchRun.salary} · {searchRun.resultCount} 条本地可审计结果</p>
          <small>{searchRun.sourceMode}；{searchRun.refs.join(" / ")}</small>
        </div>
      )}
    </div>
  );
}

function OpportunityMatchPanel({
  jobs,
  candidateProfile,
  onPrompt,
}: {
  jobs: JobListItem[];
  candidateProfile: CandidateProfile | null;
  onPrompt: (text: string, autoSubmit?: boolean) => void;
}) {
  const matrix = candidateProfile?.capability_matrix ?? [];
  const gaps = candidateProfile?.job_gaps ?? [];
  const visibleJobs = jobs.length > 0 ? jobs : [
    { job_id: "fixture-ai-frontend", title: "LLM 应用前端", company: "北辰智能", platform: "fixture", tech_stack: ["React", "TypeScript", "LLM"], match: { fit_label: "部分匹配", gaps: ["LLM 项目量化证据"], strengths: ["工作台 UX", "React"] } },
    { job_id: "fixture-data-viz", title: "数据可视化前端", company: "海石数据", platform: "fixture", tech_stack: ["地图", "ECharts", "仪表盘"], match: { fit_label: "可尝试", gaps: ["地图交互案例"], strengths: ["复杂 UI"] } },
  ] as JobListItem[];

  return (
    <div className="opportunity-match-panel">
      <div className="intelligence-card">
        <span className="eyebrow">Target Jobs</span>
        <h3>目标机会与匹配</h3>
        <p>这里展示已导入 JD 和本地 fixture，不代表真实平台自动搜索。</p>
      </div>
      <div className="opportunity-list">
        {visibleJobs.slice(0, 4).map((job) => (
          <button key={job.job_id} type="button" className="opportunity-row" onClick={() => onPrompt(`帮我比较 ${job.company || "该公司"} 的 ${job.title || "目标岗位"} 与当前资料的匹配和短板。`)}>
            <span><strong>{job.title || "目标岗位"}</strong><small>{job.company || "公司待确认"} · {job.platform || "本地"}</small></span>
            <em>{job.match?.fit_label || (job.is_current_target ? "当前目标" : "待匹配")}</em>
          </button>
        ))}
      </div>
      <div className="skill-gap-grid">
        <div>
          <strong>{matrix.length || 6}</strong>
          <small>能力证据项</small>
        </div>
        <div>
          <strong>{gaps.length || 3}</strong>
          <small>岗位短板</small>
        </div>
        <div>
          <strong>{candidateProfile?.source_refs?.length ?? 0}</strong>
          <small>source refs</small>
        </div>
      </div>
      <div className="gap-chip-row">
        {(gaps.length ? gaps.map((item) => item.requirement) : ["LLM 项目证据", "地图可视化案例", "可量化业务结果"]).slice(0, 5).map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </div>
  );
}

function ApplicationPipelineView({
  pipelineItems,
  onPrompt,
}: {
  pipelineItems: PipelineItem[];
  onPrompt: (text: string, autoSubmit?: boolean) => void;
}) {
  return (
    <div className="application-pipeline-view">
      <div className="pipeline-lane">
        {["待评估", "待投递", "已投递", "HR 沟通", "笔试", "面试", "Offer"].map((stage) => (
          <span key={stage} className={pipelineItems.some((item) => item.stage === stage) ? "has-item" : ""}>{stage}</span>
        ))}
      </div>
      <div className="pipeline-list">
        {pipelineItems.map((item) => (
          <article key={item.id} className={`pipeline-item tone-${item.statusTone}`}>
            <div>
              <strong>{item.company}</strong>
              <span>{item.role} · {item.city}</span>
            </div>
            <em>{item.stage}</em>
            <p>{item.nextAction}</p>
            <button type="button" onClick={() => onPrompt(`把${item.company}${item.role}的投递状态更新为：`)}>
              用 Chatbox 更新
            </button>
          </article>
        ))}
      </div>
    </div>
  );
}

function LeftIntelligencePanel({
  jobs,
  candidateProfile,
  searchRun,
  pipelineItems,
  onPrompt,
}: {
  jobs: JobListItem[];
  candidateProfile: CandidateProfile | null;
  searchRun: SearchRun | null;
  pipelineItems: PipelineItem[];
  onPrompt: (text: string, autoSubmit?: boolean) => void;
}) {
  const [activeTab, setActiveTab] = useState<P9IntelligenceTab>("market");
  const tabs: Array<{ key: P9IntelligenceTab; label: string; icon: React.ReactNode }> = [
    { key: "market", label: "市场", icon: <MapPin size={14} /> },
    { key: "match", label: "匹配", icon: <Target size={14} /> },
    { key: "pipeline", label: "流程", icon: <Route size={14} /> },
  ];
  return (
    <aside className="left-intelligence-panel" aria-label="求职态势图">
      <div className="intelligence-header">
        <div>
          <span className="eyebrow">Job Intelligence</span>
          <h2>求职态势</h2>
        </div>
        <span className="source-boundary">本地/fixture</span>
      </div>
      <div className="intelligence-tabs" role="tablist" aria-label="求职态势页签">
        {tabs.map((tab) => (
          <button key={tab.key} type="button" role="tab" aria-selected={activeTab === tab.key} onClick={() => setActiveTab(tab.key)}>
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>
      <div className="intelligence-body">
        {activeTab === "market" && <MarketMapView searchRun={searchRun} onPrompt={onPrompt} />}
        {activeTab === "match" && <OpportunityMatchPanel jobs={jobs} candidateProfile={candidateProfile} onPrompt={onPrompt} />}
        {activeTab === "pipeline" && <ApplicationPipelineView pipelineItems={pipelineItems} onPrompt={onPrompt} />}
      </div>
      <div className="intelligence-footer" role="note">
        <ShieldCheck size={14} />
        未授权时不访问招聘平台，不执行全网抓取。
      </div>
    </aside>
  );
}

function ThinkingMessage() {
  return (
    <div className="message assistant loading">
      <div>
        <span className="thinking-spinner" aria-hidden="true" />
        <strong>Agent 正在规划执行步骤...</strong>
      </div>
      <ol className="thinking-steps">
        <li>检查 workspace、资料和目标岗位状态。</li>
        <li>准备调用本地 Agent Tools 生成结构化产物。</li>
        <li>完成后会把待确认项推送到右侧推进台。</li>
      </ol>
    </div>
  );
}

function ErrorRecovery({ content, onRetry, onRunExample }: { content: string; onRetry: () => void; onRunExample: () => void }) {
  return (
    <div className="error-recovery">
      <p>{content}</p>
      <div className="recovery-actions">
        <button type="button" className="btn-secondary-action" onClick={onRetry}>
          补充 JD
        </button>
        <button type="button" className="btn-secondary-action" onClick={onRunExample}>
          跑示例路径
        </button>
      </div>
    </div>
  );
}

function SuggestedPrompts({ onPrompt, onRunExample }: { onPrompt: (text: string, autoSubmit?: boolean) => void; onRunExample: () => void }) {
  return (
    <section className="empty-state" aria-label="建议任务">
      <div className="empty-state-copy">
        <span className="empty-kicker">推荐路径</span>
        <h2>可以自由追问，也可以直接跑示例</h2>
        <p>你可以连续补充求职目标、偏好和疑问；明确粘贴 JD 或要求生成申请包时，JobPilot 才会执行对应工具。默认不调用外部模型。</p>
      </div>
      <div className="suggested-prompts">
        <button className="prompt-card" type="button" onClick={() => onPrompt("导入我的简历和项目资料，生成基础职业事实。")}>
          <span className="prompt-kicker">01</span>
          <h3>导入简历与项目</h3>
          <p>生成职业事实与技能证据卡。</p>
        </button>
        <button className="prompt-card" type="button" onClick={() => onPrompt("帮我解析这个 JD：[请在此处粘贴 JD 内容]，并生成申请包草稿。")}>
          <span className="prompt-kicker">02</span>
          <h3>解析目标 JD</h3>
          <p>提取匹配缺口并生成申请包草稿。</p>
        </button>
        <button className="prompt-card" type="button" onClick={() => onPrompt("基于我刚刚生成的申请包，帮我准备相关的面试 STAR 故事和追问练习。")}>
          <span className="prompt-kicker">03</span>
          <h3>模拟面试准备</h3>
          <p>基于当前资料生成 STAR 故事卡。</p>
        </button>
        <button className="prompt-card" type="button" onClick={() => onPrompt("我还没有 JD，先聊聊求职方向和偏好。", true)}>
          <span className="prompt-kicker">CHAT</span>
          <h3>自由聊求职方向</h3>
          <p>不中断当前上下文，先讨论目标和准备顺序。</p>
        </button>
        <button className="prompt-card" type="button" onClick={onRunExample}>
          <span className="prompt-kicker">FAST</span>
          <h3>运行示例路径</h3>
          <p>用 examples 数据跑完整求职材料闭环。</p>
        </button>
      </div>
    </section>
  );
}

const materialGuides: Array<{ kind: MaterialKind; title: string; detail: string; example: string }> = [
  { kind: "resume", title: "简历基础版", detail: "姓名可脱敏，但需要经历、技能、教育、时间线。", example: "resume.md / pdf / txt" },
  { kind: "project", title: "项目经历", detail: "补充本人负责范围、技术栈、难点、结果和链接。", example: "README.md / project.md" },
  { kind: "portfolio", title: "作品链接", detail: "GitHub、Demo、博客或截图说明，用于 source refs。", example: "links.txt" },
  { kind: "preference", title: "求职偏好", detail: "目标城市、岗位方向、薪资范围、远程偏好。", example: "preference.md" },
  { kind: "jd", title: "目标 JD", detail: "也可以直接在右侧 JD 中心粘贴。", example: "jd.md" },
];

function MaterialIntakeWizard({
  onUpload,
  busy,
}: {
  onUpload: (file: File | undefined, kind: MaterialKind) => void;
  busy: boolean;
}) {
  return (
    <section className="p8-panel material-wizard" aria-label="资料准备向导">
      <div className="p8-panel-title">
        <span className="eyebrow">Material Intake</span>
        <h3>资料准备向导</h3>
        <p>按用途上传资料，后续生成简历时会显示来源和待确认项。</p>
      </div>
      <div className="material-card-grid">
        {materialGuides.map((item) => (
          <label key={item.kind} className="material-card">
            <input type="file" disabled={busy} onChange={(event) => onUpload(event.target.files?.[0], item.kind)} />
            <strong>{item.title}</strong>
            <span>{item.detail}</span>
            <small>{item.example}</small>
          </label>
        ))}
      </div>
    </section>
  );
}

function JDIntakeCenter({
  jdText,
  sourceUrl,
  platform,
  userNotes,
  busy,
  onChange,
  onSubmit,
}: {
  jdText: string;
  sourceUrl: string;
  platform: string;
  userNotes: string;
  busy: boolean;
  onChange: (value: { jdText?: string; sourceUrl?: string; platform?: string; userNotes?: string }) => void;
  onSubmit: () => void;
}) {
  return (
    <section className="p8-panel jd-intake-center" aria-label="JD 手动导入中心">
      <div className="p8-panel-title">
        <span className="eyebrow">JD Intake</span>
        <h3>手动导入目标 JD</h3>
        <p>粘贴 JD 文本并归档来源；URL 不会被抓取或登录平台。</p>
      </div>
      <textarea value={jdText} onChange={(event) => onChange({ jdText: event.target.value })} placeholder="粘贴岗位职责、任职要求、技术栈..." rows={4} />
      <div className="jd-meta-grid">
        <input value={platform} onChange={(event) => onChange({ platform: event.target.value })} placeholder="平台：BOSS / 猎聘 / 官网" />
        <input value={sourceUrl} onChange={(event) => onChange({ sourceUrl: event.target.value })} placeholder="来源 URL（仅归档，不抓取）" />
        <input value={userNotes} onChange={(event) => onChange({ userNotes: event.target.value })} placeholder="备注：投递偏好 / 亮点 / 风险" />
        <button type="button" className="btn-primary-action" disabled={busy || jdText.trim().length < 24} onClick={onSubmit}>
          导入并设为目标
        </button>
      </div>
    </section>
  );
}

function JobTargetList({
  jobs,
  loading,
  busy,
  onSelect,
  onGenerateResume,
}: {
  jobs: JobListItem[];
  loading: boolean;
  busy: boolean;
  onSelect: (jobId: string) => void;
  onGenerateResume: (jobId?: string) => void;
}) {
  return (
    <section className="p8-panel job-target-list" aria-label="目标岗位列表">
      <div className="p8-panel-title inline">
        <div>
          <span className="eyebrow">Job Targets</span>
          <h3>目标岗位</h3>
        </div>
        <button type="button" className="btn-secondary-action" disabled={busy || jobs.length === 0} onClick={() => onGenerateResume()}>
          生成定制简历
        </button>
      </div>
      {loading ? (
        <p className="p8-empty">正在读取岗位列表...</p>
      ) : jobs.length === 0 ? (
        <p className="p8-empty">还没有导入 JD。先在左侧粘贴一个目标岗位。</p>
      ) : (
        <div className="job-list-grid">
          {jobs.slice(0, 4).map((job) => {
            const must = job.requirements?.must_have ?? job.tech_stack ?? [];
            return (
              <article key={job.job_id} className={`job-target-card ${job.is_current_target ? "is-current" : ""}`}>
                <div className="job-card-topline">
                  <strong>{job.title || "目标岗位"}</strong>
                  <span>{job.is_current_target ? "当前目标" : job.parse_status === "needs_review" ? "需复核" : "已解析"}</span>
                </div>
                <p>{job.company || "公司待确认"} · {job.platform || "来源待补充"}</p>
                <div className="job-chip-row">
                  {must.slice(0, 5).map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
                <small>{job.match?.fit_label ? `匹配：${job.match.fit_label}` : "尚未生成匹配报告"}</small>
                <div className="job-card-actions">
                  {!job.is_current_target && (
                    <button type="button" className="btn-secondary-action" disabled={busy} onClick={() => onSelect(job.job_id)}>
                      设为目标
                    </button>
                  )}
                  <button type="button" className="btn-primary-action" disabled={busy} onClick={() => onGenerateResume(job.job_id)}>
                    生成简历
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function ResumeGenerationPlane({ result }: { result: ResumeGenerationResult | null }) {
  if (!result) return null;
  return (
    <section className="p8-panel resume-generation-plane" aria-label="JD 定制简历结果">
      <div className="p8-panel-title inline">
        <div>
          <span className="eyebrow">Resume Draft</span>
          <h3>JD 定制简历草稿</h3>
        </div>
        <span className={result.export_preflight?.blocking_count ? "resume-preflight warning" : "resume-preflight ok"}>
          {result.export_preflight?.blocking_count ? `${result.export_preflight.blocking_count} 个阻塞确认` : "可进入导出检查"}
        </span>
      </div>
      <p>{result.export_preflight?.message || "请检查 source refs 和待确认项。"}</p>
      <div className="resume-proof-grid">
        <span>
          <strong>{result.resume_version_id ? "已生成" : "待生成"}</strong>
          <small>resume_version</small>
        </span>
        <span>
          <strong>{result.source_refs?.length ?? 0}</strong>
          <small>source refs</small>
        </span>
        <span>
          <strong>{result.pending_confirmations?.length ?? 0}</strong>
          <small>待确认</small>
        </span>
      </div>
    </section>
  );
}

function ComposerWorkflowDock({
  activeTool,
  onActiveTool,
  jdDraft,
  jobs,
  jobsLoading,
  resumeResult,
  busy,
  appReady,
  onUpload,
  onJdChange,
  onJdSubmit,
  onSelectJob,
  onGenerateResume,
}: {
  activeTool: P8Tool;
  onActiveTool: (tool: P8Tool) => void;
  jdDraft: { jdText: string; sourceUrl: string; platform: string; userNotes: string };
  jobs: JobListItem[];
  jobsLoading: boolean;
  resumeResult: ResumeGenerationResult | null;
  busy: boolean;
  appReady: boolean;
  onUpload: (file: File | undefined, kind: MaterialKind) => void;
  onJdChange: (value: { jdText?: string; sourceUrl?: string; platform?: string; userNotes?: string }) => void;
  onJdSubmit: () => void;
  onSelectJob: (jobId: string) => void;
  onGenerateResume: (jobId?: string) => void;
}) {
  const disabled = busy || !appReady;
  const tools: Array<{ key: P8Tool; label: string; icon: React.ReactNode; hint: string }> = [
    { key: "materials", label: "上传资料", icon: <FileUp size={14} />, hint: "简历、项目、作品、偏好" },
    { key: "jd", label: "粘贴 JD", icon: <FileText size={14} />, hint: "手动导入，不抓取 URL" },
    { key: "jobs", label: "选择岗位", icon: <ListChecks size={14} />, hint: `${jobs.length} 个目标` },
    { key: "resume", label: "生成简历", icon: <Sparkles size={14} />, hint: resumeResult ? "查看草稿状态" : "基于当前目标 JD" },
  ];

  return (
    <section className="composer-workflow-dock" aria-label="输入框上方资料与 JD 工具">
      <div className="composer-tool-rail" role="group" aria-label="资料、JD、岗位和简历快捷入口">
        {tools.map((tool) => (
          <button
            key={tool.key}
            type="button"
            aria-pressed={activeTool === tool.key}
            disabled={disabled && tool.key !== "resume"}
            onClick={() => onActiveTool(activeTool === tool.key ? "none" : tool.key)}
          >
            {tool.icon}
            <span>{tool.label}</span>
            <small>{tool.hint}</small>
          </button>
        ))}
      </div>
      {activeTool !== "none" && (
        <div className="composer-workflow-panel">
          <div className="composer-panel-topline">
            <span className="eyebrow">Assistant Tool</span>
            <button type="button" className="btn-secondary-action icon-button" onClick={() => onActiveTool("none")} aria-label="收起工具面板">
              <X size={14} />
            </button>
          </div>
          {activeTool === "materials" && <MaterialIntakeWizard onUpload={onUpload} busy={disabled} />}
          {activeTool === "jd" && (
            <JDIntakeCenter
              jdText={jdDraft.jdText}
              sourceUrl={jdDraft.sourceUrl}
              platform={jdDraft.platform}
              userNotes={jdDraft.userNotes}
              busy={disabled}
              onChange={onJdChange}
              onSubmit={onJdSubmit}
            />
          )}
          {activeTool === "jobs" && <JobTargetList jobs={jobs} loading={jobsLoading} busy={disabled} onSelect={onSelectJob} onGenerateResume={onGenerateResume} />}
          {activeTool === "resume" && (
            <section className="p8-panel resume-request-panel" aria-label="JD 定制简历生成">
              <div className="p8-panel-title inline">
                <div>
                  <span className="eyebrow">Resume Action</span>
                  <h3>围绕当前目标 JD 生成简历</h3>
                </div>
                <button type="button" className="btn-primary-action" disabled={disabled} onClick={() => onGenerateResume()}>
                  生成定制简历
                </button>
              </div>
              <p className="p8-empty">生成结果会进入右侧工作台，并显示 source refs、待确认项和导出前检查。普通聊天不会静默覆盖简历版本。</p>
              <ResumeGenerationPlane result={resumeResult} />
            </section>
          )}
        </div>
      )}
    </section>
  );
}

function ConversationHeader({
  dataMode,
  status,
  artifactCount,
  pendingConfirmationCount,
}: {
  dataMode: DataMode;
  status: AgentStatus;
  artifactCount: number;
  pendingConfirmationCount: number;
}) {
  return (
    <section className={`conversation-header agent-state agent-state-${status.phase}`} aria-label="Agent 当前状态">
      <div className="conversation-title">
        <span className="eyebrow">Agent State</span>
        <div className="agent-heading-row">
          <h2>对话与材料处理</h2>
          <span className="agent-phase-badge">{status.label}</span>
        </div>
        <p>{status.headline}</p>
      </div>
      <div className="desktop-status-grid" aria-label="当前桌面状态">
        <span>
          <CheckCircle2 size={15} />
          {status.nextAction}
        </span>
        <span>
          <ListChecks size={15} />
          {artifactCount} 个产物
        </span>
        <span>
          <AlertCircle size={15} />
          {pendingConfirmationCount} 个待确认
        </span>
        <span>
          <ShieldCheck size={15} />
          {dataMode === "example" ? "匿名示例" : "本地资料"}
        </span>
      </div>
      <div className="agent-state-body">
        <div className="agent-progress" aria-label={`当前进度 ${status.progress}%`}>
          <span style={{ width: `${status.progress}%` }} />
        </div>
        <ol className="agent-state-steps" aria-label="Agent 执行状态机">
          {status.steps.map((step) => (
            <li key={step.label} className={`agent-step-${step.state}`}>
              <span aria-hidden="true" />
              <strong>{step.label}</strong>
            </li>
          ))}
        </ol>
        <p className="agent-state-detail">{status.detail}</p>
      </div>
    </section>
  );
}

function shortSummary(value: string | undefined, max = 120) {
  if (!value) return "尚未形成摘要";
  return value.length > max ? `${value.slice(0, max)}...` : value;
}

function DesktopContextPanel({
  dataMode,
  workflowResult,
  artifactCount,
  chatContext,
  contextLoading,
  lifecycleResult,
  lifecycleBusy,
  onRefreshContext,
  onWorkspaceAction,
}: {
  dataMode: DataMode;
  workflowResult: WorkflowResult | null;
  artifactCount: number;
  chatContext: ChatContext | null;
  contextLoading: boolean;
  lifecycleResult: LifecycleResult | null;
  lifecycleBusy: boolean;
  onRefreshContext: () => void;
  onWorkspaceAction: (kind: LifecycleResult["kind"]) => void;
}) {
  const completed = workflowResult?.steps?.filter((step) => step.status === "completed").length ?? 0;
  const total = workflowResult?.steps?.length ?? 0;
  const progressLabel = workflowResult ? `${completed}/${total} 步完成` : "等待任务";
  const nextStep = workflowResult
    ? "检查推进台中的待确认项，确认事实后再导出。"
    : dataMode === "example"
      ? "运行示例路径，快速查看完整求职材料闭环。"
      : "上传简历或项目 README，再粘贴目标 JD。";

  return (
    <aside className="desktop-context-panel" aria-label="桌面任务上下文">
      <section className="context-section context-primary">
        <span className="eyebrow">Current task</span>
        <h2>{workflowResult?.summary?.headline ?? "准备求职材料"}</h2>
        <p>{nextStep}</p>
        <div className="context-progress" aria-hidden="true">
          <span style={{ width: workflowResult ? `${Math.max(8, Math.round((completed / Math.max(total, 1)) * 100))}%` : "8%" }} />
        </div>
        <div className="context-metrics" aria-label="当前任务指标">
          <span>
            <strong>{progressLabel}</strong>
            <small>流程进度</small>
          </span>
          <span>
            <strong>{artifactCount}</strong>
            <small>可检查产物</small>
          </span>
        </div>
      </section>

      <section className="context-section">
        <span className="eyebrow">Next actions</span>
        <ol className="context-next-list" aria-label="建议操作顺序">
          <li>
            <FileUp size={15} /> 在输入框上方上传资料或粘贴 JD。
          </li>
          <li>
            <FileText size={15} /> 明确要求生成申请包后才写入产物。
          </li>
          <li>
            <Sparkles size={15} /> 先运行示例路径可快速查看完整闭环。
          </li>
        </ol>
      </section>

      <section className="context-section">
        <span className="eyebrow">Safety boundary</span>
        <ul className="context-checklist">
          <li>
            <ShieldCheck size={15} /> 默认使用本地 workspace 和 mock provider。
          </li>
          <li>
            <CheckCircle2 size={15} /> 当前模式：{modeLabel(dataMode)}。
          </li>
          <li>
            <AlertCircle size={15} /> 外部模型调用需要你明确确认。
          </li>
        </ul>
      </section>

      <section className="context-section memory-section">
        <div className="context-section-title">
          <span className="eyebrow">Long context</span>
          <button className="context-icon-button" type="button" onClick={onRefreshContext} disabled={contextLoading} aria-label="刷新长对话上下文">
            <RefreshCcw size={14} />
          </button>
        </div>
        <div className="memory-card">
          <div className="memory-metrics">
            <span>
              <strong>{chatContext?.total_message_count ?? 0}</strong>
              <small>历史消息</small>
            </span>
            <span>
              <strong>{chatContext?.recent_count ?? 0}</strong>
              <small>近期窗口</small>
            </span>
          </div>
          <p>{contextLoading ? "正在读取上下文..." : shortSummary(chatContext?.rolling_summary.summary_text)}</p>
          <ul>
            <li>摘要覆盖：{chatContext?.rolling_summary.covered_message_count ?? 0} 条旧消息</li>
            <li>产物：{chatContext?.workspace_snapshot.artifact_count ?? 0} 个，待确认 {chatContext?.workspace_snapshot.pending_confirmation_count ?? 0} 个</li>
            <li>隐私：{chatContext?.privacy_boundary.contains_api_key ? "发现风险" : "不含 API Key"} / {chatContext?.privacy_boundary.full_history_included ? "含完整历史" : "不含完整历史"}</li>
          </ul>
        </div>
      </section>

      <section className="context-section operations-section">
        <span className="eyebrow">Workspace ops</span>
        <div className="ops-grid" aria-label="workspace 生命周期操作">
          <button type="button" disabled={lifecycleBusy} onClick={() => onWorkspaceAction("backup")}>
            <Archive size={14} /> 备份清单
          </button>
          <button type="button" disabled={lifecycleBusy} onClick={() => onWorkspaceAction("cleanup")}>
            <FileCog size={14} /> 清理预演
          </button>
          <button type="button" disabled={lifecycleBusy} onClick={() => onWorkspaceAction("migration")}>
            <Database size={14} /> 迁移预演
          </button>
          <button type="button" disabled={lifecycleBusy} onClick={() => onWorkspaceAction("diagnostics")}>
            <Activity size={14} /> 诊断报告
          </button>
        </div>
        <div className={`ops-result ${lifecycleResult?.status ?? "safe"}`}>
          <strong>{lifecycleResult?.title ?? "仅执行 metadata-only / dry-run 操作"}</strong>
          <span>{lifecycleBusy ? "操作执行中..." : lifecycleResult?.summary ?? "不会删除文件，不执行迁移 apply，不上传外部服务。"}</span>
          {lifecycleResult?.detail && <small>{lifecycleResult.detail}</small>}
        </div>
      </section>
    </aside>
  );
}

function ProviderSettingsModal({
  open,
  status,
  config,
  saving,
  checking,
  consenting,
  checkMessage,
  canConsent,
  onClose,
  onChange,
  onSave,
  onCheck,
  onConsent,
}: {
  open: boolean;
  status: ProviderStatus | null;
  config: ProviderRuntimeConfig;
  saving: boolean;
  checking: boolean;
  consenting: boolean;
  checkMessage: string;
  canConsent: boolean;
  onClose: () => void;
  onChange: (config: ProviderRuntimeConfig) => void;
  onSave: () => void;
  onCheck: (confirmExternalCall: boolean) => void;
  onConsent: () => void;
}) {
  const [confirmExternalCall, setConfirmExternalCall] = useState(false);
  if (!open) return null;
  const configured = status?.api_key_configured || Boolean(config.api_key);
  const externalMode = config.provider === "openai_compatible";

  function choosePreset(preset: ProviderPreset) {
    onChange(defaultProviderConfig(preset));
    setConfirmExternalCall(false);
  }

  return (
    <div className="settings-backdrop" role="presentation">
      <section className="settings-modal" role="dialog" aria-modal="true" aria-labelledby="provider-settings-title">
        <div className="settings-header">
          <div>
            <span className="eyebrow">Model Provider</span>
            <h2 id="provider-settings-title">模型供应商设置</h2>
            <p>配置只保存到当前后端进程，不写入 .env。普通自由聊天仍走本地基线；生成结构化产物时才可能使用外部 provider。</p>
          </div>
          <button className="btn-secondary-action icon-button" type="button" onClick={onClose} aria-label="关闭模型设置">
            <X size={16} />
          </button>
        </div>

        <div className="provider-choice" role="group" aria-label="供应商预设">
          <button type="button" aria-pressed={config.provider === "mock"} onClick={() => choosePreset("")}>
            Mock
            <small>本地默认，不需要 Key</small>
          </button>
          <button type="button" aria-pressed={config.preset === "minimax"} onClick={() => choosePreset("minimax")}>
            MiniMax
            <small>OpenAI-compatible</small>
          </button>
          <button type="button" aria-pressed={config.preset === "deepseek"} onClick={() => choosePreset("deepseek")}>
            DeepSeek
            <small>OpenAI-compatible</small>
          </button>
        </div>

        <div className="settings-grid">
          <label>
            <span>Base URL</span>
            <input
              value={config.base_url}
              disabled={!externalMode}
              onChange={(event) => onChange({ ...config, base_url: event.target.value })}
              placeholder="https://api.deepseek.com/v1"
            />
          </label>
          <label>
            <span>Model</span>
            <input value={config.model} disabled={!externalMode} onChange={(event) => onChange({ ...config, model: event.target.value })} placeholder="deepseek-chat" />
          </label>
          <label className="settings-span-2">
            <span>API Key</span>
            <input
              type="password"
              value={config.api_key}
              disabled={!externalMode}
              onChange={(event) => onChange({ ...config, api_key: event.target.value })}
              placeholder={status?.api_key_configured ? "当前进程已配置；留空表示不覆盖" : "只在本次后端进程内保存，不写入磁盘"}
              autoComplete="off"
            />
          </label>
          <label>
            <span>Timeout</span>
            <input
              type="number"
              min={1}
              value={config.timeout_seconds}
              disabled={!externalMode}
              onChange={(event) => onChange({ ...config, timeout_seconds: Number(event.target.value) || 30 })}
            />
          </label>
          <label>
            <span>Retries</span>
            <input
              type="number"
              min={0}
              value={config.max_retries}
              disabled={!externalMode}
              onChange={(event) => onChange({ ...config, max_retries: Number(event.target.value) || 0 })}
            />
          </label>
        </div>

        <div className="settings-status" role="note">
          <strong>当前状态：{providerLabel(status)}</strong>
          <span>{configured ? "API Key 已配置或已输入；界面和报告只显示脱敏状态。" : "尚未配置 API Key。"}</span>
          <span>保存配置、授权外呼、真实调用是三个不同状态；配置 provider 不等于已经调用 provider。</span>
          {status?.consent && <span>当前授权范围：{status.consent.allowed_data_classes.join(" / ")}，过期时间 {new Date(status.consent.expires_at).toLocaleTimeString()}。</span>}
        </div>

        <label className="settings-confirm">
          <input type="checkbox" checked={confirmExternalCall} disabled={!externalMode} onChange={(event) => setConfirmExternalCall(event.target.checked)} />
          <span>我确认允许进行一次真实外部 provider 连通性测试。未勾选时只检查配置，不外呼。</span>
        </label>

        {checkMessage && <p className="settings-message">{checkMessage}</p>}

        <div className="settings-actions">
          <button className="btn-secondary-action" type="button" onClick={onClose}>
            取消
          </button>
          <button className="btn-secondary-action" type="button" disabled={checking || !externalMode} onClick={() => onCheck(confirmExternalCall)}>
            {checking ? "检查中..." : confirmExternalCall ? "测试连接" : "检查配置"}
          </button>
          <button className="btn-secondary-action" type="button" disabled={consenting || !externalMode || !canConsent} onClick={onConsent}>
            {consenting ? "授权中..." : "授权本轮外呼"}
          </button>
          <button className="btn-primary-action" type="button" disabled={saving} onClick={onSave}>
            {saving ? "保存中..." : "保存设置"}
          </button>
        </div>
      </section>
    </div>
  );
}

function ArtifactCard({
  artifact,
  workspaceId,
  onNotice,
  onArtifactStatus,
}: {
  artifact: any;
  workspaceId: string;
  onNotice: (message: string, tone?: Message["tone"]) => void;
  onArtifactStatus: (artifactId: string, status: string) => void;
}) {
  const data = artifact?.data ?? artifact;
  const artifactRef = data?.artifact_ref;
  const artifactId = artifactRef?.artifact_id;
  const type = artifact?.type ?? artifactRef?.artifact_type ?? "artifact";
  const packageId = data?.package_id;
  const confirmations = data?.questions_to_confirm ?? artifactRef?.questions_to_confirm ?? [];
  const hasConfirmations = Array.isArray(confirmations) && confirmations.length > 0;
  const unresolvedConfirmations = hasConfirmations && artifactRef?.status !== "confirmed" && artifactRef?.status !== "exported";
  const summary = artifactSummary(type, data);
  const highlights = artifactHighlights(type, data);
  const state = artifactStateMeta(artifactRef?.status, unresolvedConfirmations);
  const [versions, setVersions] = useState<any[]>([]);
  const [currentVersionId, setCurrentVersionId] = useState<string | undefined>(artifactRef?.current_version_id);

  useEffect(() => {
    if (!artifactId || !workspaceId) return;
    api<any[]>(`/api/artifacts/${artifactId}/versions?workspace_id=${encodeURIComponent(workspaceId)}`)
      .then((items) => {
        setVersions(items ?? []);
        setCurrentVersionId(artifactRef?.current_version_id ?? items?.[items.length - 1]?.id);
      })
      .catch(() => undefined);
  }, [artifactId, workspaceId, artifactRef?.current_version_id]);

  async function confirm() {
    if (!artifactId) return;
    try {
      const confirmed = await api<any>(`/api/artifacts/${artifactId}/confirm`, { workspace_id: workspaceId });
      onArtifactStatus(artifactId, confirmed.status ?? "confirmed");
      onNotice("产物已确认。后续导出会记录该确认状态。");
    } catch (error) {
      onNotice(formatError(error, "确认失败"));
    }
  }

  async function exportPackage() {
    if (!packageId) {
      onNotice("当前产物还不是申请包，暂不能导出。");
      return;
    }
    try {
      const result = await api<any>("/api/application/export-package", {
        workspace_id: workspaceId,
        package_id: packageId,
        formats: ["markdown", "docx"],
        artifact_version_id: currentVersionId,
      });
      if (artifactId) onArtifactStatus(artifactId, result.artifact_ref?.status ?? "exported");
      const first = result.exports?.[0];
      if (first?.path) {
        const fileName = String(first.path).split("/").pop();
        window.open(`${API_BASE}/api/application/download?workspace_id=${encodeURIComponent(workspaceId)}&path=${encodeURIComponent(`exports/${fileName}`)}`, "_blank");
      }
      onNotice("申请包已导出到本地 workspace/exports，包含 Markdown 和 DOCX。");
    } catch (error) {
      onNotice(`导出失败。${formatError(error, "请先确认事实边界，或编辑产物后再次确认。")}`, "error");
    }
  }

  async function regenerate() {
    if (!artifactId) return;
    const updated = await api<any>(`/api/artifacts/${artifactId}/regenerate`, { workspace_id: workspaceId });
    setCurrentVersionId(updated.current_version_id);
    const items = await api<any[]>(`/api/artifacts/${artifactId}/versions?workspace_id=${encodeURIComponent(workspaceId)}`);
    setVersions(items ?? []);
    onArtifactStatus(artifactId, updated.status ?? "needs_confirmation");
    onNotice("已重新生成新版本，旧版本未被覆盖。");
  }

  return (
    <article className={`artifact-card ${unresolvedConfirmations ? "flagged" : ""} ${state.className}`}>
      <div className="card-header">
        <span className="artifact-type">{readableType(type)}</span>
        <span className="card-status">{state.label}</span>
      </div>
      <h3>{unresolvedConfirmations ? "建议补充关键证据" : data?.title ?? data?.fit_label ?? readableType(type)}</h3>
      <CollapsibleText lines={4} showToggle={summary.length > 110}>
        <p>{summary}</p>
      </CollapsibleText>
      {highlights.length > 0 && (
        <div className="artifact-preview" aria-label="产物摘要">
          {highlights.map((item) => (
            <span key={`${item.label}-${item.value}`}>
              <small>{item.label}</small>
              <strong>{item.value}</strong>
            </span>
          ))}
        </div>
      )}
      {hasConfirmations && (
        <ul className="confirm-list">
          {confirmations.slice(0, 3).map((item: any, index: number) => (
            <li key={index}>{guidanceForConfirmation(item)}</li>
          ))}
        </ul>
      )}
      {versions.length > 0 && (
        <div className="version-row" aria-label="版本信息">
          {versions.slice(-4).map((version) => (
            <span key={version.id} className={version.id === currentVersionId ? "version-pill active" : "version-pill"}>
              v{version.version_number}
            </span>
          ))}
        </div>
      )}
      <div className="card-actions">
        {unresolvedConfirmations && artifactId && (
          <button className="btn-primary-action" type="button" onClick={confirm}>
            确认事实
          </button>
        )}
        {packageId && (
          <button className="btn-primary-action" type="button" onClick={exportPackage}>
            导出
          </button>
        )}
        <details className="details-popover">
          <summary>
            <Eye size={15} /> 来源与详情
          </summary>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </details>
        {artifactId && (
          <button className="btn-secondary-action" type="button" onClick={regenerate}>
            <RefreshCcw size={15} /> 重新生成
          </button>
        )}
      </div>
    </article>
  );
}

function WorkflowArtifactCards({ result }: { result: WorkflowResult }) {
  const outputs = result.key_outputs ?? {};
  const cards = [
    outputs.job && { type: "job", data: outputs.job },
    outputs.match && { type: "match_report", data: outputs.match },
    (outputs.application_package || outputs.package) && { type: "application_package", data: outputs.application_package || outputs.package },
    outputs.interview && { type: "interview_prep", data: outputs.interview },
  ].filter(Boolean) as any[];
  return cards;
}

function workflowStats(result: WorkflowResult) {
  const completed = result.steps?.filter((step) => step.status === "completed").length ?? 0;
  const exports = result.exports?.length ?? 0;
  return [
    { label: "流程", value: `${completed}/${result.steps.length}` },
    { label: "事实", value: `${result.summary.facts ?? 0}` },
    { label: "导出", value: `${exports}` },
    { label: "训练", value: `${result.summary.training_tasks ?? 0}` },
  ];
}

function WorkflowPanel({ result, busy, workspaceId, onRunExample }: { result: WorkflowResult | null; busy: boolean; workspaceId: string; onRunExample: () => void }) {
  const completed = result?.steps?.filter((step) => step.status === "completed").length ?? 0;
  if (!result) {
    return (
      <div className="workbench-empty">
        <div className="workbench-empty-icon">
          <FileText size={28} aria-hidden="true" />
        </div>
        <h3>还没有生成产物</h3>
        <p>右侧会沉淀岗位解析、匹配报告、申请包草稿和面试准备。先跑示例路径，可以快速看到完整闭环。</p>
        <ol className="workbench-empty-steps">
          <li>导入资料或粘贴 JD</li>
          <li>生成申请包草稿</li>
          <li>确认事实并导出</li>
        </ol>
        <button className="btn-primary-action" type="button" onClick={onRunExample} disabled={busy || !workspaceId}>
          运行示例路径
        </button>
      </div>
    );
  }
  return (
    <section className="current-goal" aria-label="当前求职流程总览">
      <div className="goal-heading">
        <span className="artifact-type">当前目标</span>
        <span className="goal-status">示例闭环已生成</span>
      </div>
      <h3>{result.summary.headline ?? "生成可确认的求职材料"}</h3>
      <p>已完成 {completed}/{result.steps.length} 步。下一步先检查待确认事实，再导出或替换成你的真实资料。</p>
      <div className="goal-stats" aria-label="流程摘要">
        {workflowStats(result).map((item) => (
          <span key={item.label}>
            <strong>{item.value}</strong>
            <small>{item.label}</small>
          </span>
        ))}
      </div>
      <div className="goal-insight">
        <span>匹配结论</span>
        <strong>{result.summary.fit_label ?? "待分析"}</strong>
      </div>
      {(result.exports ?? []).length > 0 && (
        <div className="export-files">
          {result.exports?.map((item) => (
            <span key={item.path}>
              {item.format.toUpperCase()} · {compactFileName(item.path, 22)}
            </span>
          ))}
        </div>
      )}
      <ol className="workflow-steps" aria-label="示例路径执行步骤">
        {result.steps.map((step, index) => (
          <li key={step.key} className={`workflow-step-${step.status}`}>
            <span className="step-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <strong>{step.title}</strong>
              <p>{step.summary}</p>
            </div>
          </li>
        ))}
      </ol>
      <div className="workflow-boundary" role="note">
        <ShieldCheck size={15} aria-hidden="true" />
        当前截图只证明匿名示例数据和本地 mock 路径；真实个人资料、真实外部 provider、自动投递和会议能力仍需单独验收。
      </div>
    </section>
  );
}

function evidenceLabel(level: string | undefined) {
  return (
    {
      strong: "强证据",
      usable: "可使用",
      weak: "弱证据",
      missing: "缺证据",
      verified: "已验证",
      plausible: "基本可信",
      needs_evidence: "需补证据",
      risky: "有风险",
      covered: "已覆盖",
      partial: "部分覆盖",
    } as Record<string, string>
  )[level ?? ""] ?? "待确认";
}

function CandidateProfilePanel({
  profile,
  loading,
  refreshing,
  onRefresh,
}: {
  profile: CandidateProfile | null;
  loading: boolean;
  refreshing: boolean;
  onRefresh: () => void;
}) {
  const summary = profile?.profile_summary;
  const matrix = profile?.capability_matrix ?? [];
  const credibility = profile?.project_credibility ?? [];
  const gaps = profile?.job_gaps ?? [];
  const sourceCount = profile?.source_refs?.length ?? summary?.source_refs?.length ?? 0;

  return (
    <section className={`candidate-profile-panel ${profile?.empty ? "is-empty" : ""}`} aria-label="候选人画像">
      <div className="profile-panel-header">
        <div>
          <span className="eyebrow">Candidate Profile</span>
          <h3>候选人画像</h3>
        </div>
        <button type="button" className="btn-secondary-action" onClick={onRefresh} disabled={loading || refreshing}>
          <RefreshCcw size={14} /> {refreshing ? "生成中" : profile?.empty ? "生成画像" : "刷新画像"}
        </button>
      </div>

      {loading ? (
        <p className="profile-empty-copy">正在读取画像状态...</p>
      ) : profile?.empty || !profile ? (
        <div className="profile-empty-copy">
          <p>还没有生成候选人画像。请先导入资料并解析 JD，然后点击“生成画像”。</p>
          <span>不会读取真实个人目录，也不会调用真实外部 provider。</span>
        </div>
      ) : (
        <>
          <div className="profile-summary-card">
            <p>{summary?.background_summary || "已有资料不足，建议先补充项目和技能证据。"}</p>
            <div className="profile-metrics">
              <span>
                <strong>{matrix.length}</strong>
                <small>能力项</small>
              </span>
              <span>
                <strong>{credibility.length}</strong>
                <small>项目</small>
              </span>
              <span>
                <strong>{gaps.length}</strong>
                <small>短板</small>
              </span>
              <span>
                <strong>{sourceCount}</strong>
                <small>来源</small>
              </span>
            </div>
          </div>

          <div className="profile-section">
            <h4>能力矩阵</h4>
            <div className="profile-chip-grid">
              {matrix.slice(0, 8).map((item) => (
                <span key={item.skill} className={`profile-chip level-${item.evidence_level}`}>
                  <strong>{item.skill}</strong>
                  <small>{evidenceLabel(item.evidence_level)}</small>
                </span>
              ))}
            </div>
          </div>

          <div className="profile-section">
            <h4>项目可信度</h4>
            <div className="profile-list">
              {credibility.slice(0, 4).map((item) => (
                <article key={item.project_name} className={`profile-list-item level-${item.credibility_label}`}>
                  <strong>{item.project_name}</strong>
                  <span>{evidenceLabel(item.credibility_label)}</span>
                  {item.evidence_gaps?.length ? <p>{item.evidence_gaps.slice(0, 2).join("；")}</p> : null}
                </article>
              ))}
            </div>
          </div>

          <div className="profile-section">
            <h4>岗位短板</h4>
            <div className="profile-list">
              {gaps.slice(0, 5).map((item) => (
                <article key={`${item.requirement}-${item.requirement_type}`} className={`profile-list-item gap-${item.gap_level}`}>
                  <strong>{item.requirement}</strong>
                  <span>{item.requirement_type === "must" ? "Must" : "Nice"} · {evidenceLabel(item.gap_level)}</span>
                  <p>{item.next_action}</p>
                </article>
              ))}
            </div>
          </div>

          <details className="profile-source-details">
            <summary>查看 source refs 与未验证范围</summary>
            <p>source refs：{sourceCount} 条；待确认项：{profile.questions_to_confirm?.length ?? 0} 项。</p>
            <ul>
              {(profile.unverified_scope ?? ["未使用真实个人资料", "未调用真实外部 provider"]).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </details>
        </>
      )}
    </section>
  );
}

function ResultRail({
  artifacts,
  workflowArtifacts,
  workspaceId,
  onNotice,
  onArtifactStatus,
}: {
  artifacts: any[];
  workflowArtifacts: any[];
  workspaceId: string;
  onNotice: (message: string, tone?: Message["tone"]) => void;
  onArtifactStatus: (artifactId: string, status: string) => void;
}) {
  const allArtifacts = [...artifacts, ...workflowArtifacts];
  if (allArtifacts.length === 0) return null;
  return (
    <>
      {allArtifacts.map((artifact, index) => (
        <ArtifactCard
          key={`${artifact?.type ?? "artifact"}-${index}`}
          artifact={artifact}
          workspaceId={workspaceId}
          onNotice={onNotice}
          onArtifactStatus={onArtifactStatus}
        />
      ))}
    </>
  );
}

function P9ArtifactOverview({
  searchRun,
  storyDrafts,
  pipelineItems,
  resumeResult,
}: {
  searchRun: SearchRun | null;
  storyDrafts: StoryDraft[];
  pipelineItems: PipelineItem[];
  resumeResult: ResumeGenerationResult | null;
}) {
  return (
    <section className="p9-artifact-overview" aria-label="P9 产物台总览">
      <div className="p9-artifact-header">
        <div>
          <span className="eyebrow">Artifact Bench</span>
          <h3>产物台总览</h3>
        </div>
        <span>{pipelineItems.length} 条流程</span>
      </div>
      <div className="artifact-overview-grid">
        <article>
          <BarChart3 size={16} />
          <strong>{searchRun ? `${searchRun.resultCount} 条` : "待汇总"}</strong>
          <small>JD / 薪资 / 城市</small>
        </article>
        <article>
          <BriefcaseBusiness size={16} />
          <strong>{resumeResult?.resume_version_id ? "已生成" : "待生成"}</strong>
          <small>定制简历</small>
        </article>
        <article>
          <Layers size={16} />
          <strong>{storyDrafts.length}</strong>
          <small>项目故事</small>
        </article>
      </div>
      {searchRun && (
        <div className="artifact-brief">
          <strong>最近 search run</strong>
          <p>{searchRun.query}</p>
          <small>{searchRun.sourceMode}</small>
        </div>
      )}
      <div className="story-bank-mini">
        {storyDrafts.slice(0, 3).map((story) => (
          <article key={`${story.title}-${story.summary}`} className={`story-mini story-${story.status}`}>
            <strong>{story.title}</strong>
            <p>{story.summary}</p>
            <small>{story.evidence}</small>
          </article>
        ))}
      </div>
    </section>
  );
}

function Workbench({
  result,
  artifacts,
  jobs,
  jobsLoading,
  resumeResult,
  searchRun,
  storyDrafts,
  pipelineItems,
  busy,
  workspaceId,
  candidateProfile,
  profileLoading,
  profileRefreshing,
  open,
  onClose,
  onRunExample,
  onRefreshProfile,
  onSelectJob,
  onGenerateResume,
  onNotice,
  onArtifactStatus,
}: {
  result: WorkflowResult | null;
  artifacts: any[];
  jobs: JobListItem[];
  jobsLoading: boolean;
  resumeResult: ResumeGenerationResult | null;
  searchRun: SearchRun | null;
  storyDrafts: StoryDraft[];
  pipelineItems: PipelineItem[];
  busy: boolean;
  workspaceId: string;
  candidateProfile: CandidateProfile | null;
  profileLoading: boolean;
  profileRefreshing: boolean;
  open: boolean;
  onClose: () => void;
  onRunExample: () => void;
  onRefreshProfile: () => void;
  onSelectJob: (jobId: string) => void;
  onGenerateResume: (jobId?: string) => void;
  onNotice: (message: string, tone?: Message["tone"]) => void;
  onArtifactStatus: (artifactId: string, status: string) => void;
}) {
  const workflowArtifacts = result ? WorkflowArtifactCards({ result }) : [];
  const artifactCount = artifacts.length + workflowArtifacts.length;

  return (
    <aside className="workbench" aria-label="求职推进台">
      <div id="workbench-plane" className={`workbench-plane ${open ? "is-open" : ""}`} aria-label="求职产物推进台">
        <div className="workbench-header">
          <div>
            <span className="eyebrow">Workbench</span>
            <h2>产物推进台</h2>
          </div>
          <div className="workbench-header-actions">
            {artifactCount > 0 && <span className="badge-count">{artifactCount} 个产物</span>}
            <button className="btn-secondary-action drawer-close" type="button" onClick={onClose} aria-label="关闭推进台">
              <X size={16} /> 关闭
            </button>
          </div>
        </div>
        <div className="workbench-body">
          <P9ArtifactOverview searchRun={searchRun} storyDrafts={storyDrafts} pipelineItems={pipelineItems} resumeResult={resumeResult} />
          <JobTargetList jobs={jobs} loading={jobsLoading} busy={busy} onSelect={onSelectJob} onGenerateResume={onGenerateResume} />
          <ResumeGenerationPlane result={resumeResult} />
          <WorkflowPanel result={result} busy={busy} workspaceId={workspaceId} onRunExample={onRunExample} />
          <CandidateProfilePanel profile={candidateProfile} loading={profileLoading} refreshing={profileRefreshing} onRefresh={onRefreshProfile} />
          <ResultRail artifacts={artifacts} workflowArtifacts={workflowArtifacts} workspaceId={workspaceId} onNotice={onNotice} onArtifactStatus={onArtifactStatus} />
        </div>
      </div>
    </aside>
  );
}

function App() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const [dataMode, setDataMode] = useState<DataMode>("example");
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [providerConfig, setProviderConfig] = useState<ProviderRuntimeConfig>(defaultProviderConfig());
  const [providerSettingsOpen, setProviderSettingsOpen] = useState(false);
  const [providerSaving, setProviderSaving] = useState(false);
  const [providerChecking, setProviderChecking] = useState(false);
  const [providerConsenting, setProviderConsenting] = useState(false);
  const [providerCheckMessage, setProviderCheckMessage] = useState("");
  const [chatContext, setChatContext] = useState<ChatContext | null>(null);
  const [contextLoading, setContextLoading] = useState(false);
  const [candidateProfile, setCandidateProfile] = useState<CandidateProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileRefreshing, setProfileRefreshing] = useState(false);
  const [lifecycleResult, setLifecycleResult] = useState<LifecycleResult | null>(null);
  const [lifecycleBusy, setLifecycleBusy] = useState(false);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResult | null>(null);
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [jdDraft, setJdDraft] = useState({ jdText: "", sourceUrl: "", platform: "", userNotes: "" });
  const [resumeResult, setResumeResult] = useState<ResumeGenerationResult | null>(null);
  const [activeTool, setActiveTool] = useState<P8Tool>("none");
  const [searchRun, setSearchRun] = useState<SearchRun | null>(null);
  const [pipelineItems, setPipelineItems] = useState<PipelineItem[]>(() => {
    try {
      const stored = window.localStorage.getItem("jobpilot:p9:pipeline");
      return stored ? JSON.parse(stored) as PipelineItem[] : initialPipelineItems;
    } catch {
      return initialPipelineItems;
    }
  });
  const [storyDrafts, setStoryDrafts] = useState<StoryDraft[]>(() => {
    try {
      const stored = window.localStorage.getItem("jobpilot:p9:stories");
      return stored ? JSON.parse(stored) as StoryDraft[] : initialStoryDrafts;
    } catch {
      return initialStoryDrafts;
    }
  });
  const [drawerOpen, setDrawerOpen] = useState(false);
  const autorunStarted = useRef(false);
  const initializationNoticeShown = useRef(false);
  const messagesListRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const artifacts = useMemo(() => messages.flatMap((message) => message.artifacts ?? []), [messages]);
  const workflowArtifacts = useMemo(() => (workflowResult ? WorkflowArtifactCards({ result: workflowResult }) : []), [workflowResult]);
  const allArtifacts = useMemo(() => [...artifacts, ...workflowArtifacts], [artifacts, workflowArtifacts]);
  const pendingConfirmationCount = useMemo(() => countPendingConfirmations(allArtifacts), [allArtifacts]);
  const workflowArtifactCount = workflowArtifacts.length;
  const appReady = Boolean(workspaceId && sessionId);
  const agentStatus = useMemo(
    () =>
      deriveAgentStatus({
        appReady,
        busy,
        dataMode,
        workflowResult,
        artifactCount: allArtifacts.length,
        pendingConfirmationCount,
        lastMessageTone: messages[messages.length - 1]?.tone,
      }),
    [appReady, busy, dataMode, workflowResult, allArtifacts.length, pendingConfirmationCount, messages],
  );

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const workspaceRoot = params.get("workspace_root");
    api<ProviderStatus>("/api/provider/runtime-config")
      .then((status) => {
        setProviderStatus(status);
        setProviderConfig(configFromStatus(status));
      })
      .catch(() => undefined);
    api<any>("/api/workspace/init", {
      name: "local-job-search",
      root_path: workspaceRoot || undefined,
      llm_provider: "mock",
      privacy_mode: "local_first",
    }).then(async (data) => {
      const id = data.workspace_id ?? data.id;
      setWorkspaceId(id);
      try {
        const sessions = await api<any[]>(`/api/chat/sessions?workspace_id=${encodeURIComponent(id)}`);
        const latest = sessions?.[0];
        if (latest?.id) {
          const recovered = await api<any>(`/api/chat/sessions/${latest.id}?workspace_id=${encodeURIComponent(id)}`);
          const restored = restoreMessages(recovered.messages ?? [], recovered.artifacts ?? []);
          setSessionId(latest.id);
          if (restored.length > 0) setMessages(restored);
          return;
        }
      } catch {
        setMessages([{ role: "assistant", content: "未能恢复历史会话，已为当前 workspace 创建新会话。", tone: "notice" }]);
      }
      const session = await api<any>("/api/chat/sessions", { workspace_id: id, title: "P4 UX 工作台" });
      setSessionId(session.session_id);
    });
  }, []);

  useEffect(() => {
    if (!workspaceId || !sessionId) return;
    refreshProviderStatus().catch(() => undefined);
    refreshChatContext().catch(() => undefined);
    loadCandidateProfile().catch(() => undefined);
    loadJobs().catch(() => undefined);
  }, [workspaceId, sessionId]);

  useEffect(() => {
    const messageList = messagesListRef.current;
    if (messageList) messageList.scrollTop = messageList.scrollHeight;
  }, [messages, busy]);

  useEffect(() => {
    window.localStorage.setItem("jobpilot:p9:pipeline", JSON.stringify(pipelineItems));
  }, [pipelineItems]);

  useEffect(() => {
    window.localStorage.setItem("jobpilot:p9:stories", JSON.stringify(storyDrafts));
  }, [storyDrafts]);

  function notice(content: string, tone: Message["tone"] = "notice") {
    setMessages((current) => [...current, { role: "assistant", content, tone }]);
  }

  function updateArtifactStatus(artifactId: string, status: string) {
    setMessages((current) =>
      current.map((message) => ({
        ...message,
        artifacts: message.artifacts?.map((artifact: any) => {
          const data = artifact?.data ?? artifact;
          if (data?.artifact_ref?.artifact_id !== artifactId) return artifact;
          return {
            ...artifact,
            data: {
              ...data,
              artifact_ref: { ...data.artifact_ref, status },
            },
          };
        }),
      })),
    );
    setWorkflowResult((current) => {
      if (!current?.key_outputs) return current;
      const nextOutputs: Record<string, any> = {};
      let changed = false;
      for (const [key, value] of Object.entries(current.key_outputs)) {
        const data = value as any;
        if (data?.artifact_ref?.artifact_id !== artifactId) {
          nextOutputs[key] = value;
          continue;
        }
        changed = true;
        nextOutputs[key] = {
          ...data,
          artifact_ref: { ...data.artifact_ref, status },
        };
      }
      return changed ? { ...current, key_outputs: nextOutputs } : current;
    });
  }

  function fillPrompt(text: string, autoSubmit = false) {
    setInput(text);
    inputRef.current?.focus();
    if (autoSubmit) {
      window.setTimeout(() => sendText(text), appReady ? 80 : 220);
    }
  }

  async function refreshProviderStatus() {
    const query =
      workspaceId && sessionId
        ? `?workspace_id=${encodeURIComponent(workspaceId)}&session_id=${encodeURIComponent(sessionId)}`
        : "";
    const status = await api<ProviderStatus>(`/api/provider/runtime-config${query}`);
    setProviderStatus(status);
    setProviderConfig(configFromStatus(status));
    return status;
  }

  async function refreshChatContext() {
    if (!workspaceId || !sessionId) return null;
    setContextLoading(true);
    try {
      const context = await api<ChatContext>(`/api/chat/session/${encodeURIComponent(sessionId)}/context?workspace_id=${encodeURIComponent(workspaceId)}`);
      setChatContext(context);
      return context;
    } finally {
      setContextLoading(false);
    }
  }

  async function loadCandidateProfile() {
    if (!workspaceId) return null;
    setProfileLoading(true);
    try {
      const profile = await api<CandidateProfile>(`/api/profile/candidate?workspace_id=${encodeURIComponent(workspaceId)}`);
      setCandidateProfile(profile);
      return profile;
    } finally {
      setProfileLoading(false);
    }
  }

  async function loadJobs() {
    if (!workspaceId) return [];
    setJobsLoading(true);
    try {
      const list = await api<JobListItem[]>(`/api/jobs?workspace_id=${encodeURIComponent(workspaceId)}`);
      setJobs(list ?? []);
      return list ?? [];
    } finally {
      setJobsLoading(false);
    }
  }

  async function intakeJd() {
    if (!workspaceId) {
      notice("本地 workspace 尚未初始化，暂不能导入 JD。", "notice");
      return;
    }
    const jdText = jdDraft.jdText.trim();
    if (jdText.length < 24) {
      notice("请粘贴更完整的 JD 文本，至少包含岗位职责或任职要求。", "notice");
      return;
    }
    setBusy(true);
    try {
      const result = await api<any>("/api/job/intake", {
        workspace_id: workspaceId,
        jd_text: jdText,
        source_url: jdDraft.sourceUrl.trim() || undefined,
        platform: jdDraft.platform.trim() || undefined,
        import_method: "manual_paste",
        user_notes: jdDraft.userNotes.trim() || undefined,
      });
      setDataMode("my_data");
      setJdDraft({ jdText: "", sourceUrl: "", platform: "", userNotes: "" });
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          tone: "plan",
          content: result.message ?? "JD 已手动导入并设为当前目标岗位。",
          artifacts: [
            { type: "job", data: result.job },
            { type: "match_report", data: result.match },
          ],
        },
      ]);
      setActiveTool("jobs");
      setDrawerOpen(true);
      await Promise.allSettled([loadJobs(), refreshChatContext(), loadCandidateProfile()]);
    } catch (error) {
      notice(formatError(error, "JD 导入失败"), "error");
    } finally {
      setBusy(false);
    }
  }

  async function selectJob(jobId: string) {
    if (!workspaceId) return;
    setBusy(true);
    try {
      const result = await api<any>(`/api/jobs/${encodeURIComponent(jobId)}/select`, { workspace_id: workspaceId });
      setJobs(result.jobs ?? []);
      notice("当前目标岗位已切换。后续定制简历会绑定这个 JD。", "notice");
      await refreshChatContext();
    } catch (error) {
      notice(formatError(error, "切换目标岗位失败"), "error");
    } finally {
      setBusy(false);
    }
  }

  async function generateTargetedResume(jobId?: string) {
    if (!workspaceId) {
      notice("本地 workspace 尚未初始化，暂不能生成简历。", "notice");
      return;
    }
    setBusy(true);
    try {
      const result = await api<ResumeGenerationResult>("/api/resume/generate", {
        workspace_id: workspaceId,
        job_id: jobId,
        mode: "targeted",
        style: "junior_developer",
        language: "zh-CN",
      });
      setResumeResult(result);
      setActiveTool("resume");
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          tone: "plan",
          content: "JD 定制简历草稿已生成。请检查 source refs、待确认项和导出前检查，不要把缺证据内容直接对外投递。",
          artifacts: [{ type: "application_package", data: result }],
        },
      ]);
      setDrawerOpen(true);
      await Promise.allSettled([refreshChatContext(), loadCandidateProfile(), loadJobs()]);
    } catch (error) {
      notice(formatError(error, "生成定制简历失败"), "error");
    } finally {
      setBusy(false);
    }
  }

  function inferCity(text: string) {
    return marketCities.find((city) => text.includes(city.city))?.city ?? "北京/上海/深圳";
  }

  function inferPipelineStage(text: string): PipelineStage {
    if (/offer|录用/i.test(text)) return "Offer";
    if (/拒绝|不合适|失败/.test(text)) return "拒绝";
    if (/笔试|测评/.test(text)) return "笔试";
    if (/面试|一面|二面|终面/.test(text)) return "面试";
    if (/hr|沟通|约/.test(text.toLowerCase())) return "HR 沟通";
    if (/已投|投递完成/.test(text)) return "已投递";
    if (/搁置|暂停/.test(text)) return "搁置";
    if (/待投|准备投/.test(text)) return "待投递";
    return "待评估";
  }

  function pipelineTone(stage: PipelineStage): PipelineItem["statusTone"] {
    if (stage === "Offer") return "done";
    if (stage === "拒绝" || stage === "搁置") return "risk";
    if (stage === "HR 沟通" || stage === "笔试" || stage === "面试") return "action";
    if (stage === "已投递" || stage === "待投递") return "active";
    return "idle";
  }

  async function handleP9Command(text: string): Promise<boolean> {
    if (/汇总|搜索|岗位|JD|jd|薪资|城市|招聘信息|机会/.test(text) && !/生成.*(简历|申请包)/.test(text) && !/更新|改成|状态|投递|一面|二面|终面|面试|HR|hr|笔试|Offer|offer|拒绝|搁置/.test(text)) {
      const city = inferCity(text);
      const run: SearchRun = {
        query: text,
        city,
        salary: text.match(/\d+\s*[-~到]\s*\d+\s*k/i)?.[0] ?? "14-35k",
        sourceMode: "用户粘贴 / 已导入 JD / repo fixture，本轮不联网抓取",
        resultCount: marketCities.reduce((sum, item) => sum + (city.includes(item.city) || city.includes("/") ? item.jobs : 0), 0),
        generatedAt: new Date().toLocaleString(),
        refs: ["examples/jds/junior_frontend_jd.md", "examples/p5_synthetic_personas/*/jd.md"],
      };
      setSearchRun(run);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          tone: "plan",
          content: `已生成一组本地可审计 JD 信息源汇总：${run.city}，薪资参考 ${run.salary}，结果 ${run.resultCount} 条。来源限定为用户粘贴、已导入 JD 和 repo fixture；本轮没有登录或抓取招聘平台，也不声称全网搜索通过。你可以继续说“比较这些岗位”或“把深圳岗位优先级调低”。`,
        },
      ]);
      return true;
    }

    if (/故事|项目|能力证据|补全|简历模板|ASR|语音/.test(text)) {
      const asrNote = /ASR|语音/.test(text) ? "ASR 仍是 opt-in 状态入口，本轮没有采集麦克风或调用外部语音服务。" : "";
      const nextStory: StoryDraft = {
        title: text.includes("项目") ? "项目故事补全草稿" : "能力证据补全草稿",
        summary: "请补充：背景、本人职责、关键动作、可量化结果、可公开 source refs。",
        evidence: "来自 Chatbox 引导输入，缺证据内容会进入 pending confirmations。",
        status: "needs_evidence",
      };
      setStoryDrafts((current) => [nextStory, ...current].slice(0, 6));
      setDrawerOpen(true);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          tone: "plan",
          content: `我会按 STAR 结构引导你补资料：1. 场景和目标；2. 你负责的部分；3. 技术动作；4. 结果和证据；5. 可展示链接。${asrNote} 右侧产物台已新增故事草稿，待你继续补充事实。`,
        },
      ]);
      return true;
    }

    if (/更新|改成|状态|投递|一面|二面|终面|面试|HR|hr|笔试|Offer|offer|拒绝|搁置/.test(text)) {
      const nextStage = inferPipelineStage(text);
      setPipelineItems((current) => {
        const [first, ...rest] = current;
        const target = first ?? initialPipelineItems[0];
        return [
          {
            ...target,
            stage: nextStage,
            statusTone: pipelineTone(nextStage),
            nextAction: text,
            updatedAt: new Date().toLocaleString(),
          },
          ...rest,
        ];
      });
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          tone: "plan",
          content: `已在本地求职流程中记录状态更新：${nextStage}。这只是本地流程态势更新，不会对外发送消息、不会自动投递，也不会联系招聘平台。`,
        },
      ]);
      return true;
    }

    if (/生成.*(申请包|简历|面试故事)|申请包.*生成/.test(text)) {
      await generateTargetedResume();
      const nextStory: StoryDraft = {
        title: "面试故事包草稿",
        summary: "围绕当前目标 JD 准备 3 个可追溯项目故事，缺指标的内容需用户确认。",
        evidence: "由 Chatbox 触发，复用当前 JD 与候选人画像上下文。",
        status: "draft",
      };
      setStoryDrafts((current) => [
        nextStory,
        ...current,
      ].slice(0, 6));
      return true;
    }

    return false;
  }

  async function refreshCandidateProfile() {
    if (!workspaceId) {
      notice("本地 workspace 尚未初始化，暂不能生成画像。", "notice");
      return;
    }
    setProfileRefreshing(true);
    try {
      const profile = await api<CandidateProfile>("/api/profile/candidate/refresh", {
        workspace_id: workspaceId,
        target_role: "Junior Frontend Developer",
      });
      setCandidateProfile(profile);
      setDrawerOpen(true);
      notice(profile.empty ? "还没有足够资料生成画像，请先导入资料并解析 JD。" : "候选人画像已刷新。请在右侧查看能力矩阵、项目可信度和岗位短板。", "notice");
      await refreshChatContext();
    } catch (error) {
      notice(formatError(error, "画像刷新失败"), "error");
    } finally {
      setProfileRefreshing(false);
    }
  }

  async function saveProviderSettings() {
    setProviderSaving(true);
    setProviderCheckMessage("");
    try {
      const saved = await api<ProviderStatus>("/api/provider/runtime-config", providerConfig);
      setProviderStatus(saved);
      setProviderConfig(configFromStatus(saved));
      if (workspaceId) {
        const params = new URLSearchParams(window.location.search);
        const workspaceRoot = params.get("workspace_root");
        await api<any>("/api/workspace/init", {
          name: "local-job-search",
          root_path: workspaceRoot || undefined,
          llm_provider: providerConfig.provider === "mock" ? "mock" : "openai_compatible",
          privacy_mode: "local_first",
        });
      }
      setProviderCheckMessage(providerConfig.provider === "mock" ? "已切回 Mock 本地模式。" : "模型配置已保存到当前后端进程。");
      notice(providerConfig.provider === "mock" ? "已切回 Mock 本地模式，不会外呼真实 provider。" : "模型供应商已保存。执行结构化工具前请确认是否允许真实外部调用。", "notice");
    } catch (error) {
      setProviderCheckMessage(formatError(error, "保存 provider 配置失败"));
    } finally {
      setProviderSaving(false);
    }
  }

  async function checkProvider(confirmExternalCall: boolean) {
    setProviderChecking(true);
    setProviderCheckMessage("");
    try {
      await api<ProviderStatus>("/api/provider/runtime-config", providerConfig);
      const result = await api<any>("/api/provider/check", {
        workspace_id: workspaceId || undefined,
        provider: providerConfig.provider,
        confirm_external_call: confirmExternalCall,
      });
      await refreshProviderStatus();
      if (result.checked) {
        setProviderCheckMessage("真实 provider 连通性测试通过。");
      } else {
        setProviderCheckMessage(result.message ?? "配置已存在；未执行真实外部调用。");
      }
    } catch (error) {
      setProviderCheckMessage(formatError(error, "provider 检查失败"));
    } finally {
      setProviderChecking(false);
    }
  }

  async function requestProviderConsent() {
    if (!workspaceId || !sessionId) {
      setProviderCheckMessage("本地 workspace 和会话尚未初始化，暂不能授权外呼。");
      return;
    }
    setProviderConsenting(true);
    setProviderCheckMessage("");
    try {
      const status = await api<ProviderStatus>("/api/provider/consent", {
        workspace_id: workspaceId,
        session_id: sessionId,
        scope: "chat_session",
        ttl_seconds: 900,
        allowed_data_classes: ["recent_messages", "rolling_summary", "workspace_summary", "artifact_summary"],
        confirm_external_call: true,
      });
      setProviderStatus(status);
      setProviderCheckMessage(status.consented ? "已授权本会话外呼范围；是否真实调用仍由具体操作和 Provider Policy Gate 决定。" : "授权未生效。");
      notice("已记录本会话外呼授权范围。普通聊天当前仍保持本地基线；后续 provider-backed chat 会继续通过 Policy Gate。", "notice");
    } catch (error) {
      setProviderCheckMessage(formatError(error, "授权外呼失败"));
    } finally {
      setProviderConsenting(false);
    }
  }

  async function sendText(rawText?: string) {
    const text = (rawText ?? input).trim();
    if (!text) {
      notice("还没有收到任务。你可以选择一个建议任务，或粘贴目标 JD。", "notice");
      return;
    }
    if (!workspaceId || !sessionId) {
      if (!initializationNoticeShown.current) {
        initializationNoticeShown.current = true;
        notice("本地工作区和会话还在初始化，请稍后再发送。", "notice");
      }
      return;
    }
    setInput("");
    setMessages((current) => [...current, { role: "user", content: text }]);
    if (await handleP9Command(text)) {
      await Promise.allSettled([refreshChatContext(), loadCandidateProfile(), loadJobs()]);
      return;
    }
    setBusy(true);
    try {
      const providerMode = providerStatus?.consented && providerStatus.provider !== "mock" ? "provider_opt_in" : "local_default";
      const result = await api<any>("/api/chat/message", { workspace_id: workspaceId, session_id: sessionId, message: text, provider_mode: providerMode });
      const providerNote =
        result.provider_invocation_status === "called"
          ? "（已按授权使用 provider-backed 路径；普通聊天未写入产物。）"
          : result.fallback_used
            ? "（provider 未调用或已降级，本轮使用本地连续对话。）"
            : "";
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: providerNote ? `${result.message}\n${providerNote}` : result.message,
          artifacts: result.artifacts,
          tone: inferAssistantTone(result.message, result.artifacts),
        },
      ]);
      await Promise.allSettled([refreshProviderStatus(), refreshChatContext(), loadCandidateProfile()]);
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", tone: "error", content: formatError(error, "请求失败") }]);
    } finally {
      setBusy(false);
    }
  }

  async function upload(file: File | undefined, kind: MaterialKind = "upload") {
    if (!file || !workspaceId) return;
    const form = new FormData();
    form.set("file", file);
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/api/files/upload?workspace_id=${encodeURIComponent(workspaceId)}&kind=${encodeURIComponent(kind)}`, { method: "POST", body: form });
      const json = await response.json();
      if (!response.ok) throw new Error(json.detail?.message ?? "Upload failed");
      setDataMode("my_data");
      setMessages((current) => [
        ...current,
        { role: "assistant", content: `已按“${kind}”导入 ${file.name}。下一步可以整理资料、粘贴 JD 或生成定制简历。`, artifacts: [{ type: "document", data: json.data }], tone: "notice" },
      ]);
      await refreshChatContext();
      await loadCandidateProfile();
      if (kind === "jd") await loadJobs();
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", tone: "error", content: formatError(error, "上传失败") }]);
    } finally {
      setBusy(false);
    }
  }

  async function runGuidedDemo() {
    if (!workspaceId) return;
    setBusy(true);
    try {
      setDataMode("example");
      const result = await api<WorkflowResult>("/api/workflows/p2-demo/run", { workspace_id: workspaceId, data_mode: "example" });
      setWorkflowResult(result);
      setDrawerOpen(true);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          tone: "plan",
          content: `示例路径已完成：${result.steps.length} 个步骤，导出 ${result.exports?.length ?? 0} 个文件。请检查推进台里的待确认项和导出状态。`,
        },
      ]);
      await refreshChatContext();
      await loadCandidateProfile();
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", tone: "error", content: formatError(error, "示例工作流执行失败") }]);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (!workspaceId || autorunStarted.current) return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("autorun") !== "1") return;
    autorunStarted.current = true;
    runGuidedDemo();
  }, [workspaceId]);

  async function runWorkspaceAction(kind: LifecycleResult["kind"]) {
    if (!workspaceId) return;
    setLifecycleBusy(true);
    try {
      if (kind === "backup") {
        const result = await api<any>("/api/workspace/backup", { workspace_id: workspaceId });
        setLifecycleResult({
          kind,
          title: "备份清单已生成",
          summary: `metadata-only，文件数 ${result.file_count}，不包含文件内容。`,
          detail: result.manifest_path,
          status: "safe",
        });
      } else if (kind === "cleanup") {
        const result = await api<any>("/api/workspace/cleanup/plan", { workspace_id: workspaceId, rules: { include_exports: true } });
        setLifecycleResult({
          kind,
          title: "清理预演完成",
          summary: `dry-run=true，影响 ${result.affected_count} 个文件，未删除任何内容。`,
          detail: result.message,
          status: "warning",
        });
      } else if (kind === "migration") {
        const result = await api<any>("/api/workspace/migrate/plan", { workspace_id: workspaceId, target_version: "p7-beta" });
        setLifecycleResult({
          kind,
          title: "迁移预演完成",
          summary: `目标版本 ${result.target_version}，dry-run=true，apply 仍需人工确认。`,
          detail: result.rollback_notes,
          status: "warning",
        });
      } else {
        const result = await api<any>("/api/diagnostics/report", { workspace_id: workspaceId, include_provider: true });
        setLifecycleResult({
          kind,
          title: "脱敏诊断已生成",
          summary: `artifacts=${result.counts.artifacts}，sessions=${result.counts.chat_sessions}，provider=${result.provider.provider}。`,
          detail: result.redaction_status,
          status: "safe",
        });
      }
    } catch (error) {
      setLifecycleResult({
        kind,
        title: "操作失败",
        summary: formatError(error, "workspace 操作失败"),
        detail: "未执行删除、迁移 apply 或外部上传。",
        status: "warning",
      });
    } finally {
      setLifecycleBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="eyebrow">JobPilot AI</span>
          <div className="brand-title-row">
            <h1>Chatbox-native 求职材料工作台</h1>
          </div>
        </div>
        <TopServiceCenter providerStatus={providerStatus} workspaceId={workspaceId} dataMode={dataMode} onOpenSettings={() => setProviderSettingsOpen(true)} />
      </header>

      <div className="layout-grid">
        <LeftIntelligencePanel
          jobs={jobs}
          candidateProfile={candidateProfile}
          searchRun={searchRun}
          pipelineItems={pipelineItems}
          onPrompt={fillPrompt}
        />
        <section className="workstream conversation-area" aria-label="对话区">
          <section className="conversation-plane" aria-label="对话与任务区">
            <ConversationHeader
              dataMode={dataMode}
              status={agentStatus}
              artifactCount={artifacts.length + workflowArtifactCount}
              pendingConfirmationCount={pendingConfirmationCount}
            />
            <div className="timeline" ref={messagesListRef} role="log" aria-live="polite">
              <div className="timeline-content">
                {messages.length === 0 && !busy && <SuggestedPrompts onPrompt={fillPrompt} onRunExample={runGuidedDemo} />}
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.role} ${message.tone ?? ""}`}>
                    {message.tone === "error" ? (
                      <ErrorRecovery content={message.content} onRetry={() => fillPrompt("请帮我解析这个 JD：[请在这里粘贴 JD 内容]")} onRunExample={runGuidedDemo} />
                    ) : (
                      <CollapsibleText lines={message.role === "user" ? 6 : 5} showToggle={message.content.length > 160}>
                        <p>{message.content}</p>
                      </CollapsibleText>
                    )}
                  </div>
                ))}
                {busy && <ThinkingMessage />}
              </div>
            </div>

            <form
              className="composer"
              onSubmit={(event) => {
                event.preventDefault();
                sendText();
              }}
            >
              <ComposerWorkflowDock
                activeTool={activeTool}
                onActiveTool={setActiveTool}
                jdDraft={jdDraft}
                jobs={jobs}
                jobsLoading={jobsLoading}
                resumeResult={resumeResult}
                busy={busy}
                appReady={appReady}
                onUpload={upload}
                onJdChange={(value) => setJdDraft((current) => ({ ...current, ...value }))}
                onJdSubmit={intakeJd}
                onSelectJob={selectJob}
                onGenerateResume={generateTargetedResume}
              />
              <div className="composer-quick-actions" aria-label="输入区快捷任务">
                <button type="button" onClick={() => fillPrompt("我还没有 JD，先聊聊求职方向和偏好。", true)} disabled={!appReady || busy}>
                  <MessageSquare size={14} /> 自由聊
                </button>
                <button type="button" onClick={() => fillPrompt("帮我解析这个 JD：[请在这里粘贴 JD 内容]")} disabled={!appReady || busy}>
                  <FileText size={14} /> 粘贴 JD
                </button>
                <button type="button" onClick={() => fillPrompt("请基于当前资料和目标 JD，生成申请包草稿。")} disabled={!appReady || busy}>
                  <ListChecks size={14} /> 生成申请包
                </button>
                <button type="button" onClick={() => fillPrompt("基于当前申请包，帮我准备面试问题和 STAR 故事。")} disabled={!appReady || busy}>
                  <CheckCircle2 size={14} /> 准备面试
                </button>
                <button type="button" onClick={refreshCandidateProfile} disabled={!appReady || busy || profileRefreshing}>
                  <RefreshCcw size={14} /> 生成画像
                </button>
                <button type="button" onClick={runGuidedDemo} disabled={!workspaceId || busy}>
                  <Sparkles size={14} /> 示例路径
                </button>
              </div>
              <div className="composer-inner">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      sendText();
                    }
                  }}
                  placeholder="可以连续追问、补充偏好，或直接粘贴目标岗位 JD..."
                  aria-label="对话输入框"
                  rows={2}
                />
                <button type="submit" className="btn-send" disabled={busy || !appReady} aria-label="发送任务">
                  <Send size={17} /> {appReady ? "发送任务" : "初始化中"}
                </button>
              </div>
            </form>
          </section>
        </section>

        <div className={`drawer-overlay ${drawerOpen ? "is-open" : ""}`} onClick={() => setDrawerOpen(false)} />
        <Workbench
          result={workflowResult}
          artifacts={artifacts}
          jobs={jobs}
          jobsLoading={jobsLoading}
          resumeResult={resumeResult}
          searchRun={searchRun}
          storyDrafts={storyDrafts}
          pipelineItems={pipelineItems}
          busy={busy}
          workspaceId={workspaceId}
          candidateProfile={candidateProfile}
          profileLoading={profileLoading}
          profileRefreshing={profileRefreshing}
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          onRunExample={runGuidedDemo}
          onRefreshProfile={refreshCandidateProfile}
          onSelectJob={selectJob}
          onGenerateResume={generateTargetedResume}
          onNotice={notice}
          onArtifactStatus={updateArtifactStatus}
        />
        {(artifacts.length > 0 || workflowResult) && (
          <button className="mobile-fab" type="button" onClick={() => setDrawerOpen(true)} aria-expanded={drawerOpen} aria-controls="workbench-plane">
            查看推进台 <span className="badge">{artifacts.length || workflowResult?.steps.length}</span>
          </button>
        )}
      </div>
      <ProviderSettingsModal
        open={providerSettingsOpen}
        status={providerStatus}
        config={providerConfig}
        saving={providerSaving}
        checking={providerChecking}
        consenting={providerConsenting}
        checkMessage={providerCheckMessage}
        canConsent={Boolean(workspaceId && sessionId)}
        onClose={() => setProviderSettingsOpen(false)}
        onChange={setProviderConfig}
        onSave={saveProviderSettings}
        onCheck={checkProvider}
        onConsent={requestProviderConsent}
      />
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
