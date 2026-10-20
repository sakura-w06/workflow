import argparse
import sys

from content_workflow.config import PROJECT_ROOT, load_settings
from content_workflow.model_client import BailianClient
from content_workflow.state import WorkflowInput
from content_workflow.workflow import ContentWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="content-workflow",
        description="按规划、写作、审校顺序运行内容创作 Workflow。",
    )
    parser.add_argument("topic", help="创作主题")
    parser.add_argument("--audience", default="普通读者", help="目标读者")
    parser.add_argument("--content-type", default="文章", help="内容类型")
    parser.add_argument("--length", default="约 800 字", dest="target_length", help="期望长度")
    parser.add_argument("--tone", default="清晰易懂", help="写作语气")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    topic = args.topic.strip()
    if not topic:
        print("主题不能为空。", file=sys.stderr)
        return 2

    try:
        settings = load_settings()
        client = BailianClient(settings)
    except (ValueError, ImportError) as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    request = WorkflowInput(
        topic=topic,
        audience=args.audience,
        content_type=args.content_type,
        target_length=args.target_length,
        tone=args.tone,
    )
    workflow = ContentWorkflow(client, PROJECT_ROOT / "data" / "runs")
    print("开始执行：规划 Agent → 写作 Agent → 审校 Agent")
    state = workflow.run(request)
    run_path = PROJECT_ROOT / "data" / "runs" / f"{state.run_id}.json"

    if state.status == "failed":
        print(f"工作流失败（步骤：{state.steps[-1].name if state.steps else '初始化'}）：")
        print(state.error["message"] if state.error else "未知错误")
        print(f"运行记录：{run_path}")
        return 1

    print(f"\n标题：{state.final_content['title']}\n")
    print(state.final_content["content"])
    if state.status == "completed":
        print(f"\n审校通过。运行记录：{run_path}")
        return 0

    print("\n修改一次后仍有未解决的审校意见：")
    for issue in state.review["issues"]:
        print(f"- {issue}")
    print(f"运行记录：{run_path}")
    return 2
