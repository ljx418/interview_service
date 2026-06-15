from __future__ import annotations

import importlib
import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from services.chat.core import ChatCore
from services.storage.workspace import workspace_conn
from services.tools import jobpilot


class PiAgentUnavailableError(ValueError):
    pass


class PiAgentChatCore:
    """Adapter for a vendored PiAgent runtime.

    Supported migration targets:
    - services/piagent
    - vendor/piagent
    - installed piagent package

    The adapter intentionally keeps JobPilot domain tools and artifact writing
    outside PiAgent until a concrete source package is reviewed.
    """

    CANDIDATE_MODULES = (
        "services.piagent",
        "services.piagent.core",
        "vendor.piagent",
        "vendor.piagent.core",
        "piagent",
        "piagent.core",
    )

    def __init__(self, fallback: ChatCore, strict: bool = False, source_root: Path | None = None):
        self.fallback = fallback
        self.strict = strict
        self.project_root = Path(__file__).resolve().parents[2]
        self.source_root = source_root or self.project_root / "vendor/earendil_pi_source"
        self.node_bridge = self.project_root / "services/chat/pi_node_bridge.mjs"
        self.handler = self._load_handler()
        if self.handler is None and strict and not self._node_bridge_ready():
            raise PiAgentUnavailableError(
                "PiAgent core is not available. Put a Python-compatible source under services/piagent/vendor/piagent, "
                "or build the reviewed earendil-works/pi source so packages/ai/dist and packages/agent/dist exist."
            )

    def handle_message(self, workspace_id: str, session_id: str | None, message: str) -> dict:
        if self.handler is None:
            bridged = self._handle_via_node_bridge(workspace_id, session_id, message)
            if bridged is not None:
                if bridged.get("ok") is False:
                    if self.strict:
                        raise PiAgentUnavailableError(bridged.get("message", "PiAgent bridge failed."))
                    result = self.fallback.handle_message(workspace_id, session_id, message)
                    result["chat_core"] = {
                        "requested": "piagent",
                        "active": "keyword",
                        "reason": bridged.get("error_code", "piagent_bridge_failed").lower(),
                    }
                    return result
                if bridged.get("orchestration"):
                    return self._execute_orchestration(workspace_id, session_id, message, bridged)
                self._persist_basic_chat(workspace_id, session_id, message, str(bridged.get("message", "")))
                return {key: value for key, value in bridged.items() if key != "ok"}
            result = self.fallback.handle_message(workspace_id, session_id, message)
            result["chat_core"] = {"requested": "piagent", "active": "keyword", "reason": "piagent_unavailable"}
            return result
        result = self.handler(workspace_id=workspace_id, session_id=session_id, message=message)
        if not isinstance(result, dict):
            raise ValueError("PiAgent chat core must return a dict result.")
        return result

    def _persist_basic_chat(self, workspace_id: str, session_id: str | None, user_message: str, assistant_message: str) -> None:
        if not session_id:
            return
        conn, _ = workspace_conn(workspace_id)
        jobpilot.append_chat_message(conn, session_id, "user", user_message.strip())
        jobpilot.append_chat_message(conn, session_id, "assistant", assistant_message, [])
        conn.commit()

    def _execute_orchestration(self, workspace_id: str, session_id: str | None, user_message: str, bridged: dict) -> dict:
        orchestration = bridged.get("orchestration") or {}
        intent = orchestration.get("intent")
        conn, _ = workspace_conn(workspace_id)
        jobpilot.append_chat_message(conn, session_id, "user", user_message.strip())
        conn.commit()

        artifacts: list[dict] = []
        if intent == "extract_profile":
            facts = jobpilot.extract_facts(workspace_id)
            artifacts = [{"type": "career_facts", "data": facts}]
            assistant_message = "我先整理了你的职业事实、技能线索和待确认信息。"
        elif intent == "analyze_job":
            parsed = jobpilot.parse_jd(workspace_id, user_message.strip())
            matched = jobpilot.match_profile(workspace_id, parsed["job_id"])
            artifacts = [{"type": "job", "data": parsed}, {"type": "match_report", "data": matched}]
            assistant_message = "我已解析岗位并生成适合度分析。"
        elif intent == "create_application_package":
            job = self._latest_job(conn, workspace_id)
            if not job:
                assistant_message = "请先粘贴一个 JD，我才能生成申请包。"
            else:
                package = jobpilot.create_application_package(workspace_id, job["id"])
                artifacts = [{"type": "application_package", "data": package}]
                assistant_message = "申请包已生成，请先确认事实再导出。"
        elif intent == "prepare_interview":
            job = self._latest_job(conn, workspace_id)
            if not job:
                assistant_message = "请先分析目标岗位，再生成面试准备。"
            else:
                prep = jobpilot.prepare_interview(workspace_id, job["id"])
                artifacts = [{"type": "interview_prep", "data": prep}]
                assistant_message = "面试准备包和故事卡已生成。"
        else:
            assistant_message = str(bridged.get("message") or "我已收到请求，但当前没有可执行的 JobPilot 编排计划。")

        artifact_refs = [artifact["data"].get("artifact_ref") for artifact in artifacts if artifact.get("data", {}).get("artifact_ref")]
        jobpilot.append_chat_message(conn, session_id, "assistant", assistant_message, artifact_refs)
        conn.commit()
        return {
            "message": assistant_message,
            "artifacts": artifacts,
            "chat_core": bridged.get("chat_core"),
            "orchestration": orchestration,
        }

    def _latest_job(self, conn, workspace_id: str):
        return conn.execute("SELECT id FROM job WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()

    def _load_handler(self) -> Callable[..., dict] | None:
        for module_name in self.CANDIDATE_MODULES:
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            handler = self._handler_from_module(module)
            if handler is not None:
                return handler
        return None

    def _node_bridge_ready(self) -> bool:
        return (
            self.node_bridge.exists()
            and (self.source_root / "packages/ai/dist/index.js").exists()
            and (self.source_root / "packages/agent/dist/index.js").exists()
        )

    def _handle_via_node_bridge(self, workspace_id: str, session_id: str | None, message: str) -> dict | None:
        if not self.node_bridge.exists() or not self.source_root.exists():
            return None
        env = os.environ.copy()
        env["JOBPILOT_PI_SOURCE_ROOT"] = str(self.source_root)
        payload = json.dumps({"workspace_id": workspace_id, "session_id": session_id, "message": message})
        completed = subprocess.run(
            ["node", str(self.node_bridge)],
            input=payload,
            text=True,
            capture_output=True,
            timeout=15,
            env=env,
            check=False,
        )
        if not completed.stdout.strip():
            return {"ok": False, "error_code": "PI_AGENT_BRIDGE_FAILED", "message": completed.stderr.strip() or "Pi bridge produced no output."}
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {"ok": False, "error_code": "PI_AGENT_BRIDGE_BAD_OUTPUT", "message": completed.stdout[:500]}

    def _handler_from_module(self, module: Any) -> Callable[..., dict] | None:
        direct = getattr(module, "handle_message", None)
        if callable(direct):
            return direct

        core_cls = getattr(module, "PiAgentCore", None)
        if core_cls is not None:
            core = core_cls()
            method = getattr(core, "handle_message", None)
            if callable(method):
                return method

        create_core = getattr(module, "create_core", None)
        if callable(create_core):
            core = create_core()
            method = getattr(core, "handle_message", None)
            if callable(method):
                return method

        return None
