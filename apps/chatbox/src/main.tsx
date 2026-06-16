import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertCircle, CheckCircle2, Database, Download, Edit3, FileText, FileUp, ListChecks, MessageSquare, PlayCircle, RefreshCcw, Save, Send, ShieldCheck, Sparkles } from "lucide-react";
import "./styles.css";

const API_BASE = "http://127.0.0.1:8000";

type Message = {
  role: "user" | "assistant";
  content: string;
  tone?: "normal" | "notice" | "error";
  artifacts?: unknown[];
};

type DataMode = "example" | "my_data";

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
  if (!providerStatus) return "Provider checking";
  if (providerStatus.external_calls_enabled) return "External configured";
  return `${providerStatus.provider} local`;
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

function ArtifactReadableSummary({ type, data }: { type: string; data: any }) {
  if (type === "application_package") {
    return (
      <div className="artifact-summary">
        <strong>申请包摘要</strong>
        {data?.project_description && <p>{data.project_description}</p>}
        {data?.recruiter_message && <p>{data.recruiter_message}</p>}
      </div>
    );
  }
  if (type === "match_report") {
    return (
      <div className="artifact-summary">
        <strong>匹配结论：{data?.fit_label ?? "待分析"}</strong>
        {Array.isArray(data?.strengths) && data.strengths.length > 0 && <p>优势：{data.strengths.slice(0, 2).join("；")}</p>}
        {Array.isArray(data?.gaps) && data.gaps.length > 0 && <p>缺口：{data.gaps.slice(0, 2).join("；")}</p>}
      </div>
    );
  }
  if (type === "job") {
    return (
      <div className="artifact-summary">
        <strong>{data?.title ?? "目标岗位"}</strong>
        {Array.isArray(data?.tech_stack) && data.tech_stack.length > 0 && <p>技术栈：{data.tech_stack.slice(0, 6).join(" / ")}</p>}
      </div>
    );
  }
  if (type === "career_facts") {
    const facts = Array.isArray(data?.facts) ? data.facts : [];
    return (
      <div className="artifact-summary">
        <strong>职业事实：{facts.length} 条</strong>
        {facts.slice(0, 3).map((fact: any, index: number) => (
          <p key={index}>{fact.title ?? fact.content}</p>
        ))}
      </div>
    );
  }
  if (type === "interview_prep") {
    return (
      <div className="artifact-summary">
        <strong>面试准备</strong>
        <p>问题 {data?.questions?.length ?? 0} 个，故事卡 {data?.story_cards?.length ?? 0} 张。</p>
      </div>
    );
  }
  return null;
}

function StatusPill({ tone = "neutral", children }: { tone?: "success" | "warning" | "neutral"; children: React.ReactNode }) {
  return <span className={`status-pill ${tone}`}>{children}</span>;
}

function WorkflowPanel({ result, busy, onRun }: { result: WorkflowResult | null; busy: boolean; onRun: () => void }) {
  const steps = result?.steps ?? [
    { key: "import_materials", title: "导入资料", status: "pending", summary: "导入简历和项目 README。" },
    { key: "build_profile", title: "生成事实", status: "pending", summary: "抽取职业事实、技能证据和待确认项。" },
    { key: "analyze_job", title: "分析岗位", status: "pending", summary: "解析 JD 并生成匹配报告。" },
    { key: "create_application_package", title: "申请包", status: "pending", summary: "生成可编辑、可导出的申请材料。" },
    { key: "prepare_interview", title: "面试准备", status: "pending", summary: "生成面试问题和故事卡。" },
    { key: "realtime_hint", title: "实时提示", status: "pending", summary: "文本问题转结构化提示。" },
    { key: "review_and_training", title: "复盘训练", status: "pending", summary: "从 transcript 生成复盘和训练任务。" },
  ];
  const completed = steps.filter((step) => step.status === "completed").length;
  const nextStep = steps.find((step) => step.status !== "completed");
  return (
    <section className="workflow-panel">
      <div className="workflow-head">
        <div>
          <span className="eyebrow">Guided flow</span>
          <h2>求职推进台</h2>
          <p>{result ? "已生成本次求职材料，继续检查确认项和导出文件。" : "使用 examples 跑完整路径，先得到一组可审查结果。"}</p>
        </div>
        <button className="workflow-run" onClick={onRun} disabled={busy}>
          <PlayCircle size={18} /> {busy ? "执行中" : result ? "重新运行" : "一键体验"}
        </button>
      </div>
      <div className="workflow-metrics" aria-label="工作流状态摘要">
        <div>
          <span>{completed}/{steps.length}</span>
          <strong>完成步骤</strong>
        </div>
        <div>
          <span>{result?.summary.fit_label ?? "待分析"}</span>
          <strong>匹配结论</strong>
        </div>
        <div>
          <span>{result?.exports?.length ?? 0}</span>
          <strong>导出文件</strong>
        </div>
      </div>
      <div className="workflow-steps">
        {steps.map((step, index) => (
          <div key={`${step.key}-${index}`} className={`workflow-step ${step.status}`}>
            <span>{step.status === "completed" ? <CheckCircle2 size={15} /> : index + 1}</span>
            <div>
              <strong>{step.title}</strong>
              <p>{step.summary}</p>
            </div>
          </div>
        ))}
      </div>
      {!result && nextStep && <div className="next-action">下一步：{nextStep.summary}</div>}
      {result && (
        <div className="workflow-summary">
          <div>
            <strong>本次结果</strong>
            <p>
              事实 {result.summary.facts} 条，匹配结论 {result.summary.fit_label ?? "未提供"}，训练任务 {result.summary.training_tasks} 个。
            </p>
          </div>
          <div>
            <strong>导出文件</strong>
            {(result.exports ?? []).map((item) => (
              <p key={item.path}>{item.format.toUpperCase()}：{compactFileName(item.path)}</p>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function modeLabel(mode: DataMode) {
  return mode === "example" ? "示例模式" : "我的资料";
}

function ResultRail({
  result,
  providerStatus,
  workspaceId,
  dataMode,
}: {
  result: WorkflowResult | null;
  providerStatus: { provider: string; external_calls_enabled: boolean } | null;
  workspaceId: string;
  dataMode: DataMode;
}) {
  const outputs = result?.key_outputs ?? {};
  const exports = result?.exports ?? [];
  return (
    <aside className="result-rail" aria-label="结果摘要">
      <section className="rail-section">
        <div className="rail-title"><ShieldCheck size={16} /> 运行边界</div>
        <div className="rail-pills">
          <StatusPill tone={workspaceId ? "success" : "neutral"}>{workspaceId ? "Workspace ready" : "Starting"}</StatusPill>
          <StatusPill tone={dataMode === "my_data" ? "warning" : "success"}>{modeLabel(dataMode)}</StatusPill>
          <StatusPill tone={providerStatus?.external_calls_enabled ? "warning" : "success"}>{providerLabel(providerStatus)}</StatusPill>
        </div>
        <p>默认路径使用本地 workspace。示例模式使用 examples 数据；我的资料模式只处理你上传或输入的内容。外部 provider 只在你明确配置和确认后调用。</p>
      </section>
      <section className="rail-section">
        <div className="rail-title"><ListChecks size={16} /> 本次结果</div>
        {result ? (
          <dl className="result-list">
            <div><dt>事实</dt><dd>{result.summary.facts} 条</dd></div>
            <div><dt>匹配</dt><dd>{result.summary.fit_label ?? "未提供"}</dd></div>
            <div><dt>训练</dt><dd>{result.summary.training_tasks} 个任务</dd></div>
          </dl>
        ) : (
          <p>运行一键体验后，这里会固定显示结果和导出文件。</p>
        )}
      </section>
      {outputs.match && (
        <section className="rail-section">
          <div className="rail-title"><Sparkles size={16} /> 匹配摘要</div>
          <p>{outputs.match.fit_label}</p>
          {Array.isArray(outputs.match.strengths) && <p>优势：{outputs.match.strengths.slice(0, 2).join("；")}</p>}
        </section>
      )}
      <section className="rail-section">
        <div className="rail-title"><FileText size={16} /> 导出文件</div>
        {exports.length > 0 ? (
          <ul className="export-list">
            {exports.map((item) => (
              <li key={item.path}><strong>{item.format.toUpperCase()}</strong><span title={item.path}>{compactFileName(item.path, 24)}</span></li>
            ))}
          </ul>
        ) : (
          <p>暂无导出。完成申请包步骤后会生成 Markdown 和 DOCX。</p>
        )}
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
  const packageId = data?.package_id;
  const confirmations = data?.questions_to_confirm ?? artifactRef?.questions_to_confirm ?? [];
  const [versions, setVersions] = useState<any[]>([]);
  const [currentVersionId, setCurrentVersionId] = useState<string | undefined>(artifactRef?.current_version_id);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(() => JSON.stringify(data, null, 2));

  useEffect(() => {
    if (!artifactId || !workspaceId) return;
    api<any[]>(`/api/artifacts/${artifactId}/versions?workspace_id=${encodeURIComponent(workspaceId)}`)
      .then((items) => {
        setVersions(items ?? []);
        const latestCurrent = artifactRef?.current_version_id ?? items?.[items.length - 1]?.id;
        setCurrentVersionId(latestCurrent);
      })
      .catch(() => undefined);
  }, [artifactId, workspaceId, artifactRef?.current_version_id]);

  async function confirm() {
    if (!artifactId) return;
    const confirmed = await api<any>(`/api/artifacts/${artifactId}/confirm`, { workspace_id: workspaceId });
    onArtifactStatus(artifactId, confirmed.status ?? "confirmed");
    onNotice("产物已确认。后续导出会记录该确认状态。");
  }

  async function exportMarkdown() {
    if (!packageId) return;
    const result = await api<any>("/api/application/export-package", { workspace_id: workspaceId, package_id: packageId, formats: ["markdown", "docx"], artifact_version_id: currentVersionId });
    const first = result.exports?.[0];
    if (first?.path) {
      const fileName = String(first.path).split("/").pop();
      window.open(`${API_BASE}/api/application/download?workspace_id=${encodeURIComponent(workspaceId)}&path=${encodeURIComponent(`exports/${fileName}`)}`, "_blank");
    }
    onNotice("申请包已导出到本地 workspace/exports，包含 Markdown 和 DOCX。");
  }

  async function saveEdit() {
    if (!artifactId) return;
    let content: Record<string, unknown>;
    try {
      content = JSON.parse(draft);
    } catch {
      onNotice("JSON 格式有误，未保存。");
      return;
    }
    const updated = await api<any>(`/api/artifacts/${artifactId}`, { workspace_id: workspaceId, content_json: content }, "PATCH");
    setCurrentVersionId(updated.current_version_id);
    setEditing(false);
    const items = await api<any[]>(`/api/artifacts/${artifactId}/versions?workspace_id=${encodeURIComponent(workspaceId)}`);
    setVersions(items ?? []);
    onArtifactStatus(artifactId, updated.status ?? "needs_confirmation");
    onNotice("已保存为新的 artifact version，旧版本仍可恢复。");
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
    <article className="artifact-card">
      <div className="artifact-toolbar">
        <div>
          <div className="artifact-type">{artifact?.type ?? artifactRef?.artifact_type ?? "artifact"}</div>
          {artifactRef?.status && <span className={`artifact-status ${artifactRef.status}`}>{artifactRef.status}</span>}
          {currentVersionId && <span className="artifact-version">current {currentVersionId.slice(0, 12)}</span>}
        </div>
        <div className="artifact-actions">
          {artifactId && (
            <button title="确认产物事实" onClick={confirm}>
              <CheckCircle2 size={16} />
            </button>
          )}
          {packageId && (
            <button title="导出 Markdown + DOCX" onClick={exportMarkdown}>
              <Download size={16} />
            </button>
          )}
          {artifactId && (
            <button title="编辑并保存新版本" onClick={() => setEditing((value) => !value)}>
              <Edit3 size={16} />
            </button>
          )}
          {artifactId && (
            <button title="重新生成新版本" onClick={regenerate}>
              <RefreshCcw size={16} />
            </button>
          )}
        </div>
      </div>
      {versions.length > 0 && (
        <div className="versions">
          {versions.map((version) => (
            <span key={version.id} className={version.id === currentVersionId ? "version-pill active" : "version-pill"}>
              v{version.version_number}
            </span>
          ))}
        </div>
      )}
      {confirmations.length > 0 && (
        <div className="confirmations">
          {confirmations.map((item: any, index: number) => (
            <div key={index}>
              <strong>{item.confirmation_level ?? "warning"}</strong>
              <span>{item.question ?? item}</span>
            </div>
          ))}
        </div>
      )}
      <ArtifactReadableSummary type={artifact?.type ?? artifactRef?.artifact_type ?? "artifact"} data={data} />
      {editing ? (
        <div className="artifact-editor">
          <textarea value={draft} onChange={(event) => setDraft(event.target.value)} />
          <button onClick={saveEdit}>
            <Save size={16} /> 保存为新版本
          </button>
        </div>
      ) : (
        <details className="json-details">
          <summary>查看结构化 JSON</summary>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </details>
      )}
    </article>
  );
}

function App() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "先上传简历或项目 README，再粘贴 JD。我会按事实库、岗位分析、申请包、面试准备的顺序推进。",
    },
  ]);
  const [busy, setBusy] = useState(false);
  const [dataMode, setDataMode] = useState<DataMode>("example");
  const [providerStatus, setProviderStatus] = useState<{ provider: string; external_calls_enabled: boolean } | null>(null);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResult | null>(null);
  const autorunStarted = useRef(false);
  const messagesListRef = useRef<HTMLDivElement | null>(null);

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
          if (restored.length > 0) {
            setMessages(restored);
          }
          return;
        }
      } catch {
        setMessages((current) => [...current, { role: "assistant", content: "未能恢复历史会话，已为当前 workspace 创建新会话。" }]);
      }
      const session = await api<any>("/api/chat/sessions", { workspace_id: id, title: "P0 验收路径" });
      setSessionId(session.session_id);
    });
  }, []);

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
              artifact_ref: {
                ...data.artifact_ref,
                status,
              },
            },
          };
        }),
      })),
    );
  }

  useEffect(() => {
    const messageList = messagesListRef.current;
    if (messageList) {
      messageList.scrollTop = messageList.scrollHeight;
    }
  }, [messages, busy]);

  async function sendText(rawText?: string) {
    const text = (rawText ?? input).trim();
    if (!text) {
      notice("请输入 JD、资料整理任务，或点击上传按钮导入简历 / 项目 README。", "notice");
      return;
    }
    if (!workspaceId) {
      notice("workspace 还在初始化，请稍后再发送。", "notice");
      return;
    }
    if (!sessionId) {
      notice("会话还在初始化，请稍后再发送。", "notice");
      return;
    }
    setInput("");
    setMessages((current) => [...current, { role: "user", content: text }]);
    setBusy(true);
    try {
      const result = await api<any>("/api/chat/message", { workspace_id: workspaceId, session_id: sessionId, message: text });
      setMessages((current) => [...current, { role: "assistant", content: result.message, artifacts: result.artifacts }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", tone: "error", content: formatError(error, "请求失败") }]);
    } finally {
      setBusy(false);
    }
  }

  async function send() {
    await sendText();
  }

  async function upload(file: File | undefined) {
    if (!file || !workspaceId) return;
    const form = new FormData();
    form.set("file", file);
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/api/files/upload?workspace_id=${encodeURIComponent(workspaceId)}`, {
        method: "POST",
        body: form,
      });
      const json = await response.json();
      if (!response.ok) throw new Error(json.detail?.message ?? "Upload failed");
      setDataMode("my_data");
      setMessages((current) => [
        ...current,
        { role: "assistant", content: `已导入 ${file.name}，下一步可以发送“整理资料”或粘贴 JD。`, artifacts: [{ type: "document", data: json.data }] },
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
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: `示例数据端到端体验路径已完成：${result.steps.length} 个步骤，导出 ${result.exports?.length ?? 0} 个文件。请检查推进台摘要和本地 exports。`,
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
      <aside className="sidebar">
        <div className="brand"><Sparkles size={20} /> JobPilot AI</div>
        <div className="side-block">
          <span>当前目标</span>
          <strong>拿到可确认、可导出的求职材料</strong>
        </div>
        <div className="side-steps">
          <span>路径</span>
          <ol>
            <li>导入资料</li>
            <li>分析岗位</li>
            <li>生成申请包</li>
            <li>准备面试</li>
          </ol>
        </div>
        <div className="side-note">Chatbox 只是入口，所有产物都由后端 Agent Tools 写入本地 workspace。</div>
      </aside>
      <section className="chat-panel">
        <header>
          <div>
            <span className="eyebrow">Local-first job agent</span>
            <h1>求职材料工作台</h1>
            <p>先生成可用结果，再检查事实、确认版本并导出。</p>
          </div>
          <div className="header-status">
            <StatusPill tone={workspaceId ? "success" : "neutral"}>{workspaceId ? "Workspace ready" : "Starting..."}</StatusPill>
            <StatusPill tone={dataMode === "my_data" ? "warning" : "success"}>{modeLabel(dataMode)}</StatusPill>
            {providerStatus && <StatusPill tone={providerStatus.external_calls_enabled ? "warning" : "success"}>{providerLabel(providerStatus)}</StatusPill>}
          </div>
        </header>
        <div className="workspace-grid">
          <section className="workstream conversation-area" aria-label="对话区">
            <section className="chat-thread-panel" aria-label="Chatbox 对话">
              <div className="chat-thread-head">
                <div>
                  <span className="eyebrow">Chatbox</span>
                  <h2>对话区</h2>
                  <p>从这里上传资料、粘贴 JD 或输入任务；推进台只展示阶段、产物和导出状态。</p>
                </div>
                <StatusPill tone={sessionId ? "success" : "neutral"}>{sessionId ? "Session ready" : "Session starting"}</StatusPill>
              </div>
              <div className="chat-controls" aria-label="对话模式和快捷任务">
                <div className="mode-switch" role="group" aria-label="资料模式">
                  <button className={dataMode === "example" ? "active" : ""} onClick={() => setDataMode("example")} type="button">
                    <Database size={15} /> 示例模式
                  </button>
                  <button className={dataMode === "my_data" ? "active" : ""} onClick={() => setDataMode("my_data")} type="button">
                    <FileText size={15} /> 我的资料
                  </button>
                </div>
                <div className="quick-actions" aria-label="常用任务">
                  <button type="button" onClick={() => sendText("整理资料")} disabled={busy || !workspaceId || !sessionId}>
                    <MessageSquare size={15} /> 整理资料
                  </button>
                  <button type="button" onClick={() => sendText("生成申请包")} disabled={busy || !workspaceId || !sessionId}>
                    <FileText size={15} /> 申请包
                  </button>
                  <button type="button" onClick={() => sendText("准备面试")} disabled={busy || !workspaceId || !sessionId}>
                    <ListChecks size={15} /> 面试
                  </button>
                  <button type="button" onClick={runGuidedDemo} disabled={busy || !workspaceId}>
                    <PlayCircle size={15} /> 跑示例
                  </button>
                </div>
                <p className="mode-note">
                  {dataMode === "example"
                    ? "示例模式只使用仓库 examples 数据，适合快速验收产品路径。"
                    : "我的资料模式只处理你上传或输入的内容；外部 provider 不会被默认调用。"}
                </p>
              </div>
              <div className="messages" ref={messagesListRef} role="log" aria-live="polite">
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.role} ${message.tone ?? ""}`}>
                    {message.tone === "error" && <AlertCircle className="message-icon" size={17} />}
                    <p>{message.content}</p>
                    {message.artifacts?.map((artifact, artifactIndex) => (
                      <ArtifactCard key={artifactIndex} artifact={artifact} workspaceId={workspaceId} onNotice={notice} onArtifactStatus={updateArtifactStatus} />
                    ))}
                  </div>
                ))}
                {busy && (
                  <div className="message assistant pending">
                    <p>正在处理请求...</p>
                  </div>
                )}
              </div>
              <div className="composer">
                <label className="icon-button" title="上传简历或项目 README">
                  <FileUp size={20} />
                  <input type="file" onChange={(event) => upload(event.target.files?.[0])} />
                </label>
                <textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      send();
                    }
                  }}
                  placeholder="粘贴 JD，或输入：生成申请包 / 准备面试"
                />
                <button className="send" onClick={send} disabled={busy || !workspaceId || !sessionId}>
                  <Send size={20} />
                </button>
              </div>
            </section>
          </section>
          <aside className="workbench" aria-label="求职推进台">
            <WorkflowPanel result={workflowResult} busy={busy} onRun={runGuidedDemo} />
            <ResultRail result={workflowResult} providerStatus={providerStatus} workspaceId={workspaceId} dataMode={dataMode} />
          </aside>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
