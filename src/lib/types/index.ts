export type EpisodeStatus =
  | "Idea"
  | "Planned"
  | "Script Draft"
  | "Script Review"
  | "Assets Needed"
  | "In Production"
  | "Processing"
  | "Subtitle Review"
  | "Needs Approval"
  | "Approved"
  | "Exporting"
  | "Exported"
  | "Rejected"
  | "Failed"
  | "Archived";

export type Category =
  | "Educational"
  | "Entertainment"
  | "Tutorial"
  | "Documentary"
  | "Vlog"
  | "Social"
  | "Other";

export type HookType =
  | "Question"
  | "Shock"
  | "Mystery"
  | "Warning"
  | "Personal Story"
  | "Contrarian"
  | "Cliffhanger";

export type SeriesStatus =
  | "Concept"
  | "In Development"
  | "Active"
  | "On Hold"
  | "Complete"
  | "Archived";

export type IdeaStatus =
  | "Raw Idea"
  | "Shortlisted"
  | "Developing"
  | "Converted to Episode"
  | "Converted to Series"
  | "Archived";

export type Priority = "Low" | "Medium" | "High" | "Urgent";

export type ApprovalState =
  | "Not Submitted"
  | "Pending Review"
  | "Approved"
  | "Revision Requested"
  | "Rejected";

export type ExportState =
  | "Not Ready"
  | "Ready"
  | "Exporting"
  | "Exported"
  | "Failed";

export type SubtitleState =
  | "Not Started"
  | "Draft"
  | "In Review"
  | "Reviewed"
  | "Approved";

export type ProcessingJobStatus =
  | "Queued"
  | "Processing"
  | "Completed"
  | "Failed"
  | "Cancelled"
  | "Retry Pending";

export type ProcessingJobType =
  | "Audio Extraction"
  | "Transcription"
  | "Timestamp Alignment"
  | "Subtitle Generation"
  | "Video Render"
  | "Thumbnail Generation"
  | "Drive Export";

export type AssetType =
  | "Video"
  | "Image"
  | "Audio"
  | "Voiceover"
  | "Music"
  | "Subtitle"
  | "Thumbnail"
  | "Reference";

export type CopyrightStatus =
  | "Original"
  | "Licensed"
  | "Reference Only"
  | "Permission Required"
  | "Unknown";

export type ReviewType =
  | "Script Review"
  | "Visual Review"
  | "Subtitle Review"
  | "Audio Review"
  | "Final Approval";

export type PublishingState =
  | "Not Ready"
  | "Prepared"
  | "Scheduled Metadata Ready"
  | "Manually Published"
  | "Published Record";

export type Platform =
  | "TikTok"
  | "YouTube Shorts"
  | "Facebook Reels"
  | "Instagram Reels";

export type WorkflowStage =
  | "Idea"
  | "Structure"
  | "Script"
  | "Assets"
  | "Processing"
  | "Subtitles"
  | "Review"
  | "Approval"
  | "Output";

export type SourceType =
  | "Original"
  | "Machine Generated"
  | "Human Edited"
  | "Approved";

export type IssueSeverity = "Info" | "Needs Review" | "Critical";

export type SubtitleIssueType =
  | "Subtitle too long"
  | "Appears too briefly"
  | "Caption overlap"
  | "Missing translation"
  | "Potential spelling issue"
  | "Punctuation issue"
  | "Safe area issue"
  | "Early/late caption";

export interface Series {
  id: string;
  title: string;
  genre: string;
  category: Category;
  description: string;
  status: SeriesStatus;
  seasonCount: number;
  episodeCount: number;
  progress: number;
  coverGradient: string;
  updatedAt: string;
  targetAudience: string;
  tone: string;
  language: string;
  subtitleLanguage: string;
  defaultDuration: string;
  publishingPlatforms: Platform[];
  synopsis: string;
}

export interface Season {
  id: string;
  seriesId: string;
  number: number;
  title: string;
  episodeCount: number;
}

export interface Episode {
  id: string;
  publicId: string;
  number: number;
  title: string;
  burmeseTitle: string;
  seriesId: string;
  seriesTitle: string;
  seasonNumber: number;
  category: Category;
  thumbnailGradient: string;
  duration: string;
  status: EpisodeStatus;
  currentStep: WorkflowStage;
  progress: number;
  subtitleState: SubtitleState;
  approvalState: ApprovalState;
  exportState: ExportState;
  updatedAt: string;
  logline: string;
  synopsis: string;
  emotionalTone: string;
  targetDuration: string;
  hook: string;
  cta: string;
  contentWarnings: string[];
  productionTime: string;
  checklist: { label: string; done: boolean }[];
  sceneCount: number;
  hasVideo: boolean;
  hasTranscript: boolean;
  hasThumbnail: boolean;
  criticalIssues: number;
}

export interface Idea {
  id: string;
  title: string;
  concept: string;
  category: Category;
  hookType: HookType;
  emotion: string;
  priority: Priority;
  status: IdeaStatus;
  createdAt: string;
  reference: string;
  notes: string;
  convertedTarget: string;
}

export interface ScriptBlock {
  id: string;
  type:
    | "Scene Heading"
    | "Action"
    | "Dialogue"
    | "Voiceover"
    | "On-Screen Text"
    | "Camera Note"
    | "Sound/Music Note"
    | "Transition";
  content: string;
  order: number;
}

export interface Script {
  id: string;
  episodeId: string;
  blocks: ScriptBlock[];
  wordCount: number;
  estimatedDuration: string;
  language: string;
  emotionalTone: string;
  hookStrength: string;
  cta: string;
  version: string;
  lastEdited: string;
  sourceType: SourceType;
}

export interface Scene {
  id: string;
  episodeId: string;
  number: number;
  title: string;
  durationTarget: string;
  location: string;
  characters: string[];
  visualDirection: string;
  voiceoverSummary: string;
  requiredAssets: string[];
  status: "Draft" | "Ready" | "Complete" | "Flagged";
  warning: string | null;
  gradient: string;
}

export interface Asset {
  id: string;
  name: string;
  type: AssetType;
  duration: string;
  dimensions: string;
  fileSize: string;
  episodeId: string;
  episodeTitle: string;
  sceneId: string;
  version: string;
  isFinal: boolean;
  copyrightStatus: CopyrightStatus;
  updatedAt: string;
  gradient: string;
}

export interface SubtitleCue {
  id: string;
  number: number;
  start: string;
  end: string;
  duration: string;
  originalText: string;
  burmeseText: string;
  sourceType: SourceType;
  reviewStatus: "Pending" | "Reviewed" | "Approved";
  issue: string | null;
  issueType: SubtitleIssueType | null;
  severity: IssueSeverity | null;
  reviewerNote: string;
}

export interface SubtitlePreset {
  id: string;
  name: string;
  font: string;
  fontSize: string;
  color: string;
  background: string;
  outline: string;
  position: string;
  maxCharsPerLine: number;
  maxLines: number;
  minDisplayTime: string;
  maxDisplayTime: string;
  isDefault: boolean;
  previewGradient: string;
}

export interface ProcessingJob {
  id: string;
  jobId: string;
  episodeId: string;
  episodeTitle: string;
  type: ProcessingJobType;
  status: ProcessingJobStatus;
  progress: number;
  started: string;
  duration: string;
  retryCount: number;
  errorMessage: string | null;
  input: string;
  output: string;
}

export interface ReviewItem {
  id: string;
  episodeId: string;
  episodeTitle: string;
  seriesTitle: string;
  reviewType: ReviewType;
  priority: Priority;
  issueCount: number;
  criticalIssues: number;
  dueDate: string;
  publicId: string;
  thumbnailGradient: string;
}

export interface DriveExport {
  id: string;
  episodeId: string;
  episodeTitle: string;
  publicId: string;
  status: ExportState;
  progress: number;
  exportDate: string;
  fileCount: number;
  driveFolderId: string;
  requiredFiles: { name: string; present: boolean }[];
  dateFolder: string;
}

export interface Hook {
  id: string;
  text: string;
  type: HookType;
  topic: string;
  emotion: string;
  usageCount: number;
  averageViews: number;
  completionRate: number;
  shares: number;
  performanceScore: number;
  isDefault: boolean;
  isRecommended: boolean;
}

export interface ManualProductionLog {
  id: string;
  videoId: string;
  topic: string;
  hook: string;
  hookType: HookType;
  category: Category;
  duration: string;
  sceneCount: number;
  toolsUsed: string[];
  subtitleStyle: string;
  productionTime: string;
  published: boolean;
  views: number;
  completionRate: number;
  shares: number;
  saves: number;
  notes: string;
  qualityScore: number;
  platform: Platform;
  manualErrors: string;
  scriptLength: string;
  voiceTool: string;
  imageTool: string;
  videoTool: string;
}

export interface PublishingRecord {
  id: string;
  episodeId: string;
  episodeTitle: string;
  publicId: string;
  platform: Platform;
  caption: string;
  hashtags: string[];
  scheduledDate: string;
  state: PublishingState;
  thumbnailGradient: string;
  formatReady: boolean;
  thumbnailReady: boolean;
  subtitleReady: boolean;
  platformUrl: string;
  notes: string;
}

export interface AnalyticsRecord {
  id: string;
  episodeId: string;
  episodeTitle: string;
  platform: Platform;
  views: number;
  watchTime: string;
  completionRate: number;
  shares: number;
  saves: number;
  comments: number;
  linkClicks: number;
  recordedDate: string;
}

export interface ActivityEvent {
  id: string;
  timestamp: string;
  actor: string;
  role: string;
  action: string;
  target: string;
  previousState: string;
  newState: string;
  requestId: string;
}

export interface Character {
  id: string;
  seriesId: string;
  name: string;
  role: string;
  personality: string;
  visualTraits: string;
  voiceNotes: string;
  continuityWarnings: string;
  gradient: string;
}

export interface VisualStyle {
  id: string;
  seriesId: string;
  palette: string[];
  lighting: string;
  cameraStyle: string;
  imageStyle: string;
  aspectRatio: string;
  promptGuidance: string;
  referenceFrames: string[];
}

export interface Notification {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  time: string;
  episodeId: string;
  read: boolean;
}

export interface MockSession {
  email: string;
  name: string;
  role: string;
  loginTime: string;
}
