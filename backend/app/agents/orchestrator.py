import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from app.agents.base_agent import AgentResult
from app.agents.case_agent import CaseAgent
from app.agents.content_guard_agent import ContentGuardAgent
from app.agents.exercise_agent import ExerciseAgent
from app.agents.extended_reading_agent import ExtendedReadingAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.lecture_agent import LectureAgent
from app.agents.mindmap_agent import MindMapAgent
from app.agents.verifier_agent import VerifierAgent
from app.agents.video_storyboard_agent import VideoStoryboardAgent
from app.services.llm_client import LLMClient, get_llm_client

logger = logging.getLogger(__name__)

RESOURCE_AGENTS = [
    ("lecture", LectureAgent),
    ("mindmap", MindMapAgent),
    ("case", CaseAgent),
    ("video_storyboard", VideoStoryboardAgent),
    ("exercise", ExerciseAgent),
    ("extended_reading", ExtendedReadingAgent),
]


class Orchestrator:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or get_llm_client()
        # 并行执行时保护 trace 列表的并发读写
        self._trace_lock = threading.Lock()

    def generate_resources(
        self,
        profile: dict | None = None,
        knowledge_context: dict | None = None,
        on_trace: Any = None,
    ) -> dict:
        trace: list[dict] = []
        resources: list[dict] = []

        knowledge_result = self._run_agent(
            KnowledgeAgent(self.llm), trace, on_trace,
            knowledge_context=knowledge_context,
        )
        context = knowledge_result.data if knowledge_result.success else (knowledge_context or {})

        # 6 个资源 Agent 并行生成（LLM 调用为 I/O 密集型，并行可显著降低总耗时）
        def _run_one(resource_type: str, agent_cls: type) -> dict | None:
            result = self._run_agent(
                agent_cls(self.llm), trace, on_trace,
                profile=profile, knowledge_context=context,
            )
            if not result.success:
                return None
            content = result.data
            if isinstance(content, str):
                content = {"content": content}
            return {
                "resource_type": resource_type,
                "content": content,
                "confidence": result.confidence,
                "warnings": list(result.warnings),
            }

        with ThreadPoolExecutor(max_workers=len(RESOURCE_AGENTS)) as pool:
            futures = [
                pool.submit(_run_one, rtype, acls)
                for rtype, acls in RESOURCE_AGENTS
            ]
            # 按 RESOURCE_AGENTS 顺序收集结果，保持稳定展示顺序
            results_by_type = {}
            for fut, (rtype, _) in zip(futures, RESOURCE_AGENTS):
                try:
                    res = fut.result()
                except Exception as exc:
                    logger.error("Resource agent %s crashed: %s", rtype, exc)
                    res = None
                if res:
                    results_by_type[rtype] = res
            for rtype, _ in RESOURCE_AGENTS:
                if rtype in results_by_type:
                    resources.append(results_by_type[rtype])

        # Verifier 与 ContentGuard 对每条资源并行校验（两类检查相互独立）
        verifier = VerifierAgent(self.llm)
        guard = ContentGuardAgent(self.llm)

        def _verify_and_guard(resource: dict) -> None:
            v_result = self._run_agent(
                verifier, trace, on_trace,
                resource=resource, knowledge_context=context,
            )
            if v_result.success and isinstance(v_result.data, dict):
                if not v_result.data.get("consistent", True):
                    resource["warnings"].append("factual_inconsistency")
                    resource["confidence"] = "low"

            g_result = self._run_agent(
                guard, trace, on_trace,
                resource=resource,
            )
            if g_result.success and isinstance(g_result.data, dict):
                if g_result.data.get("blocked", False):
                    resource["content"] = {"content": "该内容已被安全过滤。"}
                    resource["warnings"].append("safety_blocked")
                    resource["confidence"] = "low"

        with ThreadPoolExecutor(max_workers=min(4, max(1, len(resources)))) as pool:
            list(pool.map(_verify_and_guard, resources))

        return {"resources": resources, "trace": trace}

    def _run_agent(self, agent, trace: list, on_trace, **kwargs) -> AgentResult:
        trace_item = {
            "agent_name": agent.name,
            "status": "running",
            "started_at": datetime.now(),
            "finished_at": None,
            "duration_ms": 0,
            "warnings": [],
            "confidence": None,
        }
        with self._trace_lock:
            trace.append(trace_item)
        if on_trace:
            on_trace(trace_item)

        try:
            result = agent.run(**kwargs)
        except Exception as exc:
            logger.error("Agent %s crashed: %s", agent.name, exc)
            result = AgentResult(success=False, data={}, error=str(exc), warnings=["agent_crashed"])

        trace_item["status"] = "success" if result.success else "failed"
        trace_item["finished_at"] = datetime.now()
        trace_item["duration_ms"] = result.duration_ms
        trace_item["warnings"] = result.warnings
        trace_item["confidence"] = result.confidence
        if on_trace:
            on_trace(trace_item)

        return result
