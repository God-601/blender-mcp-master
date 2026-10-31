# Modular and parametric modeling

## Purpose

Build repeated or dimension-driven structures from reusable components instead of treating each
piece as unrelated geometry.

## Current executable capability

scripts/modular_builder.py currently supports:
- staircase: creates individually named step blocks from width, depth, total rise, and step count
- arch: creates an extruded masonry arch profile from outer radius, wall thickness, leg height, depth, and segment count

The builder creates objects in a dedicated owned collection. It rejects unrelated collection/object name
collisions. A staircase rolls back only the steps it created if a later step fails.

## Design rules

- Establish one coordinate convention and grid unit for the assembly.
- Define module dimensions before building repeated parts.
- Use stable names and explicit attachment relationships.
- Prefer linked instances when repeated meshes are identical and shared edits are intended.
- Use separate objects for parts that move independently.
- Keep pivot/origin placement meaningful for doors, hinges, wheels, and moving modules.
- Avoid hidden overlaps and gaps between adjacent modules.
- Validate the assembled silhouette, not just each part independently.

## Planned capabilities

- wall panels with door/window openings
- roof modules and modular trim
- snap points and connector sockets
- dimension-driven furniture
- radial and linear arrays
- reusable assembly templates
- deterministic regeneration from parameters

## Limitations

The current staircase and arch are blockout construction tools, not complete architectural asset kits.
The arch builder uses a simple extruded profile and does not create UVs, materials, trim, or structural
details. Inspect the result and refine it for the intended style and destination.
