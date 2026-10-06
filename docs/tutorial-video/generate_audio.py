from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import edge_tts


BASE = Path(__file__).resolve().parent
WORK = BASE / ".work"
AUDIO_DIR = WORK / "audio"
SCENES = json.loads((BASE / "scenes.json").read_text(encoding="utf-8"))["scenes"]
VOICE = "en-US-AriaNeural"
RATE = "+0%"
TOOLS = Path(r"C:\Users\User\AppData\Local\Temp\studyverse_tutorial_tools")
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
try:
    from imageio_ffmpeg import get_ffmpeg_exe

    FFMPEG = get_ffmpeg_exe()
except Exception:
    FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


def media_duration(path: Path) -> float:
    result = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)", result.stderr)
    if not match:
        raise RuntimeError(f"Could not read narration duration for {path.name}: {result.stderr[-1000:]}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


async def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    durations: list[float] = []
    for index, scene in enumerate(SCENES, start=1):
        target = AUDIO_DIR / f"scene-{index:02d}.mp3"
        await edge_tts.Communicate(scene["voiceover"], VOICE, rate=RATE).save(str(target))
        duration = media_duration(target)
        durations.append(duration)
        print(f"Generated chapter {index:02d}/{len(SCENES)}: {duration:.2f}s")
    (WORK / "audio-durations.json").write_text(json.dumps(durations, indent=2), encoding="utf-8")
    print(f"Voice: {VOICE}; total speech: {sum(durations):.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
