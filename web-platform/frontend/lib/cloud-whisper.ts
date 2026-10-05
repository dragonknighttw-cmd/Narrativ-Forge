export type CloudWhisperResult = {
  provider: string;
  model: string;
  episode_id: string;
  text: string;
  word_count: number;
  vtt: string;
};

type FFmpegInstance = {
  load(options: { coreURL: string; wasmURL: string }): Promise<void>;
  writeFile(name: string, data: Uint8Array): Promise<void>;
  exec(args: string[]): Promise<number>;
  readFile(name: string): Promise<Uint8Array>;
  deleteFile(name: string): Promise<void>;
};

let ffmpegPromise: Promise<FFmpegInstance> | null = null;

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) {
      if ((existing as HTMLScriptElement).dataset.loaded === "true") return resolve();
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("Failed to load ffmpeg.wasm runtime")), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.onload = () => { script.dataset.loaded = "true"; resolve(); };
    script.onerror = () => reject(new Error("Failed to load ffmpeg.wasm runtime"));
    document.head.appendChild(script);
  });
}

async function loadFFmpeg(): Promise<FFmpegInstance> {
  if (ffmpegPromise) return ffmpegPromise;
  ffmpegPromise = (async () => {
    await loadScript("https://cdn.jsdelivr.net/npm/@ffmpeg/ffmpeg@0.12.15/dist/umd/ffmpeg.js");
    const FFmpegCtor = (window as unknown as { FFmpeg?: { FFmpeg: new () => FFmpegInstance } }).FFmpeg?.FFmpeg;
    if (!FFmpegCtor) throw new Error("ffmpeg.wasm runtime is unavailable");
    const ffmpeg = new FFmpegCtor();
    await ffmpeg.load({
      coreURL: "https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.10/dist/umd/ffmpeg-core.js",
      wasmURL: "https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.10/dist/umd/ffmpeg-core.wasm",
    });
    return ffmpeg;
  })();
  return ffmpegPromise;
}

export async function transcribeVideoWithCloudflare(
  episodeId: string,
  file: File,
  getToken: () => Promise<{ worker_url: string; token: string }>,
  onProgress?: (message: string) => void,
): Promise<CloudWhisperResult> {
  if (file.size <= 0) throw new Error("Choose a non-empty video file");
  onProgress?.("Loading ffmpeg.wasm…");
  const ffmpeg = await loadFFmpeg();
  const input = `input-${Date.now()}.${file.name.split(".").pop() || "mp4"}`;
  const output = `audio-${Date.now()}.wav`;

  try {
    onProgress?.("Extracting 16 kHz mono audio in your browser…");
    await ffmpeg.writeFile(input, new Uint8Array(await file.arrayBuffer()));
    await ffmpeg.exec(["-i", input, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", output]);
    const audio = await ffmpeg.readFile(output);
    if (audio.byteLength > 50 * 1024 * 1024) {
      throw new Error("Extracted audio is larger than 50 MB. Use a shorter source or lower the audio bitrate.");
    }

    const { worker_url, token } = await getToken();
    onProgress?.("Sending audio to Cloudflare Whisper…");
    const response = await fetch(worker_url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "audio/wav",
        "X-Narrativ-Episode": episodeId,
      },
      body: audio,
    });
    if (!response.ok) {
      let detail = "Cloudflare Whisper request failed";
      try { detail = (await response.json() as { error?: string; detail?: string }).detail ?? (await response.clone().json() as { error?: string }).error ?? detail; } catch {}
      throw new Error(detail);
    }
    onProgress?.("Cloud transcription complete");
    return await response.json() as CloudWhisperResult;
  } finally {
    try { await ffmpeg.deleteFile(input); } catch {}
    try { await ffmpeg.deleteFile(output); } catch {}
  }
}
