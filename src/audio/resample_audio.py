"""
resample_audio.py
-----------------
Rééchantillonnage et normalisation des fichiers audio Mooré
pour la préparation ASR (Whisper / wav2vec2).

Cible : 16 kHz, mono, WAV PCM 16-bit

Usage:
    python src/audio/resample_audio.py --input data/audio/raw --output data/audio/processed
"""
import sys
import pathlib
import argparse

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR    = pathlib.Path(__file__).parent.parent.parent
DEFAULT_IN  = BASE_DIR / "data" / "raw" / "audio" / "moore"
DEFAULT_OUT = BASE_DIR / "data" / "processed" / "audio" / "moore"

TARGET_SR   = 16_000   # Hz
TARGET_BITS = 16       # bits
CHANNELS    = 1        # mono


def check_deps():
    """Vérifie que les librairies audio sont disponibles."""
    missing = []
    try:
        import librosa
    except ImportError:
        missing.append("librosa")
    try:
        import soundfile
    except ImportError:
        missing.append("soundfile")

    if missing:
        print(f"⚠ Librairies manquantes : {', '.join(missing)}")
        print(f"  Installe-les avec : pip install {' '.join(missing)}")
        return False
    return True


def resample_file(input_path: pathlib.Path, output_path: pathlib.Path) -> dict:
    """Rééchantillonne un fichier audio vers 16kHz mono WAV."""
    import librosa
    import soundfile as sf

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Charger avec resampling automatique
    audio, sr = librosa.load(str(input_path), sr=TARGET_SR, mono=True)

    # Normaliser l'amplitude (-1 à +1)
    if audio.max() > 0:
        audio = audio / audio.max()

    # Sauvegarder en WAV PCM 16-bit
    sf.write(str(output_path), audio, TARGET_SR, subtype='PCM_16')

    duration = len(audio) / TARGET_SR
    return {
        "file":     output_path.name,
        "duration": round(duration, 2),
        "sr":       TARGET_SR,
        "status":   "ok"
    }


def main(input_dir=None, output_dir=None):
    if not check_deps():
        return

    inp = pathlib.Path(input_dir) if input_dir else DEFAULT_IN
    out = pathlib.Path(output_dir) if output_dir else DEFAULT_OUT

    print("=" * 60)
    print("RÉÉCHANTILLONNAGE AUDIO → 16kHz mono WAV")
    print(f"  Source  : {inp}")
    print(f"  Sortie  : {out}")
    print("=" * 60)

    audio_exts = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.opus'}
    files = [f for f in inp.rglob('*') if f.suffix.lower() in audio_exts]

    if not files:
        print(f"\n⚠ Aucun fichier audio trouvé dans {inp}")
        print("  Place tes fichiers audio dans data/audio/raw/")
        return

    print(f"\n  {len(files)} fichier(s) audio trouvé(s)\n")

    results = []
    errors  = 0
    total_duration = 0

    import soundfile as sf

    for i, f in enumerate(files, 1):
        # Conserver la structure de sous-dossiers
        rel = f.relative_to(inp)
        out_path = out / rel.with_suffix('.wav')

        if out_path.exists() and out_path.stat().st_size > 0:
            try:
                snd_info = sf.info(str(out_path))
                dur = snd_info.duration
                total_duration += dur
                results.append({
                    "file":     out_path.name,
                    "duration": round(dur, 2),
                    "sr":       TARGET_SR,
                    "status":   "ok"
                })
                # Periodic progress output to avoid flooding logs
                if i % 100 == 0 or i == len(files):
                    print(f"  [{i:>4}/{len(files)}] (Cache) ✓ {rel}  ({dur:.1f}s)")
                continue
            except Exception:
                pass

        try:
            info = resample_file(f, out_path)
            total_duration += info['duration']
            results.append(info)
            print(f"  [{i:>4}/{len(files)}] ✓ {rel}  ({info['duration']:.1f}s)")
        except Exception as e:
            errors += 1
            print(f"  [{i:>4}/{len(files)}] ✗ {rel}  — {e}")

    print(f"\n{'=' * 60}")
    print(f"  Traités    : {len(results):,} / {len(files):,}")
    print(f"  Erreurs    : {errors}")
    print(f"  Durée tot. : {total_duration/3600:.2f} heures")
    print(f"  Sortie     : {out}")
    print(f"\n✅ Rééchantillonnage terminé !")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',  default=None, help="Dossier audio source")
    parser.add_argument('--output', default=None, help="Dossier audio traité")
    args = parser.parse_args()
    main(args.input, args.output)
