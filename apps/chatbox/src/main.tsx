import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertCircle,
  CheckCircle2,
  Download,
  Eye,
  FileText,
  FileUp,
  ListChecks,
  RefreshCcw,
  Send,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import "./styles.css";

const API_BASE = "http://127.0.0.1:8000";

type DataMode = "example" | "my_data";

type Message = {
  role: "user" | "assistant";
  content: string;
  tone?: "normal" | "notice" | "error" | "plan";
  artifacts?: unknown[];
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

function providerLabel(providerStatus: { provider: string; external_calls_enabled: boolean } | null) {
  if (!providerStatus) return "Provider 检查中";
  if (providerStatus.external_calls_enabled) return "外部模型未调用（隐私安全）";
  return "外部模型未调用（隐私安全）";
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
  if (type === "interview_prep") {
    return `问题 ${data?.questions?.length ?? 0} 个，故事卡 ${data?.story_cards?.length ?? 0} 张。`;
  }
  return "产物已生成，可在此检查来源、确认项和后续操作。";
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
      <h2>你好！准备好开始处理求职材料了吗？</h2>
      <p>选择一个建议任务，或者直接粘贴你的目标 JD。计划、产物和待确认项会进入右侧推进台。</p>
      <div className="suggested-prompts">
        <button className="prompt-card" type="button" onClick={() => onPrompt("导入我的简历和项目资料，生成基础职业事实。")}>
          <span className="prompt-kicker">第一步</span>
          <h3>导入简历与项目</h3>
          <p>生成职业事实与技能证据卡。</p>
        </button>
        <button className="prompt-card" type="button" onClick={() => onPrompt("帮我解析这个 JD：[请在此处粘贴 JD 内容]，并生成申请包草稿。")}>
          <span className="prompt-kicker">核心任务</span>
          <h3>解析目标 JD</h3>
          <p>提取匹配缺口并生成申请包草稿。</p>
        </button>
        <button className="prompt-card" type="button" onClick={() => onPrompt("基于我刚刚生成的申请包，帮我准备相关的面试 STAR 故事和追问练习。")}>
          <span className="prompt-kicker">面试</span>
          <h3>模拟面试准备</h3>
          <p>基于当前资料生成 STAR 故事卡。</p>
        </button>
        <button className="prompt-card" type="button" onClick={onRunExample}>
          <span className="prompt-kicker">快速验收</span>
          <h3>运行示例路径</h3>
          <p>用 examples 数据跑完整求职材料闭环。</p>
        </button>
      </div>
    </section>
  );
}

function ConversationHeader({
  dataMode,
  busy,
  workflowResult,
  artifactCount,
  onPrompt,
  onRunExample,
}: {
  dataMode: DataMode;
  busy: boolean;
  workflowResult: WorkflowResult | null;
  artifactCount: number;
  onPrompt: (text: string, autoSubmit?: boolean) => void;
  onRunExample: () => void;
}) {
  const completed = workflowResult?.steps?.filter((step) => step.status === "completed").length ?? 0;
  const total = workflowResult?.steps?.length ?? 0;
  return (
    <section className="conversation-header" aria-label="桌面对话工作台">
      <div className="conversation-title">
        <span className="eyebrow">Conversation</span>
        <h2>对话与材料处理</h2>
        <p>
          {workflowResult
            ? `当前已完成 ${completed}/${total} 步，继续检查右侧产物和待确认项。`
            : `${modeLabel(dataMode)}下可以先导入资料、粘贴 JD，或直接运行示例路径。`}
        </p>
      </div>
      <div className="desktop-status-grid" aria-label="当前桌面状态">
        <span>
          <CheckCircle2 size={15} />
          {busy ? "处理中" : "可继续"}
        </span>
        <span>
          <ListChecks size={15} />
          {artifactCount} 个产物
        </span>
        <span>
          <ShieldCheck size={15} />
          {dataMode === "example" ? "匿名示例" : "本地资料"}
        </span>
      </div>
      <div className="desktop-action-strip" aria-label="桌面快捷任务">
        <button type="button" onClick={() => onPrompt("导入我的简历和项目资料，生成基础职业事实。")}>
          <FileUp size={15} /> 导入资料
        </button>
        <button type="button" onClick={() => onPrompt("帮我解析这个 JD：[请在此处粘贴 JD 内容]，并生成申请包草稿。")}>
          <FileText size={15} /> 解析 JD
        </button>
        <button type="button" onClick={onRunExample}>
          <Sparkles size={15} /> 示例路径
        </button>
      </div>
    </section>
  );
}

function DesktopContextPanel({
  dataMode,
  busy,
  workflowResult,
  artifactCount,
  onPrompt,
  onRunExample,
}: {
  dataMode: DataMode;
  busy: boolean;
  workflowResult: WorkflowResult | null;
  artifactCount: number;
  onPrompt: (text: string, autoSubmit?: boolean) => void;
  onRunExample: () => void;
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
        <div className="context-action-list">
          <button type="button" onClick={() => onPrompt("导入我的简历和项目资料，生成基础职业事实。")}>
            <FileUp size={15} /> 导入资料
          </button>
          <button type="button" onClick={() => onPrompt("帮我解析这个 JD：[请在此处粘贴 JD 内容]，并生成申请包草稿。")}>
            <FileText size={15} /> 粘贴 JD
          </button>
          <button type="button" onClick={onRunExample} disabled={busy}>
            <Sparkles size={15} /> 跑示例路径
          </button>
        </div>
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
    </aside>
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
  onNotice: (message: string) => void;
  onArtifactStatus: (artifactId: string, status: string) => void;
}) {
  const data = artifact?.data ?? artifact;
  const artifactRef = data?.artifact_ref;
  const artifactId = artifactRef?.artifact_id;
  const type = artifact?.type ?? artifactRef?.artifact_type ?? "artifact";
  const packageId = data?.package_id;
  const confirmations = data?.questions_to_confirm ?? artifactRef?.questions_to_confirm ?? [];
  const hasConfirmations = Array.isArray(confirmations) && confirmations.length > 0;
  const summary = artifactSummary(type, data);
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
    const confirmed = await api<any>(`/api/artifacts/${artifactId}/confirm`, { workspace_id: workspaceId });
    onArtifactStatus(artifactId, confirmed.status ?? "confirmed");
    onNotice("产物已确认。后续导出会记录该确认状态。");
  }

  async function exportPackage() {
    if (!packageId) {
      onNotice("当前产物还不是申请包，暂不能导出。");
      return;
    }
    const result = await api<any>("/api/application/export-package", {
      workspace_id: workspaceId,
      package_id: packageId,
      formats: ["markdown", "docx"],
      artifact_version_id: currentVersionId,
    });
    const first = result.exports?.[0];
    if (first?.path) {
      const fileName = String(first.path).split("/").pop();
      window.open(`${API_BASE}/api/application/download?workspace_id=${encodeURIComponent(workspaceId)}&path=${encodeURIComponent(`exports/${fileName}`)}`, "_blank");
    }
    onNotice("申请包已导出到本地 workspace/exports，包含 Markdown 和 DOCX。");
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
    <article className={`artifact-card ${hasConfirmations ? "flagged" : ""}`}>
      <div className="card-header">
        <span className="artifact-type">{readableType(type)}</span>
        <span className="card-status">{hasConfirmations ? "需确认以提高可信度" : "已就绪"}</span>
      </div>
      <h3>{hasConfirmations ? "建议补充关键证据" : data?.title ?? data?.fit_label ?? readableType(type)}</h3>
      <CollapsibleText lines={4} showToggle={summary.length > 110}>
        <p>{summary}</p>
      </CollapsibleText>
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
        {hasConfirmations && artifactId && (
          <button className="btn-primary-action" type="button" onClick={confirm}>
            补充事实
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

function WorkflowPanel({ result, busy, workspaceId, onRunExample }: { result: WorkflowResult | null; busy: boolean; workspaceId: string; onRunExample: () => void }) {
  const completed = result?.steps?.filter((step) => step.status === "completed").length ?? 0;
  if (!result) {
    return (
      <div className="workbench-empty">
        <FileText size={48} aria-hidden="true" />
        <p>导入资料或发送任务后，求职产物将在此生成并推进。</p>
        <button className="btn-secondary-action" type="button" onClick={onRunExample} disabled={busy || !workspaceId}>
          运行示例路径
        </button>
      </div>
    );
  }
  return (
    <section className="current-goal">
      <span className="artifact-type">当前目标</span>
      <h3>{result.summary.headline ?? "生成可确认的求职材料"}</h3>
      <p>
        已完成 {completed}/{result.steps.length} 步。匹配结论：{result.summary.fit_label ?? "待分析"}；训练任务：{result.summary.training_tasks} 个。
      </p>
      {(result.exports ?? []).length > 0 && (
        <div className="export-files">
          {result.exports?.map((item) => (
            <span key={item.path}>
              {item.format.toUpperCase()} · {compactFileName(item.path, 22)}
            </span>
          ))}
        </div>
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
  onNotice: (message: string) => void;
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
  open,
  onClose,
  onRunExample,
  onNotice,
  onArtifactStatus,
}: {
  result: WorkflowResult | null;
  artifacts: any[];
  busy: boolean;
  workspaceId: string;
  open: boolean;
  onClose: () => void;
  onRunExample: () => void;
  onNotice: (message: string) => void;
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
  const [providerStatus, setProviderStatus] = useState<{ provider: string; external_calls_enabled: boolean } | null>(null);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResult | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const autorunStarted = useRef(false);
  const messagesListRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const artifacts = useMemo(() => messages.flatMap((message) => message.artifacts ?? []), [messages]);
  const workflowArtifactCount = useMemo(() => (workflowResult ? WorkflowArtifactCards({ result: workflowResult }).length : 0), [workflowResult]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const workspaceRoot = params.get("workspace_root");
    api<any>("/api/provider/status").then(setProviderStatus).catch(() => undefined);
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
  }

  function fillPrompt(text: string, autoSubmit = false) {
    setInput(text);
    inputRef.current?.focus();
    if (autoSubmit) {
      window.setTimeout(() => sendText(text), 80);
    }
  }

  async function sendText(rawText?: string) {
    const text = (rawText ?? input).trim();
    if (!text) {
      notice("还没有收到任务。你可以选择一个建议任务，或粘贴目标 JD。", "notice");
      return;
    }
    if (!workspaceId || !sessionId) {
      notice("本地工作区和会话还在初始化，请稍后再发送。", "notice");
      return;
    }
    setInput("");
    setMessages((current) => [...current, { role: "user", content: text }]);
    setBusy(true);
    try {
      const result = await api<any>("/api/chat/message", { workspace_id: workspaceId, session_id: sessionId, message: text });
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.message,
          artifacts: result.artifacts,
          tone: inferAssistantTone(result.message, result.artifacts),
        },
      ]);
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

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="eyebrow">Local-first Job Agent</span>
          <h1>求职材料工作台</h1>
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
          <StatusBadge tone="neutral" shield>
            {providerLabel(providerStatus)}
          </StatusBadge>
          <span className="mode-note">{dataMode === "example" ? "当前使用匿名示例数据" : "仅处理本地上传资料"}</span>
        </div>
      </header>

      <div className="layout-grid">
        <DesktopContextPanel
          dataMode={dataMode}
          busy={busy}
          workflowResult={workflowResult}
          artifactCount={artifacts.length + workflowArtifactCount}
          onPrompt={fillPrompt}
          onRunExample={runGuidedDemo}
        />
        <section className="workstream conversation-area" aria-label="对话区">
          <section className="conversation-plane" aria-label="对话与任务区">
            <ConversationHeader
              dataMode={dataMode}
              busy={busy}
              workflowResult={workflowResult}
              artifactCount={artifacts.length + workflowArtifactCount}
              onPrompt={fillPrompt}
              onRunExample={runGuidedDemo}
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
              <div className="composer-inner">
                <label className="btn-secondary-action upload-action" title="上传简历或项目 README">
                  <FileUp size={17} /> 上传资料
                  <input type="file" onChange={(event) => upload(event.target.files?.[0])} />
                </label>
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
                  placeholder="输入你的请求，或直接粘贴目标岗位的 JD..."
                  aria-label="对话输入框"
                  rows={2}
                />
                <button type="submit" className="btn-send" disabled={busy || !workspaceId || !sessionId} aria-label="发送任务">
                  <Send size={17} /> 发送任务
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
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          onRunExample={runGuidedDemo}
          onNotice={notice}
          onArtifactStatus={updateArtifactStatus}
        />
        <button className="mobile-fab" type="button" onClick={() => setDrawerOpen(true)} aria-expanded={drawerOpen} aria-controls="workbench-plane">
          查看推进台 {(artifacts.length > 0 || workflowResult) && <span className="badge">{artifacts.length || workflowResult?.steps.length}</span>}
        </button>
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
