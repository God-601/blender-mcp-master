"""Prepare a reviewer-only image packet from corresponding production benchmark trials."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import shutil

VIEWS = ("front", "side", "three_quarter")


def prepare(baseline, candidate, output, criteria):
    from PIL import Image

    arms = {"baseline": baseline, "with_skill": candidate}
    if baseline.samefile(candidate):
        raise ValueError("A pair requires distinct trials")
    for name in ("common_task.txt", "scene_fixture.blend"):
        hashes = set()
        for root in arms.values():
            with (root / name).open("rb") as stream:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                hashes.add(digest.hexdigest())
        if len(hashes) != 1:
            raise ValueError("Mismatched " + name)
    criteria = [item.strip() for item in criteria]
    if not all(criteria) or not criteria:
        raise ValueError("Supply observable criteria from the shared brief")
    labels = list(arms)
    secrets.SystemRandom().shuffle(labels)
    output.mkdir()
    try:
        public = output / "review"
        public.mkdir()
        (public / "criteria.json").write_text(json.dumps(criteria, indent=2), encoding="utf-8")
        dimensions = {}
        key = {}
        for label, arm in zip(("A", "B"), labels):
            root = arms[arm]
            key[label] = {"arm": arm, "trial": root.name}
            for view in VIEWS:
                with Image.open(root / (view + ".png")) as source:
                    if dimensions.setdefault(view, source.size) != source.size:
                        raise ValueError("Image dimensions differ for " + view)
                    clean = source.convert("RGBA")
                    clean.info.clear()
                    clean.save(public / f"{label}-{view}.png")
        (output / "private-key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    except BaseException:
        shutil.rmtree(output)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline", "candidate", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--criterion", action="append", required=True)
    args = parser.parse_args()
    prepare(args.baseline, args.candidate, args.output, args.criterion)
