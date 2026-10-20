from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from content_workflow.agents.planner import PlannerAgent
from content_workflow.agents.reviewer import ReviewerAgent
from content_workflow.agents.writer import WriterAgent
from content_workflow.state import StateStore, StepRecord, WorkflowInput, WorkflowState


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ContentWorkflow:
    def __init__(self, client: Any, runs_directory: Path):
        self.planner = PlannerAgent(client)
        self.writer = WriterAgent(client)
        self.reviewer = ReviewerAgent(client)
        self.store = StateStore(runs_directory)

    def _step(
        self,
        state: WorkflowState,
        name: str,
        action: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        record = StepRecord(name=name, status="running", started_at=_now())
        state.steps.append(record)
        state.current_step = name
        self.store.save(state)
        try:
            output = action()
        except Exception as exc:
            record.status = "failed"
            record.completed_at = _now()
            record.error = str(exc)
            self.store.save(state)
            raise
        record.status = "succeeded"
        record.completed_at = _now()
        record.output = output
        self.store.save(state)
        return output

    def run(self, request: WorkflowInput) -> WorkflowState:
        state = WorkflowState.create(request)
        self.store.save(state)
        try:
            state.outline = self._step(
                state,
                "planner",
                lambda: self.planner.run(request),
            )
            state.draft = self._step(
                state,
                "writer_initial",
                lambda: self.writer.run(request, state.outline),
            )
            state.review = self._step(
                state,
                "review_initial",
                lambda: self.reviewer.run(request, state.outline, state.draft),
            )

            if state.review["verdict"] == "approved":
                state.final_content = state.draft
                state.status = "completed"
            else:
                state.revision_count = 1
                revised_draft = self._step(
                    state,
                    "writer_revision",
                    lambda: self.writer.run(
                        request,
                        state.outline,
                        state.review["revision_instructions"],
                    ),
                )
                state.draft = revised_draft
                state.review = self._step(
                    state,
                    "review_revision",
                    lambda: self.reviewer.run(request, state.outline, revised_draft),
                )
                if state.review["verdict"] == "approved":
                    state.final_content = revised_draft
                    state.status = "completed"
                else:
                    state.final_content = revised_draft
                    state.status = "completed_with_unresolved_issues"
            state.current_step = None
        except Exception as exc:
            state.status = "failed"
            state.error = {"type": type(exc).__name__, "message": str(exc)}
            state.current_step = None
        self.store.save(state)
        return state
