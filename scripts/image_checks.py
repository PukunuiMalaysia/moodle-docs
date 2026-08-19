#!/usr/bin/env python3
"""Verify public documentation image signatures and dimensions."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import struct
import sys


IMAGE_SUFFIXES = frozenset({".gif", ".jpeg", ".jpg", ".png", ".webp"})


@dataclass(frozen=True)
class ImageInfo:
    """Detected raster format and dimensions."""

    format: str
    width: int
    height: int


def _jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Return JPEG dimensions from a start-of-frame segment."""
    offset = 2
    sof_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while offset < len(data):
        while offset < len(data) and data[offset] != 0xFF:
            offset += 1
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0x01, *range(0xD0, 0xD9)}:
            continue
        if marker == 0xDA:
            break
        if offset + 2 > len(data):
            break
        segment_length = struct.unpack(">H", data[offset : offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(data):
            break
        if marker in sof_markers and segment_length >= 7:
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += segment_length
    raise ValueError("JPEG has no readable start-of-frame segment")


def _webp_dimensions(data: bytes) -> tuple[int, int]:
    """Return dimensions for common WebP encodings."""
    if len(data) < 30:
        raise ValueError("WebP header is truncated")
    chunk = data[12:16]
    if chunk == b"VP8X":
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return width, height
    if chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L" and data[20] == 0x2F:
        packed = int.from_bytes(data[21:25], "little")
        return (packed & 0x3FFF) + 1, ((packed >> 14) & 0x3FFF) + 1
    raise ValueError("unsupported WebP encoding")


def inspect_image(path: Path) -> ImageInfo:
    """Detect a supported raster image from its bytes, not its suffix."""
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if len(data) < 24 or data[12:16] != b"IHDR":
            raise ValueError("PNG header is truncated")
        width, height = struct.unpack(">II", data[16:24])
        detected = "png"
    elif data.startswith((b"GIF87a", b"GIF89a")):
        if len(data) < 10:
            raise ValueError("GIF header is truncated")
        width, height = struct.unpack("<HH", data[6:10])
        detected = "gif"
    elif data.startswith(b"\xff\xd8"):
        width, height = _jpeg_dimensions(data)
        detected = "jpeg"
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        width, height = _webp_dimensions(data)
        detected = "webp"
    else:
        raise ValueError("unrecognised image signature")
    if width < 1 or height < 1:
        raise ValueError("image dimensions must be positive")
    return ImageInfo(detected, width, height)


def expected_format(path: Path) -> str | None:
    """Return the format implied by the filename."""
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "jpeg"
    return suffix.removeprefix(".") if suffix in IMAGE_SUFFIXES else None


def validate_image(path: Path) -> tuple[list[str], list[str]]:
    """Return blocking errors and quality warnings for one image."""
    errors: list[str] = []
    warnings: list[str] = []
    expected = expected_format(path)
    if expected is None:
        return ["filename does not use an approved image suffix"], warnings
    try:
        info = inspect_image(path)
    except (OSError, ValueError) as error:
        return [str(error)], warnings
    if info.format != expected:
        errors.append(
            f"file signature is {info.format}, but the filename declares {expected}"
        )
    if info.width < 1280 or info.height < 800:
        warnings.append(
            f"{info.width}x{info.height} is below the 1280x800 promotional target; "
            "confirm that the product surface remains legible at full resolution"
        )
    return errors, warnings


def image_paths(roots: list[Path]) -> list[Path]:
    """Discover approved-suffix images beneath the supplied paths."""
    found: set[Path] = set()
    for root in roots:
        if root.is_file():
            found.add(root)
            continue
        if root.is_dir():
            found.update(
                path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
            )
    return sorted(found)


def main() -> int:
    """Run the image audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    paths = image_paths(args.paths)
    error_count = 0
    warning_count = 0
    for path in paths:
        errors, warnings = validate_image(path)
        for error in errors:
            print(f"ERROR {path}: {error}", file=sys.stderr)
        for warning in warnings:
            print(f"WARNING {path}: {warning}", file=sys.stderr)
        error_count += len(errors)
        warning_count += len(warnings)
    if error_count:
        print(
            f"Image audit failed: {error_count} error(s), {warning_count} warning(s)",
            file=sys.stderr,
        )
        return 1
    print(f"Image audit passed: {len(paths)} image(s), {warning_count} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
