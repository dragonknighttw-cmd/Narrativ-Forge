export type EpisodeStatus =
  | 'idea'
  | 'planned'
  | 'script_draft'
  | 'script_review'
  | 'assets_needed'
  | 'in_production'
  | 'processing'
  | 'subtitle_review'
  | 'needs_approval'
  | 'approved'
  | 'exporting'
  | 'exported'
  | 'archived'
  | 'rejected'
  | 'failed';

export interface Episode {
  id: string;
  public_id: string;
  title: string;
  series_id: string;
  episode_number: number;
  status: EpisodeStatus;
  target_duration_seconds: number;
  synopsis?: string;
  video_url?: string;
  thumbnail_url?: string;
  myanmar_title?: string;
  hashtags?: string[];
  created_at: string;
}

export interface ProductionJob {
  id: string;
  episode_id: string;
  episode_title: string;
  step: string;
  progress: number;
  status: 'queued' | 'running' | 'completed' | 'failed';
  current_task: string;
  updated_at: string;
}
