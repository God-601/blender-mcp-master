# CAD and Dimension-Driven Technical Modeling

Use this guide for precise mechanical parts, dimensioned product concepts, technical diagrams, assemblies, fixtures, and 3D-printable geometry. Blender is a general 3D tool, not a substitute for a parametric CAD system where feature history, constraints, tolerances, or manufacturing drawings are mandatory.

## 1. Define the engineering intent

Record before modeling:
- Units and required dimensions, including reference datums and coordinate axes.
- Required fits, clearances, wall thickness, holes, threads, chamfers, fillets, and symmetry.
- Whether the deliverable is a visual model, a mesh for printing, a neutral CAD exchange file, or a drawing.
- Tolerance values and how they will be verified; never invent them if the part is intended to mate with real hardware.
- Target application and required file format. Confirm whether a suitable exporter or CAD add-on is installed.

If the input contains only an image and no measurements, state which dimensions are estimates and ask only for measurements that materially affect fit or function.

## 2. Build from datums and parameters

- Create a named parameter list for major dimensions rather than scattering unexplained numeric constants through a script.
- Use a consistent origin and axes based on the functional datum: mounting face, shaft axis, mating plane, or assembly origin.
- Model a stable primary envelope first, then add holes, slots, recesses, bosses, ribs, and fillets.
- Prefer constrained or parameterized construction where the installed tools support it; otherwise keep procedural code organized so dimensions can be changed centrally.
- Keep moving components separate and place pivots at hinges or rotational axes.
- Confirm that dimensions measured from the resulting geometry match the inputs after modifiers and transforms.

## 3. Boolean and feature robustness

- Use simple, well-aligned cutters with enough resolution for the intended curve.
- Inspect Boolean outputs for sliver faces, coplanar surfaces, missing faces, and shading artifacts.
- Avoid tiny features that are below the mesh/export/printing tolerance or cannot be represented reliably at the target scale.
- Apply bevels and fillets only after major intersections are stable; ensure their width does not exceed the available local geometry.
- Keep an untouched construction/source version before destructive modifier application.
- For repeated holes or patterns, use arrays or parameter-driven placement rather than manually duplicating unrelated coordinates.

## 4. Assemblies and interface validation

- Give each part a meaningful name and consistent local axes.
- Use explicit mating planes, centerlines, hole centers, and offset parameters to assemble components.
- Check interference and clearances at the intended transforms. A visual inspection alone cannot prove a manufactured fit.
- Confirm that screw/shaft/slot dimensions, wall thickness, and part boundaries match the stated requirements.
- Separate cosmetic details from functional geometry when they have different tolerances or need simplification for the target.

## 5. 3D printing and watertight mesh output

For a mesh intended for 3D printing, validate the slicer/manufacturing workflow rather than relying on viewport appearance alone:
- Confirm real-world dimensions, units, orientation, and scale after export.
- Check manifoldness and accidental holes, internal shells, self-intersections, flipped normals, and disconnected islands where relevant.
- Confirm minimum wall thickness, bridge/overhang limits, nozzle/layer constraints, and fit clearance for the selected printer/material. These are printer- and material-specific.
- Ensure the final export contains the intended solid(s) only.
- Open the exported file in the target slicer when possible; state when this was not done.

Open surfaces are not automatically defects for visual assets, but are usually unacceptable for a watertight-solid requirement unless the workflow intentionally supports them.

## 6. Formats and limitations

- STL is a triangle mesh and does not preserve a full parametric feature history or material definitions.
- OBJ is a mesh interchange format; material support varies by exporter/importer.
- glTF/GLB is useful for realtime visual assets, not a general parametric CAD interchange format.
- STEP/IGES support depends on the installed exporter or external CAD tooling. Do not claim to have produced a true solid CAD model merely because a mesh was exported.
- If only Blender mesh tools are available, report that the deliverable is a dimension-driven mesh and identify which CAD-specific properties are not represented.

## 7. Final validation report

Report the dimensions actually measured, unit convention, format, required tolerances, checks performed, known deviations, and any unverified manufacturing or mating constraints. Never label a part “manufacturing-ready” unless the specified engineering checks have been performed.
