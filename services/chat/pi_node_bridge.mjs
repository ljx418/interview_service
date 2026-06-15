import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

function readStdin() {
	return new Promise((resolveRead) => {
		let data = "";
		process.stdin.setEncoding("utf8");
		process.stdin.on("data", (chunk) => {
			data += chunk;
		});
		process.stdin.on("end", () => resolveRead(data));
	});
}

function write(payload, exitCode = 0) {
	process.stdout.write(`${JSON.stringify(payload)}\n`);
	process.exit(exitCode);
}

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../..");
const sourceRoot = process.env.JOBPILOT_PI_SOURCE_ROOT || resolve(root, "vendor/earendil_pi_source");
const agentDist = resolve(sourceRoot, "packages/agent/dist/index.js");
const aiDist = resolve(sourceRoot, "packages/ai/dist/index.js");

const raw = await readStdin();
let input;
try {
	input = raw ? JSON.parse(raw) : {};
} catch (error) {
	write({ ok: false, error_code: "INVALID_BRIDGE_INPUT", message: "Bridge input must be JSON." }, 2);
}

if (!existsSync(sourceRoot)) {
	write({ ok: false, error_code: "PI_SOURCE_NOT_FOUND", message: `Pi source root not found: ${sourceRoot}` }, 2);
}

if (!existsSync(aiDist) || !existsSync(agentDist)) {
	write({
		ok: false,
		error_code: "PI_AGENT_NOT_BUILT",
		message: "Pi source is present but packages/ai and packages/agent dist outputs are missing.",
		source_root: sourceRoot,
		required_files: [aiDist, agentDist],
	}, 2);
}

try {
	const [{ Agent }, { createAssistantMessageEventStream }, { Type }] = await Promise.all([
		import(agentDist),
		import(resolve(sourceRoot, "packages/ai/dist/utils/event-stream.js")),
		import(resolve(sourceRoot, "node_modules/typebox/build/index.mjs")),
	]);
	if (!Agent) {
		write({ ok: false, error_code: "PI_AGENT_EXPORT_MISSING", message: "Built Pi agent package does not export Agent." }, 2);
	}
	const message = input.message || "";
	const intent = detectIntent(message);
	const plan = buildPlan(intent, message);
	const model = {
		id: "jobpilot-local-basic",
		name: "JobPilot Local Basic",
		api: "jobpilot-local",
		provider: "jobpilot",
		baseUrl: "",
		reasoning: false,
		input: ["text"],
		cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
		contextWindow: 8192,
		maxTokens: 512,
	};
	const orchestrationTool = {
		label: "JobPilot Orchestrator",
		name: "jobpilot_orchestrate",
		description: "Select the JobPilot domain workflow that Python should execute inside the local workspace.",
		parameters: Type.Object({
			intent: Type.String({ description: "JobPilot orchestration intent" }),
			message: Type.String({ description: "Original user message" }),
		}),
		executionMode: "sequential",
		execute: async (_toolCallId, args) => {
			const selected = buildPlan(args.intent, args.message);
			return {
				content: [{ type: "text", text: selected.assistant_message }],
				details: selected,
				terminate: true,
			};
		},
	};
	const streamFn = () => {
		const stream = createAssistantMessageEventStream();
		queueMicrotask(() => {
			if (intent !== "basic_chat") {
				pushToolCall(stream, model, intent, message);
				return;
			}
			const reply = buildReply(message);
			const baseMessage = {
				role: "assistant",
				content: [{ type: "text", text: "" }],
				api: model.api,
				provider: model.provider,
				model: model.id,
				usage: zeroUsage(),
				stopReason: "stop",
				timestamp: Date.now(),
			};
			const finalMessage = {
				...baseMessage,
				content: [{ type: "text", text: reply }],
			};
			stream.push({ type: "start", partial: baseMessage });
			stream.push({ type: "text_start", contentIndex: 0, partial: baseMessage });
			stream.push({ type: "text_delta", contentIndex: 0, delta: reply, partial: finalMessage });
			stream.push({ type: "text_end", contentIndex: 0, content: reply, partial: finalMessage });
			stream.push({ type: "done", reason: "stop", message: finalMessage });
		});
		return stream;
	};
	const agent = new Agent({
		initialState: {
			systemPrompt:
				"You are JobPilot's chat orchestrator. For business requests, call jobpilot_orchestrate. For greetings or simple questions, answer briefly in Chinese.",
			model,
			tools: [orchestrationTool],
			messages: [],
		},
		streamFn,
		toolExecution: "sequential",
		sessionId: input.session_id,
	});
	await agent.prompt(message);
	const toolResultMessage = agent.state.messages
		.slice()
		.reverse()
		.find((stateMessage) => stateMessage.role === "toolResult" && stateMessage.toolName === "jobpilot_orchestrate");
	if (toolResultMessage?.details) {
		write({
			ok: true,
			message: toolResultMessage.details.assistant_message || plan.assistant_message,
			artifacts: [],
			orchestration: {
				...toolResultMessage.details,
				source: "pi_agent_tool_call",
			},
			chat_core: {
				requested: "piagent",
				active: "piagent_business_orchestrator",
				source_root: sourceRoot,
				workspace_id: input.workspace_id,
				session_id: input.session_id,
				tool_bridge: "python_jobpilot_domain_tools",
			},
		});
	}
	const assistantMessage = agent.state.messages
		.slice()
		.reverse()
		.find((message) => message.role === "assistant");
	const text = extractText(assistantMessage) || buildReply(message);
	write({
		ok: true,
		message: text,
		artifacts: [],
		chat_core: {
			requested: "piagent",
			active: "piagent_core_basic",
			source_root: sourceRoot,
			workspace_id: input.workspace_id,
			session_id: input.session_id,
			tool_bridge: "not_enabled",
		},
	});
} catch (error) {
	write({
		ok: false,
		error_code: "PI_AGENT_IMPORT_FAILED",
		message: error instanceof Error ? error.message : String(error),
		source_root: sourceRoot,
	}, 2);
}

function pushToolCall(stream, model, intent, message) {
	const toolCall = {
		type: "toolCall",
		id: "call_jobpilot_orchestrate_1",
		name: "jobpilot_orchestrate",
		arguments: { intent, message },
	};
	const baseMessage = {
		role: "assistant",
		content: [],
		api: model.api,
		provider: model.provider,
		model: model.id,
		usage: zeroUsage(),
		stopReason: "toolUse",
		timestamp: Date.now(),
	};
	const finalMessage = {
		...baseMessage,
		content: [toolCall],
	};
	stream.push({ type: "start", partial: baseMessage });
	stream.push({ type: "toolcall_start", contentIndex: 0, partial: baseMessage });
	stream.push({ type: "toolcall_end", contentIndex: 0, toolCall, partial: finalMessage });
	stream.push({ type: "done", reason: "toolUse", message: finalMessage });
}

function zeroUsage() {
	return {
		input: 0,
		output: 0,
		cacheRead: 0,
		cacheWrite: 0,
		totalTokens: 0,
		cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
	};
}

function extractText(message) {
	if (!message || !Array.isArray(message.content)) return "";
	return message.content
		.filter((item) => item?.type === "text")
		.map((item) => item.text || "")
		.join("");
}

function buildReply(message) {
	const text = String(message || "").trim();
	if (!text) return "我在。你可以直接描述目标岗位、项目经历，或问我下一步怎么推进。";
	if (/你好|hello|hi/i.test(text)) return "你好，我是 JobPilot 的基础聊天核心。现在已通过 Pi Agent Core 处理普通对话。";
	if (/你是谁|介绍/.test(text)) return "我是 JobPilot 的本地求职助手。当前基础对话由 Pi Agent Core 承载，求职产物生成仍由 JobPilot 工具链负责。";
	return `我理解你的意思：${text}。当前这是 Pi Agent Core 的基础对话模式，可以继续补充背景或目标。`;
}

function detectIntent(message) {
	const text = String(message || "").trim();
	const lower = text.toLowerCase();
	if (!text) return "basic_chat";
	if (/申请包|求职信|cover letter|resume package|application package|package/i.test(text)) return "create_application_package";
	if (/面试准备|模拟面试|interview prep|prepare interview/i.test(text)) return "prepare_interview";
	if (/job description|\bjd\b|岗位|职位描述|招聘要求|must[- ]?have|nice[- ]?to[- ]?have/i.test(text)) return "analyze_job";
	if (/简历|项目|经历|资料|整理|profile|resume|readme|career/i.test(text)) return "extract_profile";
	if (/你好|hello|hi|你是谁|介绍/i.test(lower)) return "basic_chat";
	return "extract_profile";
}

function buildPlan(intent, message) {
	const normalized = ["extract_profile", "analyze_job", "create_application_package", "prepare_interview", "basic_chat"].includes(intent)
		? intent
		: "extract_profile";
	const plans = {
		extract_profile: {
			intent: "extract_profile",
			assistant_message: "我会先整理你的职业事实、技能线索和待确认信息。",
			tool_plan: [
				{
					tool: "profile.extract_facts",
					python_function: "services.tools.jobpilot.extract_facts",
					reason: "从本地 workspace 文档生成可追溯职业事实和技能证据。",
				},
			],
			requires_python_execution: true,
		},
		analyze_job: {
			intent: "analyze_job",
			assistant_message: "我会解析这份 JD，并基于你的资料生成岗位适合度分析。",
			tool_plan: [
				{ tool: "job.parse_jd", python_function: "services.tools.jobpilot.parse_jd", reason: "抽取岗位要求、资历和关键词。" },
				{ tool: "job.match_profile", python_function: "services.tools.jobpilot.match_profile", reason: "将岗位要求与本地职业事实、技能证据和项目卡匹配。" },
			],
			requires_python_execution: true,
		},
		create_application_package: {
			intent: "create_application_package",
			assistant_message: "我会基于最近一次岗位分析生成申请包，并保留待确认事项。",
			tool_plan: [
				{
					tool: "application.create_package",
					python_function: "services.tools.jobpilot.create_application_package",
					reason: "生成可编辑、可导出的本地申请包。",
				},
			],
			requires_python_execution: true,
		},
		prepare_interview: {
			intent: "prepare_interview",
			assistant_message: "我会基于最近一次岗位分析生成面试准备包和故事卡。",
			tool_plan: [
				{ tool: "interview.prepare", python_function: "services.tools.jobpilot.prepare_interview", reason: "生成面试重点、回答结构和可追溯故事卡。" },
			],
			requires_python_execution: true,
		},
		basic_chat: {
			intent: "basic_chat",
			assistant_message: buildReply(message),
			tool_plan: [],
			requires_python_execution: false,
		},
	};
	return plans[normalized];
}
