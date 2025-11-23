# FortifyAI – Multi-Agent Resilience & Security Advisor

FortifyAI is a **multi-agent AI system** that analyzes a system architecture (described in YAML), simulates **failure scenarios**, evaluates **security risks**, and generates **actionable remediation plans** along with an **AI executive summary**.

It comes with:

- 🧠 **Multi-agent backend** (Python + FastAPI)
- 🤖 **Hybrid intelligence**: deterministic simulation + Gemini (LLM) for summarization and extra suggestions
- 📊 **Futuristic React dashboard** (Vite) with light/dark mode
- 📂 **Per-run artefacts**: JSON, Markdown, PDF report, architecture graph, agent context, remediation plan

---

## 1. High-Level Architecture

**Input:**  
A YAML file describing the system architecture (components, types, dependencies, criticality, public exposure).

**Core pipeline (multi-agent):**

1. **Orchestrator Agent**
   - Coordinates the entire analysis run
   - Creates a `run_id` + `runs/run_XXX` folder
   - Calls the other agents and aggregates their outputs
   - Logs events into `agent_context.json`

2. **Failure Simulation Agent**
   - For each component, simulates a **single-component failure**
   - Propagates impact through the dependency graph
   - Computes:
     - Severity score (0–10)
     - Whether the impact is user-visible
     - List of impacted components

3. **Security Analysis Agent**
   - Inspects component metadata (e.g. `type`, `public`, `external_api`)
   - Flags risks like:
     - Denial-of-Service on public-facing components
     - External dependency risk on 3rd-party APIs
   - Produces structured `security_risks` entries

4. **Reporting Agent**
   - Consolidates:
     - Overall resilience score
     - Worst-case severity
     - Failure scenarios
     - Security risks
   - Generates:
     - `report.json`
     - `report.md`
     - `report.pdf` (with page numbers)
     - Architecture graph PNG (via Graphviz)

5. **Remediation Agent**
   - Reads the report + architecture
   - Proposes structured remediation suggestions:
     - `category` (resilience / security / architecture)
     - `target` (component or system)
     - `priority` (high / medium / low)
     - `title` + `details`
   - **Optionally enhanced with Gemini** (adds more suggestions when API key is set)

6. **AI Summary Agent**
   - Converts the raw JSON report into a **clean executive summary**
   - Uses **Gemini 2.5 Flash Lite** when `GEMINI_API_KEY` is available
   - Falls back to a heuristic summary when no key is set
   - The frontend clearly shows whether Gemini was used

**Output (per run):**

Each analysis run creates a folder like `runs/run_003/` containing:

- `architecture.yaml` – the uploaded architecture
- `report.json` – machine-readable system report
- `report.md` – Markdown report
- `report.pdf` – formatted PDF with ToC
- `architecture_graph.png` – dependency graph
- `remediation.json` / `remediation.txt` – suggested fixes
- `ai_summary.txt` – AI/LLM executive summary
- `agent_context.json` – timeline of agent calls and shared state

---

## 2. Tech Stack

**Backend**

- Python 3.12+
- FastAPI
- Uvicorn
- Graphviz (Python package + system binary)
- ReportLab (PDF generation)
- `python-dotenv`
- `google-generativeai` (Gemini 2.5 Flash Lite integration)

**Frontend**

- React (Vite)
- Pure CSS (custom, no UI framework)
- Light/Dark theme toggle
- Responsive layout

---

## 3. Project Structure (simplified)

```txt
agentic_capstone_project/
├─ api.py                  # FastAPI app (HTTP API)
├─ main.py                 # CLI entrypoint (local runs, optional)
├─ architecture_model.py   # Data model for components & system
├─ orchestrator.py         # Orchestrator + SystemReport definition
├─ failure_simulation.py   # Failure Simulation Agent
├─ security_analysis.py    # Security Analysis Agent
├─ remediation_agent.py    # Remediation Agent
├─ ai_summary_agent.py     # AI Summary Agent
├─ llm_client.py           # Gemini client wrapper
├─ agent_context.py        # AgentContext (events + shared state)
├─ report_storage.py       # JSON serialisation helpers
├─ report_generator.py     # Markdown + PDF report generator
├─ graph_utils.py          # Graphviz-based architecture graph generator
├─ run_utils.py            # Sequential run IDs (001, 002, 003, ...)
├─ example_architecture.yaml
├─ runs/
│   └─ run_001/ ...        # Per-run artefacts (auto-generated)
└─ frontend/
    ├─ index.html
    ├─ vite.config.js
    └─ src/
        ├─ App.jsx         # Main React dashboard
        ├─ App.css         # Theming + layout + table styling
        └─ main.jsx
