import { useState } from "react";
import "./App.css";

// frontend/src/App.jsx
const API_BASE =import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const IS_LOCAL =API_BASE.includes("localhost") || API_BASE.includes("127.0.0.1");


function App() {
  const [theme, setTheme] = useState("dark");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selected = e.target.files[0] || null;
    setFile(selected);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a YAML file.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let detail = "Request failed";
        try {
          const errJson = await res.json();
          if (errJson.detail) detail = errJson.detail;
        } catch (_) {}
        throw new Error(detail);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const getPriorityClass = (priority) => {
    if (priority === "high") return "badge badge-high";
    if (priority === "medium") return "badge badge-medium";
    return "badge badge-low";
  };

  const getSeverityChipClass = (severity) => {
    if (severity >= 9) return "chip chip-critical";
    if (severity >= 7) return "chip chip-high";
    if (severity >= 4) return "chip chip-medium";
    return "chip chip-low";
  };

  const renderOverview = () => {
    if (!result) return null;

    const pdfUrl = `${API_BASE}/runs/${result.run_id}/report.pdf`;
    const graphUrl = `${API_BASE}/runs/${result.run_id}/architecture_graph.png`;

    let healthLabel = "Unknown";
    let healthClass = "health health-low";
    if (result.overall_resilience_score >= 8) {
      healthLabel = "Strong";
      healthClass = "health health-strong";
    } else if (result.overall_resilience_score >= 4) {
      healthLabel = "Moderate";
      healthClass = "health health-medium";
    } else {
      healthLabel = "Fragile";
      healthClass = "health health-low";
    }

    return (
      <section className="grid-two-columns section-spaced">
        <div className="card surface">
          <div className="section-header">
            <h2>System Overview</h2>
            <p className="section-subtitle">
              Snapshot of the current architecture’s resilience and impact
              profile.
            </p>
          </div>

          <p className="system-name">{result.system_name}</p>

          <div className="overview-metrics">
            <div className="metric-card">
              <span className="metric-label">Resilience Score</span>
              <span className="metric-value">
                {result.overall_resilience_score} / 10
              </span>
              <div className="metric-bar">
                <div
                  className="metric-bar-fill"
                  style={{
                    width: `${
                      (result.overall_resilience_score / 10) * 100
                    }%`,
                  }}
                />
              </div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Worst-case Severity</span>
              <span className="metric-value">
                {result.worst_case_severity} / 10
              </span>
              <div className="metric-bar metric-bar-danger">
                <div
                  className="metric-bar-fill"
                  style={{
                    width: `${(result.worst_case_severity / 10) * 100}%`,
                  }}
                />
              </div>
            </div>
            <div className="metric-card">
              <span className="metric-label">System Health</span>
              <span className={healthClass}>{healthLabel}</span>
              <p className="metric-hint">
                Computed from simulated impact and number of critical weak
                points.
              </p>
            </div>
          </div>

          <p className="run-id">
            <span>Run ID:</span> <code>{result.run_id}</code>
          </p>

          <div className="actions-row">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="btn-primary-outline"
            >
              Download PDF Report
            </a>

            {IS_LOCAL ? (
              <a
                href={graphUrl}
                target="_blank"
                rel="noreferrer"
                className="btn-ghost"
              >
                View Architecture Graph
              </a>
            ) : (
              <span className="btn-ghost disabled-hint">
                Architecture graph available in local setup
              </span>
            )}
          </div>

        </div>

        <div className="card surface">
          <div className="section-header">
            <h2>At a Glance</h2>
            <p className="section-subtitle">
              Key metrics for this analysis run.
            </p>
          </div>

          <ul className="glance-list">
            <li>
              <span className="glance-label">Failure Scenarios</span>
              <span className="glance-value">
                {result.failure_scenarios.length}
              </span>
            </li>
            <li>
              <span className="glance-label">Security Risks</span>
              <span className="glance-value">
                {result.security_risks.length}
              </span>
            </li>
            <li>
              <span className="glance-label">Remediation Suggestions</span>
              <span className="glance-value">
                {result.remediation_suggestions.length}
              </span>
            </li>
          </ul>

          <div className="glance-note">
            Values are derived from independent agents for failure simulation,
            security analysis, and remediation planning.
          </div>
        </div>
      </section>
    );
  };

  const renderScenarios = () => {
    if (!result) return null;

    return (
      <section className="card surface section-spaced">
        <div className="section-header">
          <h2>Failure Scenarios</h2>
          <p className="section-subtitle">
            Simulated single-component failures and their downstream business
            impact.
          </p>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Failed Component</th>
                <th>Severity</th>
                <th>User-visible</th>
                <th>Impacted Components</th>
              </tr>
            </thead>
            <tbody>
              {result.failure_scenarios.map((s, idx) => (
                <tr key={idx}>
                  <td>{s.scenario_name}</td>
                  <td>{s.failed_component}</td>
                  <td>
                    <span className={getSeverityChipClass(s.severity)}>
                      {s.severity.toFixed ? s.severity.toFixed(1) : s.severity}
                    </span>
                  </td>
                  <td>{s.user_visible_impact ? "Yes" : "No"}</td>
                  <td>{s.impacted_components.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    );
  };

  const renderRisks = () => {
    if (!result) return null;

    return (
      <section className="card surface section-spaced">
        <div className="section-header">
          <h2>Security Risks</h2>
          <p className="section-subtitle">
            Heuristic checks based on public exposure and external
            dependencies.
          </p>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Component</th>
                <th>Risk Type</th>
                <th>Severity</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {result.security_risks.map((r, idx) => {
                const key =
                  typeof r.severity === "string"
                    ? r.severity.toLowerCase()
                    : "medium";
                return (
                  <tr key={idx}>
                    <td>{r.component}</td>
                    <td>{r.risk_type}</td>
                    <td>
                      <span className={getPriorityClass(key)}>
                        {r.severity}
                      </span>
                    </td>
                    <td>{r.description}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    );
  };

  const renderRemediation = () => {
    if (!result) return null;

    return (
      <section className="card surface section-spaced">
        <div className="section-header">
          <h2>Remediation Suggestions</h2>
          <p className="section-subtitle">
            Prioritized actions generated from failure simulations and security
            findings.
          </p>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Target</th>
                <th>Priority</th>
                <th>Title</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {result.remediation_suggestions.map((s, idx) => (
                <tr key={idx}>
                  <td>{s.category}</td>
                  <td>{s.target}</td>
                  <td>
                    <span className={getPriorityClass(s.priority)}>
                      {s.priority}
                    </span>
                  </td>
                  <td>{s.title}</td>
                  <td>{s.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    );
  };

  const renderAiSummary = () => {
    if (!result) return null;

    const usedLLM = result.ai_summary_llm_used;

    let summaryText = result.ai_summary || "";
    summaryText = summaryText
      .split("\n")
      .filter(
        (line) =>
          !line.trim().startsWith("AI Insight Summary") &&
          !line.trim().startsWith("Powered by Gemini")
      )
      .join("\n")
      .trim();

    const lines = summaryText
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    const blocks = [];
    let currentList = [];

    const flushList = () => {
      if (currentList.length > 0) {
        blocks.push({ type: "list", items: [...currentList] });
        currentList = [];
      }
    };

    lines.forEach((line) => {
      const isNumbered = /^\d+\./.test(line);
      const isShortHeading = /:$/.test(line) && line.split(" ").length <= 8;

      if (isNumbered) {
        const cleaned = line.replace(/^\d+\.\s*/, "");
        currentList.push(cleaned);
        return;
      }

      flushList();

      if (isShortHeading) {
        blocks.push({
          type: "subheading",
          text: line.replace(/:$/, ""),
        });
      } else {
        blocks.push({
          type: "paragraph",
          text: line,
        });
      }
    });

    flushList();

    return (
      <section className="ai-summary-card section-spaced">
        <div className="ai-summary-header">
          <div>
            <h2>AI Insight Summary</h2>
            <p className="ai-summary-subtitle">
              Natural language view of your architecture’s resilience and
              security posture.
            </p>
          </div>

          <div
            className={
              usedLLM ? "llm-badge llm-badge-on" : "llm-badge llm-badge-off"
            }
          >
            {usedLLM ? "Powered by Gemini" : "Heuristic Engine"}
          </div>
        </div>

        <div className="ai-summary-body">
          {blocks.map((block, idx) => {
            if (block.type === "subheading") {
              return (
                <h4 key={idx} className="ai-summary-subheading">
                  {block.text}
                </h4>
              );
            }
            if (block.type === "list") {
              return (
                <ul key={idx} className="ai-summary-list">
                  {block.items.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              );
            }
            return (
              <p key={idx} className="ai-summary-paragraph">
                {block.text}
              </p>
            );
          })}
        </div>
      </section>
    );
  };

  return (
    <div className={`app-shell ${theme}`}>
      <div className="app-root">
        {/* NEW shared width wrapper so header + main align perfectly */}
        <div className="page-inner">
          <header className="app-header">
            <div className="header-inner">
              <div className="brand-block">
                <div className="logo-circle">A</div>
                <div>
                  <h1 className="app-title">
                    Resilience &amp; Security Agent
                  </h1>
                  <p className="app-subtitle">
                    Multi-agent console for architecture failure simulation
                    &amp; risk analysis.
                  </p>
                </div>
              </div>

              <div className="header-right">
                <div className="stack-tag">
                  Backend: FastAPI · Frontend: React · Agents: Python
                </div>
                <button
                  type="button"
                  className="theme-toggle"
                  onClick={toggleTheme}
                >
                  <span className="theme-toggle-icon">
                    {theme === "dark" ? "🌞" : "🌙"}
                  </span>
                  {theme === "dark" ? "Light mode" : "Dark mode"}
                </button>
              </div>
            </div>
          </header>

          <main className="app-main">
            <section className="card surface upload-card">
              <div className="section-header">
                <h2>Analyze a System Architecture</h2>
                <p className="section-subtitle">
                  Upload an <code>.yaml</code> architecture file. The agent
                  pipeline will simulate failures, evaluate security risks, and
                  propose remediation steps.
                </p>
              </div>
              <form onSubmit={handleSubmit} className="upload-form">
                <div className="file-row">
                  <label className="file-input-wrapper">
                    <span className="file-input-label">
                      {file ? "Change file" : "Choose file"}
                    </span>
                    <input
                      type="file"
                      accept=".yaml,.yml"
                      onChange={handleFileChange}
                      className="file-input"
                    />
                  </label>
                  <span className="file-chosen">
                    {file ? file.name : "No file selected"}
                  </span>
                </div>
                <div className="button-row">
                  <button type="submit" disabled={loading}>
                    {loading ? "Analyzing..." : "Run Analysis"}
                  </button>
                  {loading && (
                    <span className="loading-text">
                      Running multi-agent analysis workflow...
                    </span>
                  )}
                </div>
                {error && <div className="error-text">Error: {error}</div>}
              </form>
            </section>

            {result && (
              <>
                {renderOverview()}
                {renderScenarios()}
                {renderRisks()}
                {renderRemediation()}
                {renderAiSummary()}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
