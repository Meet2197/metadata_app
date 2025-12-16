import os
import uuid
import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from aicsimageio import AICSImage
from aicsimageio.writers import OmeTiffWriter, OmeZarrWriter
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models
from app.eln import create_eln_entry
from app.sharepoint import export_to_sharepoint


# =========================
# Configuration
# =========================

WATCH_PATH = "/microscope_output"
PROCESSED_ROOT = "/processed"

SUPPORTED_EXTENSIONS = (".dv", ".tif", ".ome.tif")


# =========================
# Metadata Parsing
# =========================

def parse_metadata(filepath: str) -> dict:
    """
    Parse OME metadata from a microscopy image file.
    """
    img = AICSImage(filepath)
    ome = img.metadata

    instrument = ome.instrument
    objective = None
    if instrument and instrument.objectives:
        objective = instrument.objectives[0]

    pixels = ome.images[0].pixels

    return {
        "user": os.getenv("USER", "unknown"),
        "acquisition_date": datetime.datetime.utcnow(),
        "microscope": instrument.model if instrument else "unknown",
        "objective": objective.model if objective else "unknown",
        "numerical_aperture": objective.lens_na if objective else None,
        "pixel_size_xy": pixels.physical_size_x,
        "pixel_size_z": pixels.physical_size_z,
        "channels": [c.name for c in pixels.channels],
        "filename": os.path.basename(filepath),
        "raw_path": filepath
    }


# =========================
# Image Conversion
# =========================

def convert_to_ometiff(src: str) -> str:
    """
    Convert raw image to OME-TIFF.
    """
    img = AICSImage(src)

    dst = (
        Path(PROCESSED_ROOT)
        / "ome-tiff"
        / f"{Path(src).stem}.ome.tif"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)

    OmeTiffWriter.save(
        img.get_image_data("TCZYX", S=0),
        dst,
        ome_xml=img.metadata.to_xml()
    )

    return str(dst)


def convert_to_omezarr(src: str) -> str:
    """
    Convert raw image to OME-Zarr.
    """
    img = AICSImage(src)

    dst = (
        Path(PROCESSED_ROOT)
        / "ome-zarr"
        / Path(src).stem
    )
    dst.parent.mkdir(parents=True, exist_ok=True)

    OmeZarrWriter.save(img, dst)

    return str(dst)


# =========================
# Ingestion Pipeline
# =========================

def ingest_file(filepath: str):
    """
    Full ingestion pipeline for one microscopy image.
    """
    db: Session = SessionLocal()

    try:
        # 1. Parse metadata
        metadata = parse_metadata(filepath)

        # 2. Convert formats
        ome_tiff_path = convert_to_ometiff(filepath)
        ome_zarr_path = convert_to_omezarr(filepath)

        # 3. Create ELN entry
        eln_id = create_eln_entry({
            **metadata,
            "ome_tiff_path": ome_tiff_path,
            "ome_zarr_path": ome_zarr_path
        })

        # 4. Store in database
        experiment = models.Experiment(
            id=uuid.uuid4(),
            acquisition_date=metadata["acquisition_date"],
            microscope=metadata["microscope"],
            objective=metadata["objective"],
            numerical_aperture=metadata["numerical_aperture"],
            pixel_size_xy=metadata["pixel_size_xy"],
            pixel_size_z=metadata["pixel_size_z"],
            channels=metadata["channels"],
            raw_path=metadata["raw_path"],
            ome_tiff_path=ome_tiff_path,
            ome_zarr_path=ome_zarr_path,
            eln_id=eln_id
        )

        db.add(experiment)
        db.commit()

        # 5. Export to SharePoint
        export_to_sharepoint({
            **metadata,
            "ome_tiff_path": ome_tiff_path,
            "ome_zarr_path": ome_zarr_path,
            "eln_id": eln_id
        })

        print(f"[INGESTED] {filepath}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to ingest {filepath}: {e}")

    finally:
        db.close()


# =========================
# File Watcher
# =========================

class ImageHandler(FileSystemEventHandler):
    """
    Reacts to new microscopy files appearing in WATCH_PATH.
    """

    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.lower().endswith(SUPPORTED_EXTENSIONS):
            ingest_file(event.src_path)


def start_watcher():
    """
    Start filesystem observer.
    """
    observer = Observer()
    observer.schedule(ImageHandler(), WATCH_PATH, recursive=True)
    observer.start()
    print(f"[WATCHING] {WATCH_PATH}")

    observer.join()
