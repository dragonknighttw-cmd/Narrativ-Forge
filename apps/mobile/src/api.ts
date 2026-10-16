import { Episode, ProductionJob } from './types';

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8001';

export const api = {
  async getEpisodes(): Promise<Episode[]> {
    try {
      const res = await fetch(`${API_BASE}/api/v1/episodes`);
      if (!res.ok) throw new Error('Failed to fetch episodes');
      const data = await res.json();
      return Array.isArray(data) ? data : data.items || [];
    } catch (e) {
      console.warn('API error, returning fallback episodes', e);
      return [
        {
          id: 'ep-001',
          public_id: 'NF-EP-01',
          title: 'သမိုင်းဦးကာလ ပုဂံအစ (Origins of Bagan)',
          series_id: 'series-01',
          episode_number: 1,
          status: 'needs_approval',
          target_duration_seconds: 180,
          synopsis: 'Burmese short-form vertical video: 9:16 format with auto voiceover and scenes.',
          video_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
          myanmar_title: 'ပုဂံခေတ်ဦး သမိုင်းကြောင်း',
          hashtags: ['#Bagan', '#MyanmarHistory', '#Shorts', '#ViralMyanmar'],
          created_at: new Date().toISOString()
        },
        {
          id: 'ep-002',
          public_id: 'NF-EP-02',
          title: 'မြန်မာ့ရိုးရာအစားအစာ - မုန့်ဟင်းခါးလျှို့ဝှက်ချက်',
          series_id: 'series-02',
          episode_number: 2,
          status: 'processing',
          target_duration_seconds: 165,
          synopsis: 'Cultural food series Episode 2 - Full AI generation pipeline.',
          created_at: new Date().toISOString()
        }
      ];
    }
  },

  async getJobs(): Promise<ProductionJob[]> {
    try {
      const res = await fetch(`${API_BASE}/api/v1/jobs`);
      if (!res.ok) throw new Error('Failed to fetch jobs');
      const data = await res.json();
      return Array.isArray(data) ? data : data.items || [];
    } catch (e) {
      return [
        {
          id: 'job-101',
          episode_id: 'ep-002',
          episode_title: 'မြန်မာ့ရိုးရာအစားအစာ - မုန့်ဟင်းခါး',
          step: 'Voiceover Synthesis',
          progress: 68,
          status: 'running',
          current_task: 'Generating Myanmar TTS Audio track (Edge Worker)',
          updated_at: new Date().toISOString()
        }
      ];
    }
  },

  async approveEpisode(id: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/api/v1/review/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true })
      });
      return res.ok;
    } catch {
      return true; // Mock success
    }
  },

  async rejectEpisode(id: string, reason: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/api/v1/review/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      return res.ok;
    } catch {
      return true;
    }
  }
};
