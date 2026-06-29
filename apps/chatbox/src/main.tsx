import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertCircle,
  Archive,
  CheckCircle2,
  Database,
  Download,
  Eye,
  FileCog,
  FileText,
  FileUp,
  ListChecks,
  MessageSquare,
  RefreshCcw,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import "./styles.css";

const API_BASE = "http://127.0.0.1:8000";

type DataMode = "example" | "my_data";
type ProviderPreset = "" | "minimax" | "deepseek";

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

function Workbench({
  result,
  artifacts,
  busy,
  workspaceId,
  candidateProfile,
  profileLoading,
  profileRefreshing,
  open,
  onClose,
  onRunExample,
  onRefreshProfile,
  onNotice,
  onArtifactStatus,
}: {
  result: WorkflowResult | null;
  artifacts: any[];
  busy: boolean;
  workspaceId: string;
  candidateProfile: CandidateProfile | null;
  profileLoading: boolean;
  profileRefreshing: boolean;
  open: boolean;
  onClose: () => void;
  onRunExample: () => void;
  onRefreshProfile: () => void;
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
  }, [workspaceId, sessionId]);

  useEffect(() => {
    const messageList = messagesListRef.current;
    if (messageList) messageList.scrollTop = messageList.scrollHeight;
  }, [messages, busy]);

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

  async function upload(file: File | undefined) {
    if (!file || !workspaceId) return;
    const form = new FormData();
    form.set("file", file);
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/api/files/upload?workspace_id=${encodeURIComponent(workspaceId)}`, { method: "POST", body: form });
      const json = await response.json();
      if (!response.ok) throw new Error(json.detail?.message ?? "Upload failed");
      setDataMode("my_data");
      setMessages((current) => [
        ...current,
        { role: "assistant", content: `已导入 ${file.name}。下一步可以发送“整理资料”或粘贴 JD。`, artifacts: [{ type: "document", data: json.data }], tone: "notice" },
      ]);
      await refreshChatContext();
      await loadCandidateProfile();
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
            <h1>求职材料工作台</h1>
          </div>
        </div>
        <div className="status-strip" role="status" aria-live="polite">
          <StatusBadge tone={workspaceId ? "ok" : "neutral"}>{workspaceId ? "本地就绪" : "本地初始化中"}</StatusBadge>
          <div className="mode-toggle" role="group" aria-label="数据模式">
            <button type="button" aria-pressed={dataMode === "example"} onClick={() => setDataMode("example")}>
              示例模式
            </button>
            <button type="button" aria-pressed={dataMode === "my_data"} onClick={() => setDataMode("my_data")}>
              我的资料
            </button>
          </div>
          <StatusBadge tone={providerTone(providerStatus)} shield>
            {providerLabel(providerStatus)}
          </StatusBadge>
          <button className="provider-settings-button" type="button" onClick={() => setProviderSettingsOpen(true)}>
            <Settings size={15} /> 模型设置
          </button>
          <span className="mode-note">{dataMode === "example" ? "当前使用匿名示例数据" : "仅处理本地上传资料"}</span>
        </div>
      </header>

      <div className="layout-grid">
        <DesktopContextPanel
          dataMode={dataMode}
          workflowResult={workflowResult}
          artifactCount={artifacts.length + workflowArtifactCount}
          chatContext={chatContext}
          contextLoading={contextLoading}
          lifecycleResult={lifecycleResult}
          lifecycleBusy={lifecycleBusy}
          onRefreshContext={() => {
            refreshChatContext().catch(() => undefined);
          }}
          onWorkspaceAction={runWorkspaceAction}
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
              <div className="composer-quick-actions" aria-label="输入区快捷任务">
                <label className="composer-action upload-action" title="上传简历或项目 README">
                  <FileUp size={14} /> 上传资料
                  <input type="file" onChange={(event) => upload(event.target.files?.[0])} />
                </label>
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
          busy={busy}
          workspaceId={workspaceId}
          candidateProfile={candidateProfile}
          profileLoading={profileLoading}
          profileRefreshing={profileRefreshing}
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          onRunExample={runGuidedDemo}
          onRefreshProfile={refreshCandidateProfile}
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
