import { AppShell } from "../../components/app-shell";

const foundationAreas = [
  ["Frontend", "Next.js app shell + protected workspace routes"],
  ["Backend", "FastAPI API + CORS + session authentication"],
  ["Database", "SQLAlchemy foundation with SQLite development default"],
  ["Workflow", "Core content model boundary reserved for Phase 2"],
];

export default function DashboardPage() {
  return <AppShell title="Dashboard">
    <section className="card">
      <div className="eyebrow">PHASE 1 · FOUNDATION</div>
      <h2>Core workspace foundation</h2>
      <p className="muted">This screen intentionally avoids fake production metrics. Real Ideas → Series → Season → Episode data will arrive in Phase 2.</p>
    </section>
    <div className="grid foundation-grid">
      {foundationAreas.map(([label, note]) => (
        <section className="card" key={label}>
          <div className="muted">{label}</div>
          <div className="status">Ready</div>
          <div className="muted">{note}</div>
        </section>
      ))}
    </div>
    <section className="card workflow">
      <div>
        <div className="eyebrow">PRODUCTION WORKFLOW</div>
        <h2>Idea → Structure → Script → Assets → Processing → Subtitle → Review → Output</h2>
        <p className="muted">The architecture keeps heavy integrations behind adapters so the workflow can be verified before real media, AI, storage, and Drive services are connected.</p>
      </div>
    </section>
  </AppShell>;
}
