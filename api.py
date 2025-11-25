# api.py

import os
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from architecture_model import load_architecture_from_yaml
from orchestrator import generate_system_report
from agent_context import AgentContext
from remediation_agent import RemediationAgent, suggestions_to_dict_list
from report_storage import save_report
from report_generator import save_text_report, generate_pdf_report
from graph_utils import generate_architecture_graph_image
from ai_summary_agent import generate_ai_summary
from run_utils import get_next_run_id

app = FastAPI(title="System Resilience & Security Agent API")


@app.get("/healthz")
async def healthz():
  return {"status": "ok"}


# Allow Vite dev server to call this API (and later, you can add your deployed frontend origin)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://fortify-ai-1.onrender.com",  # ✅ your Render static site
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_RUNS_DIR = "runs"
os.makedirs(BASE_RUNS_DIR, exist_ok=True)


@app.post("/analyze")
async def analyze_architecture(file: UploadFile = File(...)):
  """
  Upload an architecture YAML file, run the full multi-agent pipeline,
  and return a JSON summary (report + remediation + run_id).
  """
  if not file.filename.endswith((".yaml", ".yml")):
    raise HTTPException(
      status_code=400,
      detail="Please upload a .yaml or .yml file.",
    )

  # 1) Create sequential run id & directory
  run_id = get_next_run_id()  # e.g. "001", "002", ...
  run_dir = os.path.join(BASE_RUNS_DIR, f"run_{run_id}")
  os.makedirs(run_dir, exist_ok=True)

  # 2) Save uploaded YAML into run_dir as architecture.yaml
  arch_path = os.path.join(run_dir, "architecture.yaml")
  contents = await file.read()
  with open(arch_path, "wb") as f:
    f.write(contents)

  # 3) Load architecture
  try:
    arch = load_architecture_from_yaml(arch_path)
  except Exception as e:
    raise HTTPException(
      status_code=400,
      detail=f"Failed to parse architecture YAML: {e}",
    )

  # 4) Create context for this run
  context = AgentContext(run_id=run_id)

  # 5) Run main multi-agent pipeline (failure + security + scoring)
  report = generate_system_report(arch, context=context)

  # 6) Save JSON report (per run)
  report_json_path = os.path.join(run_dir, "report.json")
  save_report(report, report_json_path)

  # 7) Text + PDF reports
  report_md_path = os.path.join(run_dir, "report.md")
  save_text_report(report, report_md_path)

  graph_basename = os.path.join(run_dir, "architecture_graph")

  # ✨ Safely try to generate the architecture graph image.
  # On platforms without the Graphviz system binary (`dot`),
  # this can fail — so we degrade gracefully instead of crashing.
  graph_image_path = None
  try:
    graph_image_path = generate_architecture_graph_image(arch, graph_basename)
  except Exception as e:
    print(f"[warn] Failed to generate architecture graph: {e}")
    graph_image_path = None

  report_pdf_path = os.path.join(run_dir, "report.pdf")
  generate_pdf_report(report, report_pdf_path, graph_image_path=graph_image_path)

  # 8) Remediation Agent (rule-based + optional Gemini augmentation)
  remediation_agent = RemediationAgent()
  suggestions = remediation_agent.run(arch, report, context=context)

  remediation_json_path = os.path.join(run_dir, "remediation.json")
  with open(remediation_json_path, "w", encoding="utf-8") as f:
    json.dump(suggestions_to_dict_list(suggestions), f, indent=2)

  # 9) AI summary (Gemini if available, else heuristic)
  ai_summary, ai_used_llm = generate_ai_summary(report)

  # 10) Agent context log
  context_path = os.path.join(run_dir, "agent_context.json")
  with open(context_path, "w", encoding="utf-8") as f:
    json.dump(context.to_dict(), f, indent=2)

  # 11) Prepare JSON-friendly response payload
  failure_scenarios = [
    {
      "scenario_name": s.scenario_name,
      "failed_component": s.failed_component,
      "severity": s.severity,
      "user_visible_impact": s.user_visible_impact,
      "impacted_components": list(s.impacted_components),
    }
    for s in report.scenarios
  ]

  security_risks = [
    {
      "component": r.component,
      "risk_type": r.risk_type,
      "severity": r.severity,
      "description": r.description,
      "suggestion": r.suggestion,
    }
    for r in report.security_risks
  ]

  remediation_suggestions = suggestions_to_dict_list(suggestions)

  # 12) Return plain dict – FastAPI will JSON-encode it
  return {
    "run_id": run_id,
    "system_name": report.system_name,
    "overall_resilience_score": report.overall_resilience_score,
    "worst_case_severity": report.worst_case_severity,
    "failure_scenarios": failure_scenarios,
    "security_risks": security_risks,
    "remediation_suggestions": remediation_suggestions,
    "ai_summary": ai_summary,
    "ai_summary_llm_used": ai_used_llm,
  }


@app.get("/runs/{run_id}/report.pdf")
async def get_report_pdf(run_id: str):
  """
  Download the PDF report for a given run_id.
  """
  run_dir = os.path.join(BASE_RUNS_DIR, f"run_{run_id}")
  pdf_path = os.path.join(run_dir, "report.pdf")

  if not os.path.exists(pdf_path):
    raise HTTPException(
      status_code=404,
      detail="PDF report not found for this run_id.",
    )

  return FileResponse(
    pdf_path,
    media_type="application/pdf",
    filename=f"report_{run_id}.pdf",
  )


@app.get("/runs/{run_id}/architecture_graph.png")
async def get_architecture_graph(run_id: str):
  """
  Download the architecture graph image for a given run_id.
  """
  run_dir = os.path.join(BASE_RUNS_DIR, f"run_{run_id}")
  png_path = os.path.join(run_dir, "architecture_graph.png")

  if not os.path.exists(png_path):
    raise HTTPException(
      status_code=404,
      detail="Graph image not found for this run_id.",
    )

  return FileResponse(
    png_path,
    media_type="image/png",
    filename=f"architecture_graph_{run_id}.png",
  )
