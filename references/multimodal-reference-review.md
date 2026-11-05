# Multimodal reference-matching loop (agent-run; evidence-first)

This guide is used **only** when a connected AI agent actually has access to
user reference images AND actual Blender screenshots (e.g. a supported `look`
tool). It is an instruction protocol, not an image classifier. Do not claim
that a reference has been viewed if no image-capable tool or visible reference
is available.

## Procedure

1. **Input:** use user-supplied images and their intended use. Identify the
   object category, reference view, visible front/back, projection and likely
   camera distortion. If perspective makes scale comparisons unreliable, say
   so. Do not fabricate unseen back/side details.
2. **Plan:** write 3–7 observable landmark constraints, e.g. chair back height,
   seat-to-leg placement, sword guard extent, tree crown breaks, doorway width.
   Tag each as supplied, visible, inferred or uncertain.
3. **Capture:** use the connected Blender-control MCP's actual screenshot tool;
   match camera and object framing as well as possible. Capture front, side
   and three-quarter views plus a seam/detail view when needed.
4. **Review:** for every landmark compare reference to the **captured model**,
   naming the object and exact mismatched feature. Separate camera/perspective
   error from modeling error. High priority: silhouette and proportions;
   next: joints/topology/shading; then material and small decorative detail.
5. **Measure:** optionally use `scripts/reference_silhouette_compare.py` for
   transparent, identically framed RGBA PNG masks. Its IoU/bounding boxes
   are *not* image recognition or proof of aesthetic fidelity. For ordinary
   photos, compare visible landmarks directly; do not force them into masks.
6. **Correct:** use smallest owned/reversible change; record source and
   target before/after evidence. Recapture **same** viewpoint and repeat
   comparison. Stop after repeated ineffective correction; ask for the
   missing reference or report unresolved issue.
7. **Report:** `PASS` for individual inspected and evidenced landmarks
   only when the actual comparison supports it. If any necessary view or
   reference was missing, keep corresponding artistic quality NOT VERIFIED.

## Minimal defect record

```json
{
  "source_view": "front",
  "source_reference": "user image id or trusted file",
  "capture": "actual Blender screenshot path/id",
  "object": "Chair_Back",
  "landmark": "backrest height versus seat width",
  "observation": "proportion mismatched on front view",
  "priority": "major",
  "status": "ISSUE",
  "correction": "adjust duplicated owned backrest",
  "recapture": "actual second screenshot path/id",
  "reviewer": "actual reviewer or image-capable agent"
}
```

Review receipts, exact image hashes and visual scorecards must remain separate
from file existence and geometry metric checks. Do not claim that a generic
script can automatically verify style, composition, proportions in perspective
or photographic reference matching without image perception.
