const form = document.querySelector("#composer");
const input = document.querySelector("#message");
const timeline = document.querySelector("#timeline");
const emptyState = document.querySelector("#empty-state");
const artifactList = document.querySelector("#artifact-list");
const workbenchEmpty = document.querySelector("#workbench-empty");

function escapeHtml(value) {
  return value.replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function appendMessage(className, html) {
  if (emptyState) emptyState.hidden = true;
  const article = document.createElement("article");
  article.className = `message ${className}`;
  article.innerHTML = html;
  timeline.appendChild(article);
  article.scrollIntoView({ block: "end", behavior: "smooth" });
  return article;
}

function revealWorkbench() {
  if (artifactList) artifactList.hidden = false;
  if (workbenchEmpty) workbenchEmpty.hidden = true;
}

document.querySelectorAll(".prompt-card").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt || "";
    input.focus();
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();

  if (!text) {
    appendMessage(
      "assistant",
      "<p>还没有收到任务。你可以选择一个建议任务，或粘贴目标 JD。</p>"
    );
    return;
  }

  appendMessage("user", `<p>${escapeHtml(text)}</p>`);
  input.value = "";

  const loading = appendMessage(
    "assistant loading",
    `<strong>我正在规划执行步骤</strong>
     <ol class="thinking-steps">
       <li>检查是否已有简历、项目和 JD。</li>
       <li>准备对比岗位要求和项目证据。</li>
       <li>生成可确认的产物草稿。</li>
     </ol>`
  );

  setTimeout(() => {
    loading.remove();
    revealWorkbench();
    appendMessage(
      "assistant plan",
      `<strong>行动计划</strong>
       <ol>
         <li>解析 JD，提取核心技能和加分项。</li>
         <li>对比现有项目经历，标出缺少证据的内容。</li>
         <li>已把草稿和待确认项放到右侧推进台。</li>
       </ol>`
    );
  }, 900);
});
