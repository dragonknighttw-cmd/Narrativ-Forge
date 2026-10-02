import type {
  EpisodeStatus,
  Category,
  HookType,
  SeriesStatus,
  IdeaStatus,
  Priority,
  ApprovalState,
  ExportState,
  SubtitleState,
  ProcessingJobStatus,
  ProcessingJobType,
  AssetType,
  CopyrightStatus,
  ReviewType,
  PublishingState,
  Platform,
  WorkflowStage,
  SourceType,
  IssueSeverity,
} from "../types";

export const EPISODE_STATUSES: EpisodeStatus[] = [
  "Idea", "Planned", "Script Draft", "Script Review", "Assets Needed",
  "In Production", "Processing", "Subtitle Review", "Needs Approval",
  "Approved", "Exporting", "Exported", "Rejected", "Failed", "Archived",
];

export const CATEGORIES: Category[] = [
  "Educational", "Entertainment", "Tutorial", "Documentary", "Vlog", "Social", "Other",
];

export const HOOK_TYPES: HookType[] = [
  "Question", "Shock", "Mystery", "Warning", "Personal Story", "Contrarian", "Cliffhanger",
];

export const SERIES_STATUSES: SeriesStatus[] = [
  "Concept", "In Development", "Active", "On Hold", "Complete", "Archived",
];

export const IDEA_STATUSES: IdeaStatus[] = [
  "Raw Idea", "Shortlisted", "Developing", "Converted to Episode", "Converted to Series", "Archived",
];

export const PRIORITIES: Priority[] = ["Low", "Medium", "High", "Urgent"];

export const APPROVAL_STATES: ApprovalState[] = [
  "Not Submitted", "Pending Review", "Approved", "Revision Requested", "Rejected",
];

export const EXPORT_STATES: ExportState[] = [
  "Not Ready", "Ready", "Exporting", "Exported", "Failed",
];

export const SUBTITLE_STATES: SubtitleState[] = [
  "Not Started", "Draft", "In Review", "Reviewed", "Approved",
];

export const JOB_STATUSES: ProcessingJobStatus[] = [
  "Queued", "Processing", "Completed", "Failed", "Cancelled", "Retry Pending",
];

export const JOB_TYPES: ProcessingJobType[] = [
  "Audio Extraction", "Transcription", "Timestamp Alignment", "Subtitle Generation",
  "Video Render", "Thumbnail Generation", "Drive Export",
];

export const ASSET_TYPES: AssetType[] = [
  "Video", "Image", "Audio", "Voiceover", "Music", "Subtitle", "Thumbnail", "Reference",
];

export const COPYRIGHT_STATUSES: CopyrightStatus[] = [
  "Original", "Licensed", "Reference Only", "Permission Required", "Unknown",
];

export const REVIEW_TYPES: ReviewType[] = [
  "Script Review", "Visual Review", "Subtitle Review", "Audio Review", "Final Approval",
];

export const PUBLISHING_STATES: PublishingState[] = [
  "Not Ready", "Prepared", "Scheduled Metadata Ready", "Manually Published", "Published Record",
];

export const PLATFORMS: Platform[] = [
  "TikTok", "YouTube Shorts", "Facebook Reels", "Instagram Reels",
];

export const WORKFLOW_STAGES: WorkflowStage[] = [
  "Idea", "Structure", "Script", "Assets", "Processing", "Subtitles", "Review", "Approval", "Output",
];

export const SOURCE_TYPES: SourceType[] = [
  "Original", "Machine Generated", "Human Edited", "Approved",
];

export const ISSUE_SEVERITIES: IssueSeverity[] = ["Info", "Needs Review", "Critical"];

export const STATUS_COLORS: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  "Idea": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Planned": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Script Draft": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30", dot: "bg-primary" },
  "Script Review": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30", dot: "bg-primary" },
  "Assets Needed": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30", dot: "bg-amber" },
  "In Production": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Processing": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Subtitle Review": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30", dot: "bg-amber" },
  "Needs Approval": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30", dot: "bg-amber" },
  "Approved": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Exporting": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Exported": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Rejected": { bg: "bg-error/15", text: "text-error", border: "border-error/30", dot: "bg-error" },
  "Failed": { bg: "bg-error/15", text: "text-error", border: "border-error/30", dot: "bg-error" },
  "Archived": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Concept": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "In Development": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30", dot: "bg-primary" },
  "Active": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "On Hold": { bg: "bg-warning/15", text: "text-warning", border: "border-warning/30", dot: "bg-warning" },
  "Complete": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Raw Idea": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Shortlisted": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Developing": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30", dot: "bg-primary" },
  "Converted to Episode": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Converted to Series": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Queued": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Completed": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Cancelled": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Retry Pending": { bg: "bg-warning/15", text: "text-warning", border: "border-warning/30", dot: "bg-warning" },
  "Not Started": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Draft": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30", dot: "bg-primary" },
  "In Review": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30", dot: "bg-amber" },
  "Reviewed": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Not Submitted": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Pending Review": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30", dot: "bg-amber" },
  "Revision Requested": { bg: "bg-warning/15", text: "text-warning", border: "border-warning/30", dot: "bg-warning" },
  "Not Ready": { bg: "bg-text-muted/15", text: "text-text-muted", border: "border-text-muted/30", dot: "bg-text-muted" },
  "Ready": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30", dot: "bg-secondary" },
  "Prepared": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30", dot: "bg-primary" },
  "Scheduled Metadata Ready": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30", dot: "bg-amber" },
  "Manually Published": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
  "Published Record": { bg: "bg-success/15", text: "text-success", border: "border-success/30", dot: "bg-success" },
};

export function getStatusColor(status: string) {
  return STATUS_COLORS[status] || STATUS_COLORS["Idea"];
}

export const SEVERITY_COLORS: Record<IssueSeverity, { bg: string; text: string; border: string }> = {
  "Info": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30" },
  "Needs Review": { bg: "bg-amber/15", text: "text-amber", border: "border-amber/30" },
  "Critical": { bg: "bg-error/15", text: "text-error", border: "border-error/30" },
};

export const PLATFORM_COLORS: Record<Platform, { bg: string; text: string; border: string }> = {
  "TikTok": { bg: "bg-text-muted/15", text: "text-text-main", border: "border-text-muted/30" },
  "YouTube Shorts": { bg: "bg-error/15", text: "text-error", border: "border-error/30" },
  "Facebook Reels": { bg: "bg-secondary/15", text: "text-secondary", border: "border-secondary/30" },
  "Instagram Reels": { bg: "bg-primary/15", text: "text-primary", border: "border-primary/30" },
};
