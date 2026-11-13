"""Pack and reopen a disposable Blender checkpoint with auto-execution off."""
from pathlib import Path
import sys

import bpy


def checkpoint_paths():
    paths = set(bpy.utils.blend_paths(absolute=True, packed=False))
    brushes = bpy.utils.system_resource('DATAFILES', path='assets/brushes')
    if brushes:
        # The factory startup scene can hold an Essentials brush by weak reference.
        # A real linked library at the same path is still a scene dependency.
        stock = Path(brushes) / 'essentials_brushes-gp_draw.blend'
        libraries = {Path(bpy.path.abspath(lib.filepath)).resolve() for lib in bpy.data.libraries}
        if stock.is_file() and stock.resolve() not in libraries:
            paths.discard(str(stock))
    return sorted(paths)


def pack_checkpoint(source, destination):
    if not bpy.app.background:
        raise RuntimeError('Checkpoint packing requires a disposable background Blender')
    bpy.ops.wm.open_mainfile(filepath=source, use_scripts=False, load_ui=False)
    if bpy.ops.file.pack_all() != {'FINISHED'}:
        raise ValueError('Blender could not pack the checkpoint dependencies')
    remaining = checkpoint_paths()
    if remaining:
        raise ValueError('Unsupported or unpacked checkpoint dependencies: ' + ', '.join(remaining))
    if bpy.ops.wm.save_as_mainfile(filepath=destination) != {'FINISHED'}:
        raise ValueError('Blender could not save the packed checkpoint')
    bpy.ops.wm.open_mainfile(filepath=destination, use_scripts=False, load_ui=False)
    if checkpoint_paths():
        raise ValueError('Packed checkpoint still has external dependencies after reopening')
    print('PACKED_CHECKPOINT_VERIFIED', flush=True)


if __name__ == '__main__':
    pack_checkpoint(*sys.argv[sys.argv.index('--') + 1:])
