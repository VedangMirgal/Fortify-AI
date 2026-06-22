# FortifyAI – Architecture Resilience & Security Analysis Platform

FortifyAI is an AI-assisted architecture analysis platform that evaluates software systems defined in YAML, simulates failure scenarios, identifies security risks, generates remediation recommendations, and produces executive-level summaries.

The platform combines graph-based failure propagation analysis, rule-driven security assessment, and Gemini-powered reporting to help architects, DevOps engineers, and platform teams understand the resilience and security posture of their systems.

---

## 🌐 Live Deployment

**Frontend (UI):** https://fortify-ai-1.onrender.com

**Backend API:** https://fortify-ai.onrender.com/docs

🎥 **Project Demo:** https://youtu.be/bVp6LbKr4p4

> Note: Architecture graph generation is fully supported locally. On free hosting platforms, file persistence limitations may affect long-term access to generated artifacts.

---

## 🚀 Key Capabilities

FortifyAI provides:

* Dependency graph construction from architecture specifications
* Failure impact simulation and propagation analysis
* Automated security risk assessment
* Resilience scoring and severity analysis
* AI-powered executive summaries
* Architecture visualization
* PDF and Markdown report generation
* Per-run artifact storage and traceability
* Hybrid deterministic + LLM-assisted reasoning

---

## 🔍 What FortifyAI Does

Given a system architecture YAML file, FortifyAI:

1. Parses architecture components and dependencies.
2. Builds forward and reverse dependency graphs.
3. Simulates component failures and propagates impact.
4. Computes:

   * Impacted components
   * User visibility
   * Failure severity
5. Performs rule-based security analysis.
6. Generates:

   * Structured reports
   * Remediation recommendations
   * Architecture visualizations
   * Executive summaries

---

## 🏗 System Architecture

### Input

FortifyAI accepts architecture definitions in YAML format.

Example information includes:

* Components
* Component types
* Dependencies
* Criticality
* Public exposure
* External integrations

---

## ⚙ Core Analysis Pipeline

### 1. Architecture Parsing

The uploaded YAML is converted into an internal architecture model containing:

* Components
* Metadata
* Dependency relationships

From this representation, FortifyAI constructs:

* Forward dependency graphs
* Reverse dependency graphs

These graphs serve as the foundation for resilience analysis.

---

### 2. Failure Simulation Engine

The failure simulation engine evaluates:

> What happens if a given component becomes unavailable?

For every component:

* Failure is simulated
* Impact propagates through the reverse dependency graph
* Impacted services are identified

The system uses graph traversal techniques to determine:

* Direct failures
* Cascading failures
* User-visible failures

Metrics generated include:

* Severity score
* Impacted components
* Visibility assessment

---

### 3. Security Analysis Engine

The security analysis engine performs rule-based assessments using architecture metadata.

Current checks include:

* Public-facing service exposure
* Potential Denial-of-Service risk
* External dependency risk
* Integration exposure concerns

Security findings are incorporated into the final report.

---

### 4. Reporting Engine

The reporting engine aggregates outputs from all analysis stages and produces:

* Resilience score
* Worst-case failure scenario
* Failure analysis results
* Security findings

Generated artifacts include:

* report.json
* report.md
* report.pdf
* architecture_graph.png

---

### 5. Remediation Engine

The remediation engine generates prioritized recommendations based on:

* Failure scenarios
* Security findings
* Architecture weaknesses

Recommendations include:

* Resilience improvements
* Security enhancements
* Architectural best practices

---

### 6. AI Summary Engine

The AI Summary Engine transforms technical analysis into executive-level insights.

When configured, FortifyAI uses:

**Gemini 2.5 Flash Lite**

to generate:

* Executive summaries
* Architecture observations
* Additional remediation suggestions

If no API key is available, the platform falls back to heuristic summaries.

---

## 🧠 Hybrid Reasoning Approach

A core design principle of FortifyAI is the separation of deterministic analysis from LLM-powered assistance.

### Deterministic Components

* Graph construction
* Failure propagation
* Severity scoring
* Security rule evaluation
* Resilience calculations

### LLM-Assisted Components

* Executive summaries
* Additional remediation insights
* Human-readable reporting

This design improves:

* Explainability
* Reliability
* Reproducibility

while still leveraging modern AI capabilities where they provide the most value.

---

## 📁 Generated Artifacts

Each analysis run produces:

```text
runs/run_003/
├─ architecture.yaml
├─ report.json
├─ report.md
├─ report.pdf
├─ architecture_graph.png
├─ remediation.json
├─ remediation.txt
├─ ai_summary.txt
└─ agent_context.json
```

All generated run folders are excluded from version control.

---

## 🖼 UI Screenshots

Screenshots are available in:

```text
docs/screenshots/
```

### Dark Mode

* Dashboard
* Failure Scenarios
* Recommendations
* AI Summary

### Light Mode

* Dashboard
* Failure Scenarios
* Recommendations
* AI Summary

---

## 🧰 Technology Stack

### Backend

* Python 3.12+
* FastAPI
* Graphviz
* ReportLab
* Uvicorn
* python-dotenv
* Google Generative AI SDK

### Frontend

* React
* Vite
* Custom CSS
* Light/Dark Theme Support

### Deployment

* Render

---

## 📂 Project Structure

```text
Fortify-AI/
├── api.py
├── main.py
├── architecture_model.py
├── orchestrator.py
├── failure_simulation.py
├── security_analysis.py
├── remediation_agent.py
├── ai_summary_agent.py
├── llm_client.py
├── agent_context.py
├── report_storage.py
├── report_generator.py
├── graph_utils.py
├── run_utils.py
├── requirements.txt
├── frontend/
└── runs/
```

---

## ⚙ Setup

### Backend

```bash
pip install -r requirements.txt
uvicorn api:app --reload
```

Optional Gemini configuration:

```bash
GEMINI_API_KEY=your_api_key_here
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Security Notes

* No API keys are stored in the repository.
* Environment variables are used for secrets.
* Analysis is stateless and file-driven.
* Generated reports are isolated per run.

---

## 🎓 Academic Context

FortifyAI was developed as an exploration of:

* Architecture resilience analysis
* Failure propagation modeling
* Graph-based system analysis
* AI-assisted decision support
* Hybrid deterministic and LLM-powered reasoning

The project demonstrates how traditional software engineering techniques and modern AI systems can be combined to build explainable architecture analysis tools.

---

## 📜 License

MIT License

See LICENSE for details.

---

## Project Status

✅ Live Frontend & Backend

✅ Architecture Analysis Pipeline

✅ Failure Simulation Engine

✅ Security Assessment Engine

✅ PDF & Markdown Reporting

✅ Gemini Integration

✅ Graph Visualization

✅ Hybrid Deterministic + AI Reasoning

FortifyAI is actively maintained and serves as a foundation for future work in architecture resilience analysis, AI-assisted operations tooling, and intelligent system design.
