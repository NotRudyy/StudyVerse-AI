# StudyVerse AI walkthrough video

The MP4 is a narrated, captioned first-time tour of the actual StudyVerse demo screens. It uses the supplied StudyVerse AI logo, explains the navigation tabs, calls out useful options, and follows the suggested study loop. It is H.264 1920×1080 at 24 fps, with spoken English narration and an embedded, selectable English caption track.

- [Watch the video](StudyVerse-AI-Tutorial.mp4)
- [Read the narration transcript](narration.md)
- [Subtitles](subtitles.srt) are embedded in the MP4 as a selectable English caption track.
- [Thumbnail](thumbnail.png)

The tour covers Overview, StudyPacks, Nova Tutor, Practice, Boss Battle, Flashcards, Mistake Lab, Skill Tree, Study Planner, Focus Room, Study Wrapped, Study Rooms, and Profile. Screenshots were captured from the running demo; no sample materials were uploaded.

The browser demo uses seeded data and session-local progress. The narration calls this out and distinguishes the room directory from future real-time chat and presence. Only the narration script is sent to Microsoft Edge TTS when regenerating the voice track; uploaded study materials are not sent.

## Rebuild on Windows

The storyboard builder needs Pillow, the voice generator needs `edge-tts`, and the renderer needs `imageio-ffmpeg` or `ffmpeg` on `PATH`.

```powershell
python -m pip install -r requirements.txt
python .\generate_audio.py
python .\build_storyboards.py
python .\render_video.py
```

Intermediate audio, slides, and encoded chapters are ignored under `.work/`.
