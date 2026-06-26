const app = document.querySelector(".app-shell");
const timeline = document.querySelector("#timeline");
const emptyState = document.querySelector("#empty-state");
const input = document.querySelector("#message-input");
const workbench = document.querySelector(".workbench");
const drawerMask = document.querySelector("#drawer-mask");
const drawerTrigger = document.querySelector("#mobile-workbench-trigger");
const workbenchBody = document.querySelector("#workbench-body");
const stateSelect = document.querySelector("#state-select");
const variantSelect = document.querySelector("#variant-select");

const stateData = {
  empty: {
    contextTitle: "准备求职材料",
    contextCopy: "先选择一个建议任务，或直接描述你的求职目标。默认只使用本地 mock 路径。",
    progress: "8%",
    progressText: "等待任务",
    artifacts: 0,
    summary: "可以自由追问、补充偏好、导入资料、粘贴 JD，或直接运行示例路径。",
  },
  free: {
    contextTitle: "讨论求职方向",
    contextCopy: "普通自由对话不会生成产物。系统只整理思路，不写 artifact。",
    progress: "14%",
    progressText: "自由对话",
    artifacts: 0,
    summary: "已完成两轮自由追问，当前仍为 0 个产物。",
  },
  status: {
    contextTitle: "查看当前进展",
    contextCopy: "workspace 暂无产物，下一步可以上传资料或粘贴目标 JD。",
    progress: "12%",
    progressText: "状态查询",
    artifacts: 0,
    summary: "系统基于当前 workspace 返回状态摘要。",
  },
  loading: {
    contextTitle: "正在处理材料",
    contextCopy: "系统正在读取资料、对比 JD、准备生成可确认的草稿。",
    progress: "42%",
    progressText: "处理中",
    artifacts: 0,
    summary: "Thinking 状态显示具体执行步骤，避免用户误判卡死。",
  },
  demo: {
    contextTitle: "示例路径已完成",
    contextCopy: "已完成 9/9 步。下一步检查待确认事实，再导出或替换成真实资料。",
    progress: "100%",
    progressText: "9/9 完成",
    artifacts: 4,
    summary: "示例数据已生成申请材料闭环。",
  },
  artifact: {
    contextTitle: "职业事实已生成",
    contextCopy: "显式工具请求已生成 career_facts，Workbench 主体必须展示一致产物卡。",
    progress: "28%",
    progressText: "1 个产物",
    artifacts: 1,
    summary: "新原型修正计数为 1 但主体仍空的问题。",
  },
  error: {
    contextTitle: "需要补充资料",
    contextCopy: "当前缺少简历、项目或 JD。错误状态必须给出恢复动作。",
    progress: "8%",
    progressText: "待补充",
    artifacts: 0,
    summary: "错误不伪装成成功，提供明确恢复动作。",
  },
};

function setText(selector, value) {
  const node = document.querySelector(selector);
  if (node) node.textContent = value;
}

function setArtifacts(count) {
  setText("#metric-artifacts", String(count));
  setText("#mini-artifacts", String(count));
  setText("#artifact-count", `${count} 个产物`);
  setText("#mobile-count", String(count));
}

function message(role, content, tone = "") {
  return `<article class="message ${role} ${tone}">${content}</article>`;
}

function renderMessages(state) {
  if (state === "empty") {
    emptyState.hidden = false;
    timeline.querySelector(".message-stack")?.remove();
    return;
  }
  emptyState.hidden = true;
  const stack = document.createElement("div");
  stack.className = "message-stack";
  const content = {
    free: [
      message("user", "我还没有 JD，先聊聊求职方向和偏好。"),
      message("assistant", "可以。你可以先明确目标岗位、城市和准备周期。我会先帮你整理思路，不会生成产物，也不会外呼真实 provider。", "plan"),
      message("user", "继续，我下一步应该先补 React 还是项目经历？"),
      message("assistant", "建议先补项目经历。React 技能最好绑定到具体项目、职责和结果上，否则申请包会缺少可信证据。"),
    ],
    status: [
      message("user", "当前进展如何？有哪些产物？"),
      message("assistant", "当前还没有生成求职产物。你可以先上传简历/项目资料，或直接粘贴目标 JD；如果只是想讨论方向，也可以继续问我。"),
    ],
    loading: [
      message("user", "帮我解析这个 JD，并生成申请包草稿。"),
      message("assistant", `<strong>正在处理任务</strong><ol class="thinking-list"><li>检查 workspace 中已有简历和项目资料。</li><li>提取 JD 中的硬性要求和加分项。</li><li>准备生成可确认的申请包草稿。</li></ol>`, "plan"),
    ],
    demo: [
      message("assistant", "示例路径已完成：9 个步骤，导出 2 个文件。请检查右侧推进台里的待确认项和导出状态。", "plan"),
    ],
    artifact: [
      message("user", "请整理资料，生成职业事实。"),
      message("assistant", "我先整理了你的职业事实、技能线索和待确认信息。右侧已经生成职业事实产物卡。", "plan"),
    ],
    error: [
      message("user", "生成申请包。"),
      message("assistant", `<strong>还不能生成申请包</strong><p>当前缺少目标 JD 或可引用的项目资料。</p><div class="card-actions"><button class="primary-btn" data-action="jd" type="button">粘贴 JD</button><button class="secondary-btn" data-action="upload" type="button">补充资料</button><button class="secondary-btn" data-action="demo" type="button">跑示例路径</button></div>`, "error"),
    ],
  }[state] || [];
  stack.innerHTML = content.join("");
  timeline.querySelector(".message-stack")?.remove();
  timeline.appendChild(stack);
  timeline.scrollTop = timeline.scrollHeight;
}

function emptyWorkbench() {
  return `<section class="workbench-empty"><h3>还没有生成产物</h3><p>这里会显示职业事实、岗位解析、匹配报告、申请包草稿、待确认项和导出状态。</p><ol><li>导入资料或粘贴 JD</li><li>生成申请包草稿</li><li>确认事实并导出</li></ol><button class="primary-btn" data-action="demo" type="button">运行示例路径</button></section>`;
}

function artifactCards(state) {
  if (state === "demo") {
    return `<section class="goal-card"><div class="goal-top"><span class="type-label">当前目标</span><span class="ready">示例闭环已生成</span></div><h3>P2 guided demo flow completed</h3><p>已完成 9/9 步。下一步先检查待确认事实，再导出或替换成你的真实资料。</p><div class="stat-grid"><span><strong>9/9</strong><small>流程</small></span><span><strong>12</strong><small>事实</small></span><span><strong>2</strong><small>导出</small></span><span><strong>3</strong><small>训练</small></span></div></section>
    <article class="artifact-card"><div class="card-top"><span class="type-label">岗位解析</span><span class="ready">已就绪</span></div><h3>Junior Frontend Developer</h3><p>核心要求是 React、JavaScript、HTML/CSS、Git；TypeScript 和 Testing 是加分项。</p><div class="card-actions"><button class="secondary-btn" type="button">查看来源</button></div></article>
    <article class="artifact-card flagged"><div class="card-top"><span class="type-label">申请包草稿</span><span class="needs">需确认</span></div><h3>建议补充关键证据</h3><p>导出前建议确认项目上线状态、个人负责范围和可量化结果。</p><ul class="confirm-list"><li>TodoPlus 是否已上线或可演示？</li><li>是否有性能、用户数或测试覆盖指标？</li></ul><div class="card-actions"><button class="primary-btn" type="button">补充事实</button><button class="secondary-btn" type="button">预览草稿</button><button class="secondary-btn" type="button">导出</button></div></article>`;
  }
  if (state === "artifact") {
    return `<article class="artifact-card flagged"><div class="card-top"><span class="type-label">职业事实</span><span class="needs">需确认</span></div><h3>职业事实与技能线索</h3><p>已根据明确工具请求生成 career_facts。这里修正了旧界面“计数为 1、主体仍空”的不一致。</p><ul class="fact-list"><li>React 和 JavaScript 可作为前端目标岗位技能线索。</li><li>项目经历需要补充本人负责范围。</li><li>导出前应确认量化指标是否真实存在。</li></ul><ul class="confirm-list"><li>请确认项目是否已部署上线。</li><li>请补充可量化结果，例如性能、用户数、测试覆盖或交付周期。</li><li>请确认每项技能是否由你本人实现过。</li></ul><div class="version-row"><span>v1</span><span>needs_confirmation</span></div><div class="card-actions"><button class="primary-btn" type="button">补充事实</button><button class="secondary-btn" type="button">查看来源</button><button class="secondary-btn" type="button">重新生成</button></div></article>`;
  }
  if (state === "loading") {
    return `<article class="artifact-card"><div class="card-top"><span class="type-label">执行中</span><span class="needs">处理中</span></div><h3>正在准备可确认产物</h3><p>系统正在检查已有资料和目标岗位。完成后，这里会显示产物卡，而不是保留空状态。</p></article>`;
  }
  if (state === "error") {
    return `<article class="artifact-card flagged"><div class="card-top"><span class="type-label">阻塞项</span><span class="blocked">缺资料</span></div><h3>还缺目标 JD 或项目资料</h3><p>生成申请包前需要至少一个目标 JD 和可引用项目经历。</p><div class="card-actions"><button class="primary-btn" data-action="jd" type="button">粘贴 JD</button><button class="secondary-btn" data-action="upload" type="button">上传资料</button></div></article>`;
  }
  return emptyWorkbench();
}

function renderWorkbench(state) {
  workbenchBody.innerHTML = artifactCards(state);
}

function applyState(state) {
  const data = stateData[state] || stateData.empty;
  app.dataset.state = state;
  setText("#context-title", data.contextTitle);
  setText("#context-copy", data.contextCopy);
  setText("#metric-progress", data.progressText);
  setText("#conversation-summary", data.summary);
  setText("#mini-status", state === "loading" ? "处理中" : "可继续");
  document.querySelector("#progress-bar").style.width = data.progress;
  setArtifacts(data.artifacts);
  renderMessages(state);
  renderWorkbench(state);
  if (stateSelect && stateSelect.value !== state) stateSelect.value = state;
}

function runAction(action) {
  const map = {
    upload: "请导入我的简历和项目资料，生成基础职业事实。",
    jd: "帮我解析这个 JD：[请在此处粘贴 JD 内容]，并生成申请包草稿。",
    interview: "基于当前项目经历准备面试 STAR 故事和追问练习。",
  };
  if (action === "free") return applyState("free");
  if (action === "demo") return applyState("demo");
  if (action === "artifact") return applyState("artifact");
  if (map[action]) {
    input.value = map[action];
    input.focus();
  }
}

document.addEventListener("click", (event) => {
  const actionNode = event.target.closest("[data-action]");
  if (actionNode) runAction(actionNode.dataset.action);
  if (event.target === drawerMask) closeDrawer();
});

document.querySelector("#composer").addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return applyState("error");
  if (text.includes("进展") || text.includes("产物")) applyState("status");
  else if (text.includes("职业事实") || text.includes("整理资料")) applyState("artifact");
  else if (text.includes("JD") || text.includes("申请包")) applyState("loading");
  else applyState("free");
  input.value = "";
});

function openDrawer() {
  workbench.classList.add("is-open");
  drawerMask.hidden = false;
  drawerTrigger.setAttribute("aria-expanded", "true");
}

function closeDrawer() {
  workbench.classList.remove("is-open");
  drawerMask.hidden = true;
  drawerTrigger.setAttribute("aria-expanded", "false");
}

drawerTrigger.addEventListener("click", openDrawer);

document.querySelector(".tweaks-toggle").addEventListener("click", (event) => {
  const panel = document.querySelector(".tweaks-panel");
  const willOpen = panel.hidden;
  panel.hidden = !willOpen;
  event.currentTarget.setAttribute("aria-expanded", String(willOpen));
});

stateSelect.addEventListener("change", (event) => applyState(event.target.value));
variantSelect.addEventListener("change", (event) => {
  app.dataset.variant = event.target.value;
});

applyState("empty");
