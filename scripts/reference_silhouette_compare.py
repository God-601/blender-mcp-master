"""Read-only PNG alpha-mask silhouette comparison with bounded decoding.

Use exported transparent PNG silhouette masks of matching dimensions/framing,
not arbitrary photos. This computes overlap IoU and never certifies artwork.
Supports only non-interlaced 8-bit RGBA PNG (color type 6). No bpy/Pillow needed.
"""
import hashlib
import json
import struct
import zlib
from pathlib import Path

EVIDENCE_ROOT = ""
PAIRS = []  # [{"reference": "chair_ref.png", "render": "chair_front.png", "view": "front"}]
MAX_FILE_BYTES = 12_000_000
MAX_PIXELS = 4_000_000
MAX_PAIRS = 16
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png_alpha_mask(path):
    content = path.read_bytes()
    if len(content) > MAX_FILE_BYTES or len(content) < 45 or content[:8] != PNG_MAGIC:
        raise ValueError("PNG invalid or exceeds file size cap")
    offset = 8
    width = height = None
    idat = []
    seen_end = False
    while offset < len(content):
        if offset + 12 > len(content):
            raise ValueError("Incomplete PNG chunk")
        length = struct.unpack(">I", content[offset:offset+4])[0]
        kind = content[offset+4:offset+8]
        end = offset + 12 + length
        if end > len(content):
            raise ValueError("PNG chunk outside file")
        data = content[offset+8:offset+8+length]
        expected_crc = struct.unpack(">I", content[offset+8+length:end])[0]
        if zlib.crc32(kind + data) & 0xffffffff != expected_crc:
            raise ValueError("PNG chunk checksum mismatch")
        if kind == b"IHDR":
            if width is not None or length != 13:
                raise ValueError("Invalid or duplicate IHDR")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", data)
            if not (0 < width * height <= MAX_PIXELS and width > 0 and height > 0):
                raise ValueError("Invalid PNG dimensions")
            if (depth, color, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("Only non-interlaced 8-bit RGBA PNG is supported")
        elif kind == b"IDAT":
            if width is None:
                raise ValueError("IDAT before IHDR")
            idat.append(data)
        elif kind == b"IEND":
            seen_end = True
            break
        elif kind not in (b"PLTE", b"sRGB", b"gAMA", b"cHRM", b"pHYs", b"tEXt", b"iTXt", b"zTXt", b"tIME", b"eXIf"):
            # Unknown critical chunks cannot be ignored safely.
            if kind[0] & 32 == 0:
                raise ValueError("Unsupported critical PNG chunk")
        offset = end
    if not seen_end or width is None or not idat:
        raise ValueError("Missing PNG data/end")
    row_bytes = 4 * width
    required = height * (row_bytes + 1)
    inflater = zlib.decompressobj()
    raw = bytearray()
    for compressed in idat:
        raw.extend(inflater.decompress(compressed, max(0, required + 1 - len(raw))))
        if len(raw) > required or inflater.unconsumed_tail:
            raise ValueError("PNG decompressed data exceeds cap")
    raw.extend(inflater.flush())
    if len(raw) != required or not inflater.eof:
        raise ValueError("Unexpected PNG pixel stream length")
    mask = bytearray()
    prior = bytearray(row_bytes)
    pos = 0
    alpha_values = set()
    for _ in range(height):
        filter_type = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos+row_bytes])
        pos += row_bytes
        if filter_type not in (0, 1, 2, 3, 4):
            raise ValueError("Unsupported PNG filter")
        for i in range(row_bytes):
            left = line[i-4] if i >= 4 else 0
            up = prior[i]
            upper_left = prior[i-4] if i >= 4 else 0
            if filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                p = left + up - upper_left
                d = (abs(p-left), abs(p-up), abs(p-upper_left))
                predictor = (left, up, upper_left)[d.index(min(d))]
            else:
                predictor = 0
            line[i] = (line[i] + predictor) & 255
        for i in range(3, row_bytes, 4):
            alpha_values.add(line[i])
            mask.append(1 if line[i] >= 128 else 0)
        prior = line
    if not any(x < 128 for x in alpha_values):
        raise ValueError("No transparent background found; supply isolated alpha silhouette masks")
    return (width, height), mask, hashlib.sha256(content).hexdigest()


def _secure_path(root, relative):
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("Explicit relative PNG filename required")
    filename = Path(relative)
    if filename.is_absolute() or ".." in filename.parts or filename.suffix.lower() != ".png":
        raise ValueError("Unsafe or unsupported PNG path")
    path = (root / filename).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("Image missing or outside evidence directory")
    return path


def compare_masks(root, pairs):
    if not isinstance(root, (str, Path)) or not str(root).strip():
        raise ValueError("EVIDENCE_ROOT is required")
    base = Path(root).expanduser().resolve()
    if not base.is_dir():
        raise ValueError("EVIDENCE_ROOT must exist")
    if not isinstance(pairs, list) or not (1 <= len(pairs) <= MAX_PAIRS):
        raise ValueError("Provide 1 to 16 explicit pairs")
    results = []
    for pair in pairs:
        if not isinstance(pair, dict) or pair.get("view") not in (
            "front", "side", "top", "back", "three_quarter"):
            raise ValueError("Missing/invalid pair view")
        ref_path = _secure_path(base, pair.get("reference"))
        render_path = _secure_path(base, pair.get("render"))
        ref_size, ref_mask, ref_sha = _png_alpha_mask(ref_path)
        out_size, out_mask, out_sha = _png_alpha_mask(render_path)
        if ref_size != out_size:
            results.append({"view": pair["view"], "status": "NOT VERIFIED",
                            "reason": "Mismatched pixel dimensions/framing"})
            continue
        intersection = sum(a & b for a, b in zip(ref_mask, out_mask))
        union = sum(a | b for a, b in zip(ref_mask, out_mask))
        results.append({
            "view": pair["view"], "status": "MEASURED_REVIEW_REQUIRED",
            "silhouette_iou": round(intersection / union, 6) if union else None,
            "foreground_reference": sum(ref_mask), "foreground_render": sum(out_mask),
            "resolution": list(ref_size), "reference_sha256": ref_sha,
            "render_sha256": out_sha, "artistic_quality": "NOT VERIFIED",
        })
    return {
        "results": results, "artistic_quality": "NOT VERIFIED",
        "interpretation": "Alpha silhouette overlap is not proportion, shading, contact, style or artistic certification. Matched framing and legitimate reference provenance must be reviewed independently.",
    }


if __name__ == "__main__":
    print(json.dumps(compare_masks(EVIDENCE_ROOT, PAIRS), indent=2, sort_keys=True))
