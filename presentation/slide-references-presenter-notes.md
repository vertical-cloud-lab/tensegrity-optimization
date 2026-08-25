# Presenter notes for the slide reference list (internal)

Internal to-dos and provenance notes for
[slide-references.md](slide-references.md), kept out of the public page per
@me-madsen's request (2026-08-24). Resolve these before the reference list is
called complete. Updated 2026-08-25 after auditing the public list against the
active (non-hidden) slides of the stored `idetc-2026.pptx`.

## Open to-dos

- The 48x assembly clip was recorded in the deck's notes as "hexahedron, exact
  URL TODO". The frames match TensoLogic's "12 Dowel Structure" video (same
  studio, kit boxes, and finished structure), so that link is used in the
  public list. Confirm by eye before the talk, and replace the TODO text in
  that slide's speaker notes with the confirmed link so no TODO shows in
  presenter view.
- The tensegrity side table photo still has no identified original. Replace it
  with a photo of one of our own models, or drop it, before the reference list
  is called complete.
- The kit-ball image on the compact-and-deploy slide carries an "AI-generated
  content" watermark (visible bottom-left on screen), and that slide's notes
  still hold the "insert picture of assembled ball" placeholder. Replace it
  with a real photo of the Tensegrity Adventures kit ball; if it stays, it
  needs no external credit but should be labeled AI-generated.
- The anatomy slide's speaker notes say only "Model courtesy of Wikipedia".
  CC BY-SA requires naming the author: use the public list's exact credit
  line, "Cmglee, CC BY-SA 3.0, via Wikimedia Commons".
- The future-applications slide's speaker notes still credit
  Al Sabouni-Zawadzka et al. (2025) for the lattice image, but the lattice
  image now on that slide is our own render
  (`presentation/media/fig-lattice-concept.png`). Update the speaker note, or
  restore the paper's photo if that is preferred.
- The references QR code is now embedded on the closing References slide
  (verified by decoding the stored deck, 2026-08-25). It points to this
  file's sibling on the working branch, so the link dies if the branch is
  deleted after merge. Before the deck freezes: merge PR #84 (or otherwise
  land `presentation/slide-references.md` on main), regenerate with
  `python presentation/build_references_qr.py --branch main`, and swap the QR
  image on the closing slide. The second QR on that slide points to the
  repository root and needs no change.

## Entries removed 2026-08-25 (asset no longer on an active slide)

Per @me-madsen's instruction that the public list reference nothing that is
not in the active deck. Restore the entry if the slide comes back.

- **Al Sabouni-Zawadzka et al. (2025)**, modular tensegrity-like lattice
  photo: now appears only on the hidden variant of the future-applications
  slide. Citation for restoring: A. Al Sabouni-Zawadzka, A. Micheletti,
  M. Kolodziejczak, A. Zawadzki, "Design and fabrication of modular
  tensegrity-like lattices with auxetic properties", *Materials & Design*
  258, 114513 (2025), DOI 10.1016/j.matdes.2025.114513.
- **Pajunen et al. (2019)**, spherically-jointed impact cell (our re-render
  of their Geometry #3): now appears only on a hidden backup variant of the
  "traditional structures" slide. Citation for restoring: K. Pajunen,
  P. Johanns, R. K. Pal, J. J. Rimoli, C. Daraio, "Design and impact response
  of 3D-printable tensegrity-inspired structures", *Materials & Design* 182,
  107966 (2019), DOI 10.1016/j.matdes.2019.107966 (open access).
- The **fold-and-release clip** of the kit ball now sits on a hidden slide in
  the motivation section. The public list keeps the kit identification and
  the YouTube link, reframed as our own material about the physical demo
  model rather than as an in-deck asset.

## Provenance notes (no action needed)

- The seven-model tensegrity gallery on the "traditional structures" slide is
  our own render: `figures/tensegrity_models_extended_preview_shaded.png`
  from PR #22 (commit 52ce670). The configurations it depicts are classic
  published designs (Geiger cable-dome, biotensegrity spine, SUPERball,
  Tibert/Pellegrino mast, Knight et al. patent antenna, bistable
  double-prism, cuboctahedron tessellation); the labeled original,
  `figures/tensegrity_models_extended_preview.png`, names them if anyone asks.
- The Pareto front figures on the active results slides carry a "PROTOTYPE:
  round-2 outcomes are synthetic" annotation. Swap in the real round-2
  figures (the deck notes point at PR #102) before the deck freezes, or keep
  the label and say it aloud.
