"""Script to auto-download and verify public benchmark EEG datasets.

Downloads:
- PhysioNet eegmmidb motor imagery & rest recordings (Subjects S003-S005)
- PhysioNet EEG Motor Movement / Mental Arithmetic dataset files (eegmat)
"""

import os
import sys
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_DIR = os.path.join(BASE_DIR, "data", "public_benchmarks")


def download_physionet_eegmmidb(subjects=(3, 4, 5), runs=(1, 2)):
    """Downloads select PhysioNet eegmmidb runs directly via HTTPS."""
    target_dir = os.path.join(DATA_DIR, "eog_emg_artifacts", "physionet.org", "files", "eegmmidb", "1.0.0")
    base_url = "https://physionet.org/files/eegmmidb/1.0.0"

    for sub_id in subjects:
        sub_str = f"S{sub_id:03d}"
        sub_path = os.path.join(target_dir, sub_str)
        os.makedirs(sub_path, exist_ok=True)

        for run in runs:
            filename = f"{sub_str}R{run:02d}.edf"
            file_url = f"{base_url}/{sub_str}/{filename}"
            dest_file = os.path.join(sub_path, filename)

            if os.path.exists(dest_file) and os.path.getsize(dest_file) > 1000:
                logger.info(f"Already exists: {filename}")
                continue

            logger.info(f"Downloading {file_url} -> {dest_file}...")
            try:
                urllib.request.urlretrieve(file_url, dest_file)
                logger.info(f"✓ Saved {filename} ({os.path.getsize(dest_file)} bytes)")
            except Exception as e:
                logger.warning(f"Could not download {file_url}: {e}")


def download_eegmat_sample():
    """Downloads sample recording from PhysioNet EEG Mental Arithmetic database (eegmat)."""
    target_dir = os.path.join(DATA_DIR, "mental_arithmetic_eegmat")
    os.makedirs(target_dir, exist_ok=True)
    base_url = "https://physionet.org/files/eegmat/1.0.0"
    files = ["Subject00_1.edf", "Subject00_2.edf"]

    for fname in files:
        dest_file = os.path.join(target_dir, fname)
        if os.path.exists(dest_file) and os.path.getsize(dest_file) > 1000:
            logger.info(f"Already exists: {fname}")
            continue

        url = f"{base_url}/{fname}"
        logger.info(f"Downloading {url} -> {dest_file}...")
        try:
            urllib.request.urlretrieve(url, dest_file)
            logger.info(f"✓ Saved {fname} ({os.path.getsize(dest_file)} bytes)")
        except Exception as e:
            logger.warning(f"Could not download {url}: {e}")


if __name__ == "__main__":
    logger.info("Starting automated benchmark downloads...")
    download_physionet_eegmmidb(subjects=[3, 4], runs=[1, 2])
    download_eegmat_sample()
    logger.info("Dataset download task complete.")
