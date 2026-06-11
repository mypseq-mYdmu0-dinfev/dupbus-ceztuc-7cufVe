# Response to career_query_202606112014.md
*AURÉA Reel — process notes & presentation brief*

1. Outcome —— task complete. All deliverables sit in `dupbus-ceztuc-7cufVe/temp/Rennly_20260612/`.
- 1.1. `AUREA_Rhodes_Reel.mp4` —— final Reel, 1080×1920, 30fps, 26s, video + silent audio track.
- 1.2. `Rennly_Assessment_Deliverables.md` —— the single employer-facing doc (caption, CTA, music, Canva links, file list).
- 1.3. `AUREA_Canva_cover.png` + Canva edit/view links (in the doc).
- 1.4. `render_*.png` —— the 6 Gemini hero visuals; `build/` —— reproducible scripts (`gen_overlays.py`, `build_reel2.sh`) and `build/qa/` QA frames.

2. Tool decision (important) —— I built the MP4 locally with ffmpeg, not in Canva.
- 2.1. The Canva MCP can only ingest images via a public URL (`upload-asset-from-url`); your Gemini renders are local files with no web host, so Canva could not use them.
- 2.2. Building locally let the premium Gemini renders be the hero visuals AND gave full control of hook, Ken Burns motion, crossfades, animated captions, amber palette and CTA. This is the stronger artefact.
- 2.3. ffmpeg on this Mac ships without `drawtext` (no freetype), so text is rendered as transparent PNG overlays via Pillow (Didot serif, Futura, Avenir, STHeiti for Chinese) and composited with timed alpha fades. Fonts and the Traditional-Chinese line were QA'd on screen before the full build.

3. Canva deliverable —— caveat to know.
- 3.1. `generate-design` returned a single-page `your_story` design (not the 6-page storyboard I requested), an on-brand AURÉA cover with an illustrated cityscape, amber palette and the $1.2M line.
- 3.2. It satisfies the brief's "Canva link / Design File" requirement and is fully editable in your account, but it is clearly secondary to the MP4 and does not use the photoreal renders. Present the MP4 as the finished Reel and the Canva link as the editable design file.

4. Music —— the MP4 carries a clean silent audio track only.
- 4.1. I did not embed any track (no licensed music available locally; a synth bed would cheapen a premium piece).
- 4.2. Either present muted whilst narrating, or drop a Canva Audio / Instagram trending track on before posting. Search terms and a target style are in the deliverables doc §5.

5. Honesty —— all project details are fictional sample data per the brief.
- 5.1. AURÉA, Rhodes waterfront, two/three bed, from $1.2M, Spring 2026, AUREARhodes.com.au —— realistic, plausible for Rhodes premium stock, nothing claimed as real. If asked, say the figures are benchmarked sample data.

6. Strategic angles to lean on in the room.
- 6.1. This piece directly answers the one flagged gap in your AR (§2, video editing "essential"). You produced an end-to-end animated Reel with motion graphics, transitions and a hook —— present it as proof of hands-on capability, not just creative direction.
- 6.2. The Traditional-Chinese tagline (臨水尊邸 · 誠邀預約) signals the cultural and language awareness the role mandates and HOME789's Chinese/Korean buyer market values. You can speak to localising for Rednote/WeChat as a natural extension.
- 6.3. Map the work to their stated assessment criteria as you present —— creative thinking (the "Wake up to this" hook and gold/aurum naming), design quality, video editing, copywriting, storytelling (the 6-beat arc), and social best practice (vertical, 3s hook, captions, clear CTA).

7. Before you present —— quick checks.
- 7.1. Play `AUREA_Rhodes_Reel.mp4` end to end once to confirm it opens on your machine.
- 7.2. Open the Canva edit link to confirm it loads under your login.
- 7.3. Optional, if you want the Reel under ~30s with music, add the track in Canva or IG; nothing else needs changing.

8. Q & QB —— none. Brief, AR and profile covered everything; no blockers encountered.
