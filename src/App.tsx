import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { ToastProvider } from "./components/ui/Toast";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { IdeasPage } from "./pages/IdeasPage";
import { SeriesPage } from "./pages/SeriesPage";
import { SeriesDetailPage } from "./pages/SeriesDetailPage";
import { EpisodesPage } from "./pages/EpisodesPage";
import { EpisodeDetailPage } from "./pages/EpisodeDetailPage";
import { ScriptsPage } from "./pages/ScriptsPage";
import { ScriptEditorPage } from "./pages/ScriptEditorPage";
import { ScenesPage } from "./pages/ScenesPage";
import { EpisodeScenesPage } from "./pages/EpisodeScenesPage";
import { AssetsPage } from "./pages/AssetsPage";
import { VideoProjectsPage } from "./pages/VideoProjectsPage";
import { VideoProjectDetailPage } from "./pages/VideoProjectDetailPage";
import { SubtitleStudioListPage } from "./pages/SubtitleStudioListPage";
import { SubtitleStudioEditorPage } from "./pages/SubtitleStudioEditorPage";
import { PresetsPage } from "./pages/PresetsPage";
import { ProcessingPage } from "./pages/ProcessingPage";
import { ReviewPage } from "./pages/ReviewPage";
import { ReviewDetailPage } from "./pages/ReviewDetailPage";
import { ApprovalsPage } from "./pages/ApprovalsPage";
import { DriveExportsPage } from "./pages/DriveExportsPage";
import { DriveExportDetailPage } from "./pages/DriveExportDetailPage";
import { PublishingPage } from "./pages/PublishingPage";
import { ManualLogsPage } from "./pages/ManualLogsPage";
import { HooksPage } from "./pages/HooksPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { ActivityPage } from "./pages/ActivityPage";
import { SettingsPage } from "./pages/SettingsPage";

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/ideas" element={<IdeasPage />} />
          <Route path="/series" element={<SeriesPage />} />
          <Route path="/series/:id" element={<SeriesDetailPage />} />
          <Route path="/episodes" element={<EpisodesPage />} />
          <Route path="/episodes/:id" element={<EpisodeDetailPage />} />
          <Route path="/episodes/:id/scenes" element={<EpisodeScenesPage />} />
          <Route path="/scripts" element={<ScriptsPage />} />
          <Route path="/scripts/:id" element={<ScriptEditorPage />} />
          <Route path="/scenes" element={<ScenesPage />} />
          <Route path="/assets" element={<AssetsPage />} />
          <Route path="/video" element={<VideoProjectsPage />} />
          <Route path="/video-projects/:id" element={<VideoProjectDetailPage />} />
          <Route path="/subtitles" element={<SubtitleStudioListPage />} />
          <Route path="/subtitle-studio/:id" element={<SubtitleStudioEditorPage />} />
          <Route path="/presets" element={<PresetsPage />} />
          <Route path="/processing" element={<ProcessingPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/review/:id" element={<ReviewDetailPage />} />
          <Route path="/approvals" element={<ApprovalsPage />} />
          <Route path="/drive-exports" element={<DriveExportsPage />} />
          <Route path="/drive-export/:id" element={<DriveExportDetailPage />} />
          <Route path="/publishing" element={<PublishingPage />} />
          <Route path="/manual-logs" element={<ManualLogsPage />} />
          <Route path="/hooks" element={<HooksPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/activity" element={<ActivityPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </ToastProvider>
  );
}
