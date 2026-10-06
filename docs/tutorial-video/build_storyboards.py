from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


BASE = Path(__file__).resolve().parent
REPO = BASE.parent.parent
ASSETS = REPO / "docs" / "tutorial-assets"
BRAND_MARK = REPO / "apps" / "web" / "public" / "brand" / "studyverse-ai-mark.png"
WORK = BASE / ".work"
SCENE_DIR = WORK / "scenes"
WIDTH, HEIGHT = 1920, 1080
SCREEN_X, SCREEN_Y = 42, 170
SCREEN_W, SCREEN_H = 1450, 797
PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 1530, 170, 348, 797
GAP_SECONDS = 0.62
FONT_DIR = Path("C:/Windows/Fonts")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = ([FONT_DIR / "seguisb.ttf", FONT_DIR / "arialbd.ttf"] if bold
                  else [FONT_DIR / "segoeui.ttf", FONT_DIR / "arial.ttf"])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap_pixels(draw: ImageDraw.ImageDraw, text: str, use_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), candidate, font=use_font)[2] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], use_font: ImageFont.FreeTypeFont,
                 fill: tuple[int, int, int], max_width: int, line_gap: int = 7) -> int:
    x, y = xy
    for line in wrap_pixels(draw, text, use_font, max_width):
        draw.text((x, y), line, font=use_font, fill=fill)
        box = draw.textbbox((x, y), line, font=use_font)
        y += box[3] - box[1] + line_gap
    return y


def make_background(accent: tuple[int, int, int]) -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(base)
    top, bottom = (8, 8, 15), (13, 14, 28)
    for y in range(HEIGHT):
        amount = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1 - amount) + bottom[i] * amount) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((60, 100, 760, 760), fill=(*accent, 65))
    glow_draw.ellipse((1150, 180, 1960, 800), fill=(57, 72, 160, 32))
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    return Image.alpha_composite(base.convert("RGBA"), glow).convert("RGB")


def scene_frame(scene: dict, index: int, total: int) -> Image.Image:
    accent = tuple(scene.get("accent", [161, 88, 255]))
    frame = make_background(accent)
    draw = ImageDraw.Draw(frame)
    white, muted, soft = (246, 243, 255), (174, 171, 191), (123, 119, 143)

    # Header and chapter counter use the supplied StudyVerse logo.
    with Image.open(BRAND_MARK) as brand:
        mark = ImageOps.contain(brand.convert("RGB"), (50, 40), method=Image.Resampling.LANCZOS)
    logo_box = (38, 34, 38 + mark.width, 34 + mark.height)
    frame.paste(ImageChops.lighter(frame.crop(logo_box), mark), (logo_box[0], logo_box[1]))
    draw = ImageDraw.Draw(frame)
    draw.text((94, 39), "STUDYVERSE AI", font=font(20, True), fill=white)
    draw.text((270, 43), "LEARN · ASK · GROW  /  FIRST-TIME STUDENT GUIDE", font=font(14, True), fill=soft)
    badge = f"CHAPTER {index:02d} / {total:02d}"
    bbox = draw.textbbox((0, 0), badge, font=font(15, True))
    badge_width = bbox[2] + 34
    draw.rounded_rectangle((WIDTH - 42 - badge_width, 35, WIDTH - 42, 76), radius=18,
                           fill=(29, 25, 43), outline=(72, 56, 103), width=1)
    draw.text((WIDTH - 42 - badge_width + 17, 47), badge, font=font(15, True), fill=(208, 181, 255))

    # Actual StudyVerse screen and selected navigation tab.
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((SCREEN_X - 3, SCREEN_Y - 3, SCREEN_X + SCREEN_W + 3, SCREEN_Y + SCREEN_H + 3),
                                  radius=19, fill=(0, 0, 0, 175))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    frame = Image.alpha_composite(frame.convert("RGBA"), shadow).convert("RGB")
    source_path = ASSETS / scene["screenshot"]
    with Image.open(source_path) as source:
        shot = ImageOps.fit(source.convert("RGB"), (SCREEN_W, SCREEN_H), method=Image.Resampling.LANCZOS,
                            centering=(0.5, 0.5))
    mask = Image.new("L", (SCREEN_W, SCREEN_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, SCREEN_W - 1, SCREEN_H - 1), radius=16, fill=255)
    frame.paste(shot, (SCREEN_X, SCREEN_Y), mask)
    ImageDraw.Draw(frame).rounded_rectangle((SCREEN_X, SCREEN_Y, SCREEN_X + SCREEN_W, SCREEN_Y + SCREEN_H),
                                            radius=16, outline=(69, 62, 89), width=2)

    # Teaching panel beside the live screen.
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H), radius=24,
                           fill=(18, 17, 29), outline=(53, 48, 70), width=2)
    x, right_width = PANEL_X + 26, PANEL_W - 52
    y = PANEL_Y + 28
    draw.text((x, y), "YOU ARE HERE", font=font(13, True), fill=tuple(min(255, c + 25) for c in accent))
    y += 31
    y = draw_wrapped(draw, scene["tab"], (x, y), font(16, True), (202, 196, 222), right_width, line_gap=4) + 14
    y = draw_wrapped(draw, scene["title"], (x, y), font(36, True), white, right_width, line_gap=4) + 15
    y = draw_wrapped(draw, scene["summary"], (x, y), font(19), muted, right_width, line_gap=7) + 26
    draw.text((x, y), "WHAT TO DO", font=font(13, True), fill=soft)
    y += 31
    for point in scene["points"]:
        draw.ellipse((x, y + 8, x + 8, y + 16), fill=accent)
        y = draw_wrapped(draw, point, (x + 18, y), font(17, True), (224, 220, 237), right_width - 20, line_gap=5) + 14

    next_y = PANEL_Y + PANEL_H - 114
    draw.line((x, next_y - 21, PANEL_X + PANEL_W - 26, next_y - 21), fill=(56, 50, 72), width=1)
    draw.text((x, next_y), "NEXT", font=font(12, True), fill=soft)
    draw_wrapped(draw, scene["next"], (x, next_y + 24), font(17, True), white, right_width, line_gap=4)

    draw.text((42, 1000), "The selected tab is highlighted in the left navigation.", font=font(15), fill=(145, 141, 163))
    bar_x, bar_y, bar_width = 42, 1044, WIDTH - 84
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + 6), radius=3, fill=(34, 31, 48))
    progress = max(1, int(bar_width * index / total))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + progress, bar_y + 6), radius=3, fill=accent)
    return frame


def seconds_to_srt(value: float) -> str:
    milliseconds = max(0, round(value * 1000))
    hours, rem = divmod(milliseconds, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def main() -> None:
    scene_data = json.loads((BASE / "scenes.json").read_text(encoding="utf-8"))
    scenes = scene_data["scenes"]
    audio_durations_path = WORK / "audio-durations.json"
    audio_durations = json.loads(audio_durations_path.read_text(encoding="utf-8")) if audio_durations_path.exists() else None
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    chapter_durations: list[float] = []
    subtitle_blocks: list[str] = []
    transcript: list[str] = [f"# {scene_data['title']}\n"]
    cursor = 0.0

    for index, scene in enumerate(scenes, start=1):
        word_count = len(scene["voiceover"].split())
        duration = audio_durations[index - 1] if audio_durations else max(6.5, word_count / 3.0 + 0.8)
        chapter_durations.append(duration + (GAP_SECONDS if index < len(scenes) else 0.0))

        slide = scene_frame(scene, index, len(scenes))
        slide.save(SCENE_DIR / f"scene-{index:02d}.png", optimize=True)
        if index == 1:
            slide.save(BASE / "thumbnail.png", optimize=True)
        transcript.append(f"## {index:02d}. {scene['tab']} - {scene['title']}\n\n{scene['voiceover']}\n")

        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", scene["voiceover"]) if part.strip()]
        total_words = sum(max(1, len(part.split())) for part in sentences)
        scene_cursor = cursor
        for sentence in sentences:
            sentence_words = max(1, len(sentence.split()))
            sentence_duration = duration * sentence_words / total_words
            start, end = scene_cursor, min(cursor + duration, scene_cursor + sentence_duration)
            subtitle_blocks.append(f"{len(subtitle_blocks) + 1}\n{seconds_to_srt(start)} --> {seconds_to_srt(end)}\n{sentence}\n")
            scene_cursor = end
        cursor += duration + GAP_SECONDS

    if not scenes:
        raise RuntimeError("No tutorial scenes were defined.")
    (BASE / "subtitles.srt").write_text("\n".join(subtitle_blocks).strip() + "\n", encoding="utf-8")
    (BASE / "narration.md").write_text("\n".join(transcript).strip() + "\n", encoding="utf-8")
    (WORK / "durations.json").write_text(json.dumps(chapter_durations, indent=2), encoding="utf-8")
    print(f"Prepared {len(scenes)} scenes; estimated reading time {sum(chapter_durations):.1f}s; 1920x1080.")


if __name__ == "__main__":
    main()
