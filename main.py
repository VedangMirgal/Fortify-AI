# main.py

import os
import uuid
import json
import shutil
from run_utils import get_next_run_id

from architecture_model import load_architecture_from_yaml
from orchestrator import generate_system_report, print_system_report
from report_storage import save_report
from ai_summary_agent import generate_ai_summary
from report_generator import save_text_report, generate_pdf_report
from agent_context import AgentContext
from graph_utils import generate_architecture_graph_image
from remediation_agent import RemediationAgent, suggestions_to_dict_list


def main():
    # 1) Load architecture
    arch_path = "example_architecture.yaml"
    arch = load_architecture_from_yaml(arch_path)

    # 2) Create neutral run ID (no timestamp) and run directory
        # Create neutral, sequential run ID
    run_id = get_next_run_id()
    run_dir = os.path.join("runs", f"run_{run_id}")
    os.makedirs(run_dir, exist_ok=True)

    print(f"[info] Starting analysis run: {run_id}")
    print(f"[info] Run directory: {run_dir}")


    print(f"[info] Starting analysis run: {run_id}")
    print(f"[info] Run directory: {run_dir}\n")

    # 3) Copy the architecture file into the run directory (for traceability)
    if os.path.exists(arch_path):
        shutil.copy2(arch_path, os.path.join(run_dir, "architecture.yaml"))

    # 4) Create agent context for this run
    context = AgentContext(run_id=run_id)

    # 5) Generate system report (multi-agent pipeline: failure + security + reporting)
    report = generate_system_report(arch, context=context)

    # 6) Console report (useful for local dev; can be removed later if you want only files)
    print_system_report(report)

    # 7) JSON reports

    # 7a) last_report.json in project root (latest run snapshot)
    save_report(report, "last_report.json")

    # 7b) report.json specific to this run
    json_path = os.path.join(run_dir, "report.json")
    save_report(report, json_path)
    print(f"[info] Report saved to {json_path}")

    # 8) Text / markdown report
    md_path = os.path.join(run_dir, "report.md")
    save_text_report(report, md_path)

    # 9) Architecture graph image (PNG)
    graph_basename = os.path.join(run_dir, "architecture_graph")
    graph_image_path = generate_architecture_graph_image(arch, graph_basename)

    # 10) PDF report (with graph image if available)
    pdf_path = os.path.join(run_dir, "report.pdf")
    generate_pdf_report(report, pdf_path, graph_image_path=graph_image_path)

    # 11) Remediation Agent: propose improvement suggestions
    remediation_agent = RemediationAgent()
    suggestions = remediation_agent.run(arch, report, context=context)

    # 11a) Save remediation suggestions as JSON
    remediation_json_path = os.path.join(run_dir, "remediation.json")
    with open(remediation_json_path, "w", encoding="utf-8") as f:
        json.dump(suggestions_to_dict_list(suggestions), f, indent=2)
    print(f"[info] Remediation suggestions saved to {remediation_json_path}")

    # 11b) Save a human-readable remediation text file
    remediation_txt_path = os.path.join(run_dir, "remediation.txt")
    with open(remediation_txt_path, "w", encoding="utf-8") as f:
        if not suggestions:
            f.write("No remediation suggestions generated.\n")
        else:
            for i, s in enumerate(suggestions, start=1):
                f.write(f"[{i}] ({s.category.upper()}) Target: {s.target} | Priority: {s.priority}\n")
                f.write(f"    {s.title}\n")
                f.write(f"    {s.details}\n\n")
    print(f"[info] Remediation text report saved to {remediation_txt_path}")

    # 12) AI-style summary (console + file)
    ai_summary, ai_used_llm = generate_ai_summary(report)
    print("\n\n" + "=" * 60)
    print(ai_summary)

    ai_summary_path = os.path.join(run_dir, "ai_summary.txt")
    with open(ai_summary_path, "w", encoding="utf-8") as f:
        f.write(ai_summary)
    print(f"\n[info] AI summary saved to {ai_summary_path}")

    if ai_used_llm:
        print("[info] AI summary generated using Gemini.")
    else:
        print("[info] AI summary generated using heuristic engine (no LLM).")





    # 13) Save agent context (events + shared state) to JSON
    context_path = os.path.join(run_dir, "agent_context.json")
    with open(context_path, "w", encoding="utf-8") as f:
        json.dump(context.to_dict(), f, indent=2)
    print(f"[info] Agent context saved to {context_path}")

    print(f"\n[info] Analysis run complete. All artifacts stored in: {run_dir}")


if __name__ == "__main__":
    main()
