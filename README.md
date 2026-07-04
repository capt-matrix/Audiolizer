# Audiolizer (ADLiz)

Convert guitar tab notation into synchronized audio + video.

## How it works

```
Config (chords, strum/pick patterns, song DSL)
  → AC binary (guitar frame data)
    → MIDI → WAV (via FluidSynth + SoundFont)
    → Pygame fretboard visualization → MP4 (via FFmpeg)
```

## Quick start

```bash
pip install pygame opencv-python-headless psutil platformdirs midiutil
python main.py
```

Opens a web UI at `http://localhost:8000`.

## Config format

| Key | Example | Description |
|-----|---------|-------------|
| `FILE_NAME` | `My_Song` | Output filename |
| `TEMPO` | `120` | Beats per minute |
| `MEASURE` | `4/4` | Time signature |
| `CAPO` | `0` | Capo fret |
| `INSTRUMENT` | `24` | General MIDI instrument |
| `SF` | `path/to/soundfont.sf2` | SoundFont for audio rendering |
| `CUSTOM_CHORDS` | `X.3.2.0.1.0` | Define chord shapes, reference as `U1`, `U2`... |
| `STRUM_PATTERN` | `1\|D-D-U-DU` | Strum sequence, reference as `S1`, `S2`... |
| `PICK_PATTERN` | `1\|e0.e0.B0.-.G5` | Pluck sequence, reference as `P1`, `P2`... |
| `CHORD_PATTERN` | `C>>G>>Am>>F` | Chord progression, reference as `C1`, `C2`... |
| `SONG` | `(S1 x C1) * 4` | Song expression using `+` (seq), `*` (repeat), `x` (cross) |

### Song DSL operators

- `+` — sequence: `P1 + P2` plays P1 then P2
- `*` — repeat: `(S1 x C1) * 4` repeats 4 times
- `x` — cross product: `S1 x C1` applies strum pattern S1 to chord progression C1
- `()` — grouping

### Functions per frame

- `S` — rest (silence)
- `P` — pluck (single string)
- `D` — down strum
- `U` — up strum
- `H` — hit (percussive slap)

## Dependencies

- Python 3.10+
- [FluidSynth](https://www.fluidsynth.org/) (for MIDI → WAV)
- [FFmpeg](https://ffmpeg.org/) (for audio → video mux)
- A SoundFont (e.g. FluidR3, VintageDreamsWaves)

System binaries (`fluidsynth`, `ffmpeg`) are preferred over bundled ones.
