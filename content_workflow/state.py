from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import tempfile
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkflowInput:
    topic: str
    audience: str
    content_type: str
    target_length: str
    tone: str


@dataclass
class StepRecord:
    name: str
    status: str = "pending"
    started_at: str | None = None
    completed_at: str | None = None
    output: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class WorkflowState:
    run_id: str
    created_at: str
    input: WorkflowInput
    status: str = "running"
    current_step: str | None = None
    revision_count: int = 0
    steps: list[StepRecord] = field(default_factory=list)
    outline: dict[str, Any] | None = None
    draft: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
    final_content: dict[str, Any] | None = None
    error: dict[str, str] | None = None

    @classmethod
    def create(cls, workflow_input: WorkflowInput) -> "WorkflowState":
        return cls(run_id=uuid4().hex, created_at=utc_now(), input=workflow_input)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StateStore:
    def __init__(self, directory: Path):
        self.directory = directory

    def save(self, state: WorkflowState) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        if not re.fullmatch(r"[a-f0-9]{32}", state.run_id):
            raise ValueError("无效的运行 ID，拒绝写入状态文件。")
        destination = self.directory / f"{state.run_id}.json"
        serialized = json.dumps(state.to_dict(), ensure_ascii=False, indent=2)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.directory,
                prefix=f".{state.run_id}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_file.write(serialized)
                temporary_path = Path(temporary_file.name)
            temporary_path.replace(destination)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
        return destination
