"""Pack and reopen a disposable Blender checkpoint with auto-execution off."""
import sys

import bpy


def pack_checkpoint(source, destination):
    if not bpy.app.background:
        raise RuntimeError('Checkpoint packing requires a disposable background Blender')
    bpy.ops.wm.open_mainfile(filepath=source, use_scripts=False, load_ui=False)
    if bpy.ops.file.pack_all() != {'FINISHED'}:
        raise ValueError('Blender could not pack the checkpoint dependencies')
    remaining = bpy.utils.blend_paths(absolute=True, packed=False)
    if remaining:
        raise ValueError('Unsupported or unpacked checkpoint dependencies: ' + ', '.join(remaining))
    if bpy.ops.wm.save_as_mainfile(filepath=destination) != {'FINISHED'}:
        raise ValueError('Blender could not save the packed checkpoint')
    bpy.ops.wm.open_mainfile(filepath=destination, use_scripts=False, load_ui=False)
    if bpy.utils.blend_paths(absolute=True, packed=False):
        raise ValueError('Packed checkpoint still has external dependencies after reopening')
    print('PACKED_CHECKPOINT_VERIFIED', flush=True)


if __name__ == '__main__':
    pack_checkpoint(*sys.argv[sys.argv.index('--') + 1:])
