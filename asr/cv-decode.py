import argparse
import os
import pandas as pd
import requests
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to cv-valid-dev.csv")
    parser.add_argument("--audio_dir", required=True, help="Directory containing mp3 files for cv-valid-dev")
    parser.add_argument("--api", default="http://localhost:8001/asr", help="ASR API endpoint")
    parser.add_argument("--out_csv", default=None, help="Path to save updated CSV (default: overwrite input CSV)")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    gen_texts = []
    durations = []

    # iterate over each row in the csv and call the ASR API. 
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Transcribing"):
        rel = row.get("path") or row.get("filename") or row.get("file")
        if not rel:
            gen_texts.append("")
            durations.append(0.0)
            continue
        audio_path = os.path.join(args.audio_dir, rel)
        if not os.path.exists(audio_path):
            gen_texts.append("")
            durations.append(0.0)
            continue

        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
            try:
                resp = requests.post(args.api, files=files, timeout=60000)
                resp.raise_for_status()
                data = resp.json()
                gen_texts.append(data.get("transcription", ""))
                durations.append(data.get("duration", 0.0))
            except Exception as e:
                gen_texts.append("")
                durations.append(0.0)
                print(f"Error for {audio_path}: {e}")

    df["generated_text"] = gen_texts
    df["duration"] = durations
    out = args.out_csv or args.csv
    df.to_csv(out, index=False)
    print(f"Saved updated CSV to {out}")

if __name__ == "__main__":
    main()
