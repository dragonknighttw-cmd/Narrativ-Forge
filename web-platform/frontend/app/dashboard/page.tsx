import { AppShell } from "../../components/app-shell";

const metrics = [
  ["Ideas", "12", "Ready for planning"],
  ["In production", "4", "Across active episodes"],
  ["Needs review", "2", "Human approval required"],
  ["Exported", "18", "Approved packages"],
];

export default function DashboardPage() {
  return <AppShell title="Dashboard">
    <div className="grid">
      {metrics.map(([label, value, note]) => (
        <section className="card" key={label}>
          <div className="muted">{label}</div>
          <div className="metric">{value}</div>
          <div className="muted">{note}</div>
        </section>
      ))}
    </div>
    <section className="card workflow">
      <div>
        <div className="eyebrow">PRODUCTION WORKFLOW</div>
        <h2>Idea → Structure → Script → Assets → Processing → Subtitle → Review → Output</h2>
        <p className="muted">Foundation is ready for mock-first workflow integration. Real processing adapters come after the core flow is verified.</p>
      </div>
    </section>
  </AppShell>;
}