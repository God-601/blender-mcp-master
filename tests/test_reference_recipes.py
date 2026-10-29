"""Execute every ```python recipe in the recipe guides against a real Blender (bpy).

Each block is standalone: it is run on a fresh empty scene with one active cube
(UVs included). Passing proves the code runs on the bpy version under test and produced
the expected datablock; it does NOT prove the visual result is good.
Skipped when bpy is missing, unless REQUIRE_BPY=1 (CI sets it).
"""
import contextlib
import io
import os
import re
import unittest
import warnings
from pathlib import Path

try:
    import bpy
except ImportError:  # pragma: no cover - depends on environment
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

ROOT = Path(__file__).resolve().parents[1]
RECIPE_FILES = ["handpaint-recipes.md", "shading-recipes.md"]
FENCE = re.compile(r"^```python[ \t]*\n(.*?)^```", re.M | re.S)


def load_recipes():
    recipes = []
    for name in RECIPE_FILES:
        text = (ROOT / "references" / name).read_text(encoding="utf-8")
        for index, match in enumerate(FENCE.finditer(text)):
            recipes.append((f"{name}#{index + 1}", match.group(1)))
    return recipes


def fresh_scene_with_cube():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=2.0)
    return bpy.context.active_object


# Extra assertions keyed by a distinctive string inside the recipe source.
def check_curvature(obj):
    assert obj.data.color_attributes.get("Curvature") is not None


def check_stamps(obj):
    img = bpy.data.images["T_Paint_Test"]
    pixels = list(img.pixels)
    assert len(set(round(p, 3) for p in pixels[0::4])) > 1, "stamps changed nothing"


def check_ao(obj):
    img = bpy.data.images["T_AO"]
    reds = list(img.pixels)[0::4]
    assert max(reds) - min(reds) > 0.0 or max(reds) > 0.0, "bake produced a blank image"


def check_unwrap(obj):
    assert obj.mode == 'OBJECT'
    assert any(e.use_seam for e in obj.data.edges), "no seams were marked on a cube"


def check_sharp(obj):
    assert any(p.use_smooth for p in obj.data.polygons)


def check_bevel_wn(obj):
    types = [m.type for m in obj.modifiers]
    assert types.index("BEVEL") < types.index("WEIGHTED_NORMAL")


def check_toon(obj):
    assert "MAT_Toon" in bpy.data.materials


def check_outline(obj):
    assert obj.modifiers["Outline"].use_flip_normals
    assert bpy.data.materials["MAT_Outline"].use_backface_culling


CHECKS = [
    ('color_attributes.new("Curvature"', check_curvature),
    ("def paint_stamps", check_stamps),
    ("bpy.ops.object.bake(type='AO')", check_ao),
    ("bpy.ops.uv.unwrap", check_unwrap),
    ("auto_smooth_angle", check_sharp),
    ("WEIGHTED_NORMAL", check_bevel_wn),
    ("MAT_Toon", check_toon),
    ("MAT_Outline", check_outline),
]


@unittest.skipIf(bpy is None, "bpy is not installed; install the wheel matching your Python to run these")
class ReferenceRecipeTests(unittest.TestCase):
    def test_recipe_files_contain_code(self):
        found = {label.split("#")[0] for label, _ in load_recipes()}
        self.assertEqual(found, set(RECIPE_FILES))

    def test_every_recipe_runs_and_produces_its_result(self):
        recipes = load_recipes()
        self.assertGreaterEqual(len(recipes), 7)
        matched = set()
        for label, source in recipes:
            with self.subTest(recipe=label):
                obj = fresh_scene_with_cube()
                out = io.StringIO()
                # Deprecated Blender API in a recipe is a future break: fail on it.
                with contextlib.redirect_stdout(out), warnings.catch_warnings():
                    warnings.simplefilter("error", DeprecationWarning)
                    exec(compile(source, label, "exec"), {"__name__": "__recipe__"})
                for marker, check in CHECKS:
                    if marker in source:
                        check(bpy.data.objects[obj.name] if obj.name in bpy.data.objects else obj)
                        matched.add(marker)
        # Every extra check must have found its recipe, so renaming a recipe cannot silently drop a check.
        self.assertEqual(matched, {marker for marker, _ in CHECKS})


if __name__ == "__main__":
    unittest.main()
