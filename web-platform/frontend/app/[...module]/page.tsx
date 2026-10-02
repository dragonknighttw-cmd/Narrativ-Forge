import { AppShell } from "../../components/app-shell";

export default async function ModulePage({ params }: { params: Promise<{ module: string[] }> }) {
  const { module } = await params;
  const title = module.map(x => x.replace(/-/g, " ")).join(" / ");
  return <AppShell title={title.replace(/\b\w/g, c => c.toUpperCase())}>
    <section className="card">
      <div className="eyebrow">FOUNDATION MODULE</div>
      <h2>{title}</h2>
      <p className="muted">UI route is established. Domain implementation will follow the source-of-truth phase order and quality gates.</p>
    </section>
  </AppShell>;
}