import React from "react";
import { useNavigate } from "react-router-dom";
import { cn } from "../lib/utils";
import { MetricCard } from "../components/dashboard/MetricCard";
import { StatusBadge } from "../components/ui/Badge";
import { ProgressBar } from "../components/ui/ProgressBar";
import { Button } from "../components/ui/Button";
import {
  Film, Clapperboard, ListChecks, HardDrive, Share2, History,
  Plus, Lightbulb, FolderClosed, ArrowRight, Clock,
  CheckCircle2, AlertTriangle, Loader, FileText, Zap,
} from "lucide-react";
import { mockEpisodes, mockReviewItems, mockActivity, mockDriveExports, mockHooks, mockManualLogs } from "../lib/mock-data";
import { useToast } from "../components/ui/Toast";

export function DashboardPage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const pipelineStages = [
    { label: "Ideas", count: 3, color: "bg-text-muted" },
    { label: "Script", count: 2, color: "bg-primary" },
    { label: "Assets", count: 1, color: "bg-amber" },
    { label: "Processing", count: 1, color: "bg-secondary" },
    { label: "Subtitles", count: 1, color: "bg-amber" },
    { label: "Review", count: 2, color: "bg-amber" },
    { label: "Approved", count: 1, color: "bg-success" },
    { label: "Exported", count: 1, color: "bg-success" },
  ];

  const continueEpisodes = mockEpisodes.filter((e) => e.progress > 0 && e.progress < 100).slice(0, 4);
  const pendingReviews = mockReviewItems.slice(0, 3);
  const recentExports = mockDriveExports.filter((e) => e.status === "Exported").concat(mockDriveExports.filter((e) => e.status === "Ready")).slice(0, 3);
  const recentActivity = mockActivity.slice(0, 6);
  const bestHook = mockHooks.find((h) => h.isRecommended) || mockHooks[0];

  const manualCount = mockManualLogs.length;
  const avgManualTime = "4h 17m";
  const avgProcessTime = "18m 42s";
  const timeSaved = "3h 58m";

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-text-main">Studio Overview</h1>
          <p className="text-sm text-text-muted mt-0.5">Create, review, and export your next Burmese story.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => navigate("/activity")}>
            <Clock size={14} /> View Activity
          </Button>
          <Button variant="secondary" size="sm" onClick={() => navigate("/ideas")}>
            <Lightbulb size={14} /> New Idea
          </Button>
          <Button variant="primary" size="sm" onClick={() => navigate("/episodes")}>
            <Plus size={14} /> New Episode
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard label="Active Series" value={5} icon={<Film size={18} />} change={{ value: "+1", positive: true }} color="primary" onClick={() => navigate("/series")} />
        <MetricCard label="In Production" value={8} icon={<Clapperboard size={18} />} change={{ value: "+2", positive: true }} color="secondary" onClick={() => navigate("/episodes")} />
        <MetricCard label="Needs Review" value={4} icon={<ListChecks size={18} />} change={{ value: "-1", positive: true }} color="amber" onClick={() => navigate("/review")} />
        <MetricCard label="Ready to Export" value={3} icon={<HardDrive size={18} />} change={{ value: "+2", positive: true }} color="success" onClick={() => navigate("/drive-exports")} />
        <MetricCard label="Published Records" value={12} icon={<Share2 size={18} />} change={{ value: "+3", positive: true }} color="primary" onClick={() => navigate("/publishing")} />
        <MetricCard label="Manual Videos Logged" value={manualCount} icon={<History size={18} />} change={{ value: "+1", positive: true }} color="amber" onClick={() => navigate("/manual-logs")} />
      </div>

      <div className="surface-card p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-text-main">Production Pipeline</h2>
          <button onClick={() => navigate("/episodes")} className="text-xs text-text-muted hover:text-text-main transition-colors flex items-center gap-1">
            View all <ArrowRight size={12} />
          </button>
        </div>
        <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
          {pipelineStages.map((stage) => (
            <button
              key={stage.label}
              onClick={() => navigate("/episodes")}
              className="bg-elevated border border-border rounded-lg p-3 text-center hover:border-primary/30 transition-colors"
            >
              <div className={cn("w-2 h-2 rounded-full mx-auto mb-2", stage.color)} />
              <div className="text-lg font-bold text-text-main">{stage.count}</div>
              <div className="text-[10px] text-text-muted mt-0.5">{stage.label}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="surface-card p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-text-main">Continue Creating</h2>
            <button onClick={() => navigate("/episodes")} className="text-xs text-text-muted hover:text-text-main flex items-center gap-1">
              All episodes <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {continueEpisodes.map((ep) => (
              <div
                key={ep.id}
                onClick={() => navigate(`/episodes/${ep.id}`)}
                className="flex items-center gap-3 p-3 bg-elevated border border-border rounded-lg cursor-pointer hover:border-primary/30 transition-colors"
              >
                <div className={cn("w-12 h-12 rounded-md bg-gradient-to-br flex-shrink-0", ep.thumbnailGradient)} />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-text-muted">{ep.seriesTitle} · Ep {ep.number}</div>
                  <div className="text-sm font-medium text-text-main truncate">{ep.title}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <StatusBadge status={ep.status} />
                    <span className="text-[10px] text-text-muted">{ep.updatedAt}</span>
                  </div>
                </div>
                <div className="flex-shrink-0 w-16">
                  <ProgressBar value={ep.progress} color={ep.progress > 80 ? "success" : "primary"} />
                  <div className="text-[10px] text-text-muted text-center mt-1">{ep.progress}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-text-main">Review Queue</h2>
            <button onClick={() => navigate("/review")} className="text-xs text-text-muted hover:text-text-main flex items-center gap-1">
              Open center <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {pendingReviews.map((rev) => (
              <div
                key={rev.id}
                onClick={() => navigate(`/review/${rev.id}`)}
                className="flex items-center gap-3 p-3 bg-elevated border border-border rounded-lg cursor-pointer hover:border-primary/30 transition-colors"
              >
                <div className={cn("w-10 h-10 rounded-md bg-gradient-to-br flex-shrink-0", rev.thumbnailGradient)} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-text-main truncate">{rev.episodeTitle}</div>
                  <div className="text-[11px] text-text-muted">{rev.reviewType}</div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {rev.criticalIssues > 0 && (
                    <span className="text-[10px] text-error flex items-center gap-1">
                      <AlertTriangle size={10} /> {rev.criticalIssues}
                    </span>
                  )}
                  <StatusBadge status={rev.priority === "Urgent" ? "Failed" : rev.priority === "High" ? "Needs Approval" : "Draft"} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="surface-card p-4">
          <h2 className="text-sm font-semibold text-text-main mb-4">Recent Exports</h2>
          <div className="space-y-2">
            {recentExports.map((exp) => (
              <div
                key={exp.id}
                onClick={() => navigate(`/drive-export/${exp.id}`)}
                className="flex items-center gap-3 p-2.5 bg-elevated border border-border rounded-lg cursor-pointer hover:border-primary/30 transition-colors"
              >
                <HardDrive size={16} className="text-text-muted flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium text-text-main truncate">{exp.episodeTitle}</div>
                  <div className="text-[10px] text-text-muted mono">{exp.publicId}</div>
                </div>
                <StatusBadge status={exp.status} />
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card p-4">
          <h2 className="text-sm font-semibold text-text-main mb-4">Manual vs Auto Snapshot</h2>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-elevated rounded-lg p-3 border border-border">
                <div className="text-lg font-bold text-text-main">{manualCount}</div>
                <div className="text-[10px] text-text-muted">Manual videos</div>
              </div>
              <div className="bg-elevated rounded-lg p-3 border border-border">
                <div className="text-lg font-bold text-text-main">3</div>
                <div className="text-[10px] text-text-muted">Auto-assisted</div>
              </div>
            </div>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-[11px] text-text-muted mb-1">
                  <span>Manual avg time</span>
                  <span className="text-text-sec">{avgManualTime}</span>
                </div>
                <ProgressBar value={100} color="amber" />
              </div>
              <div>
                <div className="flex justify-between text-[11px] text-text-muted mb-1">
                  <span>Processing avg time</span>
                  <span className="text-text-sec">{avgProcessTime}</span>
                </div>
                <ProgressBar value={28} color="secondary" />
              </div>
              <div>
                <div className="flex justify-between text-[11px] text-text-muted mb-1">
                  <span>Time saved</span>
                  <span className="text-success">{timeSaved}</span>
                </div>
                <ProgressBar value={72} color="success" />
              </div>
            </div>
          </div>
        </div>

        <div className="surface-card p-4">
          <h2 className="text-sm font-semibold text-text-main mb-4">Hook Performance</h2>
          <div className="space-y-3">
            <div className="bg-elevated rounded-lg p-3 border border-border">
              <div className="flex items-center gap-2 mb-2">
                <Zap size={14} className="text-amber" />
                <span className="text-[11px] text-text-muted">Best hook type</span>
              </div>
              <div className="text-sm font-medium text-text-main">{bestHook.type}</div>
              <div className="text-[11px] text-text-muted mt-1">Avg completion: {bestHook.completionRate}%</div>
            </div>
            <div className="bg-elevated rounded-lg p-3 border border-border">
              <div className="text-[11px] text-text-muted mb-1">Best-performing sample</div>
              <div className="text-xs text-text-main italic">"{bestHook.text}"</div>
            </div>
            <Button variant="secondary" size="sm" className="w-full" onClick={() => navigate("/hooks")}>
              Open Hook Library
            </Button>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="surface-card p-4">
          <h2 className="text-sm font-semibold text-text-main mb-4">Recent Activity</h2>
          <div className="space-y-1">
            {recentActivity.map((act) => (
              <div key={act.id} className="flex items-center gap-3 py-2 border-b border-border-soft last:border-0">
                <div className={cn(
                  "w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0",
                  act.action.includes("approved") ? "bg-success/15 text-success" :
                  act.action.includes("failed") ? "bg-error/15 text-error" :
                  act.action.includes("export") ? "bg-secondary/15 text-secondary" :
                  act.action.includes("uploaded") ? "bg-amber/15 text-amber" :
                  "bg-primary/15 text-primary"
                )}>
                  {act.action.includes("approved") ? <CheckCircle2 size={14} /> :
                   act.action.includes("failed") ? <AlertTriangle size={14} /> :
                   act.action.includes("export") ? <HardDrive size={14} /> :
                   act.action.includes("uploaded") ? <FolderClosed size={14} /> :
                   act.action.includes("processing") ? <Loader size={14} /> :
                   <FileText size={14} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-text-main truncate">{act.action}</div>
                  <div className="text-[10px] text-text-muted truncate">{act.target}</div>
                </div>
                <div className="text-[10px] text-text-muted flex-shrink-0">{act.timestamp.split(" ")[1]}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card p-4">
          <h2 className="text-sm font-semibold text-text-main mb-4">System Snapshot</h2>
          <div className="space-y-2">
            {[
              { label: "Narrativ Forge UI", status: "Operational", color: "success" as const },
              { label: "Local Processing Worker", status: "Simulated", color: "secondary" as const },
              { label: "Mock Drive Adapter", status: "Not Connected", color: "amber" as const },
              { label: "Database Mock", status: "Local Mode", color: "secondary" as const },
              { label: "AI Draft Mode", status: "Local Mock", color: "secondary" as const },
              { label: "Storage", status: "42% Used (Mock)", color: "success" as const },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-border-soft last:border-0">
                <span className="text-xs text-text-sec">{item.label}</span>
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "w-1.5 h-1.5 rounded-full",
                    item.color === "success" ? "bg-success" :
                    item.color === "amber" ? "bg-amber" : "bg-secondary"
                  )} />
                  <span className={cn(
                    "text-[11px]",
                    item.color === "success" ? "text-success" :
                    item.color === "amber" ? "text-amber" : "text-secondary"
                  )}>{item.status}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 p-2.5 bg-elevated rounded-md border border-border">
            <p className="text-[10px] text-text-muted text-center">
              UI Prototype — No external connections active. All data is simulated.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
