import React, { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { cn } from "../../lib/utils";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

const pageTitles: Record<string, { title: string; breadcrumb: { label: string; path?: string }[] }> = {
  "/dashboard": { title: "Studio Overview", breadcrumb: [{ label: "Overview" }, { label: "Studio Overview" }] },
  "/ideas": { title: "Content Ideas", breadcrumb: [{ label: "Content" }, { label: "Content Ideas" }] },
  "/series": { title: "All Series", breadcrumb: [{ label: "Content" }, { label: "All Series" }] },
  "/episodes": { title: "Episodes", breadcrumb: [{ label: "Content" }, { label: "Episodes" }] },
  "/scripts": { title: "Script Studio", breadcrumb: [{ label: "Production" }, { label: "Script Studio" }] },
  "/scenes": { title: "Scene Breakdown", breadcrumb: [{ label: "Production" }, { label: "Scene Breakdown" }] },
  "/assets": { title: "Asset Library", breadcrumb: [{ label: "Production" }, { label: "Asset Library" }] },
  "/video": { title: "Video Projects", breadcrumb: [{ label: "Production" }, { label: "Video Projects" }] },
  "/subtitles": { title: "Subtitle Studio", breadcrumb: [{ label: "Production" }, { label: "Subtitle Studio" }] },
  "/processing": { title: "Processing Queue", breadcrumb: [{ label: "Production" }, { label: "Processing Queue" }] },
  "/presets": { title: "Subtitle Presets", breadcrumb: [{ label: "Production" }, { label: "Subtitle Presets" }] },
  "/review": { title: "Review Center", breadcrumb: [{ label: "Review & Output" }, { label: "Review Center" }] },
  "/approvals": { title: "Approval History", breadcrumb: [{ label: "Review & Output" }, { label: "Approval History" }] },
  "/drive-exports": { title: "Drive Exports", breadcrumb: [{ label: "Review & Output" }, { label: "Drive Exports" }] },
  "/publishing": { title: "Publishing Preparation", breadcrumb: [{ label: "Review & Output" }, { label: "Publishing Preparation" }] },
  "/manual-logs": { title: "Manual Production Log", breadcrumb: [{ label: "Review & Output" }, { label: "Manual Production Log" }] },
  "/hooks": { title: "Hook Library", breadcrumb: [{ label: "Content" }, { label: "Hook Library" }] },
  "/analytics": { title: "Analytics", breadcrumb: [{ label: "Insights" }, { label: "Analytics" }] },
  "/activity": { title: "Activity Log", breadcrumb: [{ label: "System" }, { label: "Activity Log" }] },
  "/settings": { title: "Settings", breadcrumb: [{ label: "System" }, { label: "Settings" }] },
};

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  useEffect(() => {
    const session = localStorage.getItem("narrativ_session");
    if (!session) {
      navigate("/login");
      return;
    }
  }, [navigate]);

  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [location.pathname]);

  const pathMatch = Object.keys(pageTitles).find((p) => location.pathname.startsWith(p));
  const pageInfo = pathMatch
    ? pageTitles[pathMatch]
    : { title: "Narrativ Forge", breadcrumb: [{ label: "Narrativ Forge" }] };

  if (location.pathname.match(/\/episodes\/[^/]+$/)) {
    pageInfo.title = "Episode Detail";
    pageInfo.breadcrumb = [{ label: "Content" }, { label: "Episodes", path: "/episodes" }, { label: "Episode Detail" }];
  } else if (location.pathname.match(/\/series\/[^/]+$/)) {
    pageInfo.title = "Series Detail";
    pageInfo.breadcrumb = [{ label: "Content" }, { label: "All Series", path: "/series" }, { label: "Series Detail" }];
  } else if (location.pathname.match(/\/review\/[^/]+$/)) {
    pageInfo.title = "Review Detail";
    pageInfo.breadcrumb = [{ label: "Review & Output" }, { label: "Review Center", path: "/review" }, { label: "Review Detail" }];
  } else if (location.pathname.match(/\/scripts\/[^/]+$/)) {
    pageInfo.title = "Script Editor";
    pageInfo.breadcrumb = [{ label: "Production" }, { label: "Script Studio", path: "/scripts" }, { label: "Script Editor" }];
  } else if (location.pathname.match(/\/subtitle-studio\/[^/]+$/)) {
    pageInfo.title = "Subtitle Studio";
    pageInfo.breadcrumb = [{ label: "Production" }, { label: "Subtitle Studio", path: "/subtitles" }, { label: "Editor" }];
  } else if (location.pathname.match(/\/video-projects\/[^/]+$/)) {
    pageInfo.title = "Video Project";
    pageInfo.breadcrumb = [{ label: "Production" }, { label: "Video Projects", path: "/video" }, { label: "Project" }];
  } else if (location.pathname.match(/\/episodes\/[^/]+\/scenes$/)) {
    pageInfo.title = "Scene Breakdown";
    pageInfo.breadcrumb = [{ label: "Production" }, { label: "Scene Breakdown", path: "/scenes" }, { label: "Episode Scenes" }];
  }

  return (
    <div className="h-screen flex bg-bg overflow-hidden">
      <div className="hidden lg:block">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {mobileSidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-bg/80 backdrop-blur-sm" onClick={() => setMobileSidebarOpen(false)} />
          <div className="relative animate-slide-right">
            <Sidebar
              collapsed={false}
              onToggleCollapse={() => {}}
              onNavigate={() => setMobileSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onMenuClick={() => setMobileSidebarOpen(true)}
          pageTitle={pageInfo.title}
          breadcrumb={pageInfo.breadcrumb}
        />
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 md:p-6 animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
