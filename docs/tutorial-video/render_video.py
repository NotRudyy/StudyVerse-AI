from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
WORK = BASE / ".work"
SCENES = WORK / "scenes"
OUTPUT = BASE / "StudyVerse-AI-Tutorial.mp4"
FPS = 24
GAP_SECONDS = 0.62
ENCODE_PROFILE = "1080p-crf13-medium-v3-brand"
TOOLS = Path(r"C:\Users\User\AppData\Local\Temp\studyverse_tutorial_tools")

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

try:
    from imageio_ffmpeg import get_ffmpeg_exe

    FFMPEG = get_ffmpeg_exe()
except Exception:
    FFMPEG = os.environ.get("FFMPEG", "ffmpeg")


def run(args: list[str]) -> str:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(args[:5])}\n{result.stdout[-5000:]}")
    return result.stdout


def main() -> None:
    scenes = json.loads((BASE / "scenes.json").read_text(encoding="utf-8"))["scenes"]
    durations = json.loads((WORK / "durations.json").read_text(encoding="utf-8"))
    clips_dir = WORK / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    clip_files: list[Path] = []
    profile_path = WORK / "encode-profile.txt"
    previous_profile = profile_path.read_text(encoding="utf-8").strip() if profile_path.exists() else ""
    if previous_profile != ENCODE_PROFILE:
        for stale in clips_dir.glob("scene-*.mp4"):
            stale.unlink()
        profile_path.write_text(ENCODE_PROFILE, encoding="utf-8")

    for index, duration in enumerate(durations, start=1):
        image_path = SCENES / f"scene-{index:02d}.png"
        clip_path = clips_dir / f"scene-{index:02d}.mp4"
        clip_files.append(clip_path)
        if clip_path.exists() and clip_path.stat().st_size > 100_000:
            print(f"Using existing chapter {index:02d}/{len(durations)}")
            continue
        fade = min(0.28, duration / 8)
        video_filter = (
            "scale=1920:1080,"
            "zoompan=z='min(zoom+0.00012,1.024)':x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,"
            f"fade=t=in:st=0:d={fade:.3f},fade=t=out:st={max(0.0, duration - fade):.3f}:d={fade:.3f},"
            "format=yuv420p"
        )
        run([
            FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", str(image_path),
            "-t", f"{duration:.3f}", "-vf", video_filter, "-an", "-c:v", "libx264", "-preset", "medium",
            "-crf", "13", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(clip_path)
        ])
        print(f"Encoded chapter {index:02d}/{len(durations)}")

    concat_lines = []
    for clip_path in clip_files:
        safe_path = clip_path.as_posix().replace("'", "'\\''")
        concat_lines.append("file '" + safe_path + "'")
    list_path = WORK / "clips.txt"
    list_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    audio_paths = [WORK / "audio" / f"scene-{index:02d}.mp3" for index in range(1, len(durations) + 1)]
    has_narration = all(path.exists() for path in audio_paths)
    if not has_narration:
        print("Narration audio is not available; creating a high-quality captioned video without voice.")
        run([
            FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-i", str(BASE / "subtitles.srt"), "-map", "0:v:0", "-map", "1:s:0", "-c:v", "copy",
            "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-metadata:s:s:0", "title=English captions",
            "-disposition:s:0", "default", "-movflags", "+faststart", str(OUTPUT)
        ])
    else:
        audio_inputs: list[str] = []
        filter_parts: list[str] = []
        concat_labels: list[str] = []
        for index, audio_path in enumerate(audio_paths):
            audio_inputs.extend(["-i", str(audio_path)])
            label = f"voice{index}"
            pad = f",apad=pad_dur={GAP_SECONDS:.2f}" if index < len(audio_paths) - 1 else ""
            filter_parts.append(f"[{index}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo{pad}[{label}]")
            concat_labels.append(f"[{label}]")
        filter_parts.append("".join(concat_labels) + f"concat=n={len(audio_paths)}:v=0:a=1[aout]")
        narration = WORK / "narration.m4a"
        run([
            FFMPEG, "-y", "-loglevel", "error", *audio_inputs, "-filter_complex", ";".join(filter_parts),
            "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", str(narration)
        ])
        run([
            FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-i", str(narration), "-i", str(BASE / "subtitles.srt"), "-map", "0:v:0", "-map", "1:a:0", "-map", "2:s:0",
            "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
            "-metadata:s:s:0", "title=English captions", "-disposition:s:0", "default", "-movflags", "+faststart", str(OUTPUT)
        ])
    probe = subprocess.run([FFMPEG, "-i", str(OUTPUT)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, encoding="utf-8", errors="replace")
    info = probe.stdout
    if OUTPUT.stat().st_size < 1_000_000 or "Video:" not in info or (has_narration and "Audio:" not in info) or "Subtitle:" not in info:
        raise RuntimeError(f"Rendered video did not pass the media probe.\n{info[-4000:]}")
    run([FFMPEG, "-y", "-loglevel", "error", "-ss", "00:00:36", "-i", str(OUTPUT), "-frames:v", "1",
         str(WORK / "video-preview-frame.png")])
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size / (1024 * 1024):.1f} MiB).")
    print("\n".join(line.strip() for line in info.splitlines() if "Duration:" in line or "Video:" in line or "Audio:" in line or "Subtitle:" in line))


if __name__ == "__main__":
    main()
