from pathlib import Path
import zipfile
import requests

SYNTHEA_URL = (
    "https://synthetichealth.github.io/"
    "synthea-sample-data/downloads/latest/"
    "synthea_sample_data_csv_latest.zip"
)

PROJECT_ROOT = Path.cwd()
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ZIP_PATH = RAW_DIR / "synthea_sample_data_csv_latest.zip"
EXTRACT_DIR = RAW_DIR / "synthea"


def download_file(url: str, destination: Path) -> None:
    if destination.exists():
        print(f"File already exists: {destination}")
        return

    print(f"Downloading Synthea data from: {url}")

    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    with destination.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    print(f"Downloaded: {destination}")


def extract_zip(zip_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting data to: {output_dir}")

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(output_dir)

    print("Extraction complete.")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    download_file(SYNTHEA_URL, ZIP_PATH)
    extract_zip(ZIP_PATH, EXTRACT_DIR)

    print("\nSynthea data preparation complete.")
    print(f"Raw data location: {EXTRACT_DIR}")


if __name__ == "__main__":
    main()