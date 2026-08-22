# Published geometry data used by `models/generate_stl.py`

Every other model in `models/generate_stl.py` is authored from first principles.
The files in this directory are the exception: they hold numeric geometry taken
from a published dataset, so they are kept separate and their provenance is
recorded here.

## `liu2019_cuboctahedron_nodes.csv`, `liu2019_cuboctahedron_members.csv`

The Class-1 tensegrity tessellation block on a cuboctahedron design domain from:

> K. Liu, T. Zegard, P. P. Pratapa, G. H. Paulino, "Unraveling tensegrity
> tessellations for metamaterials with tunable stiffness and bandgaps",
> *Journal of the Mechanics and Physics of Solids* **131**:147-166 (2019).
> DOI: [10.1016/j.jmps.2019.05.006](https://doi.org/10.1016/j.jmps.2019.05.006)

Source of the numbers: the article's supplementary dataset
`1-s2.0-S0022509619300432-mmc2.zip`, whose single member is
`Cuboctahedron tensegrity tessellation block data_V3.xls`. Retrieved from the
green open-access copy in CaltechAUTHORS, record
[`afqa1-33315`](https://authors.library.caltech.edu/records/afqa1-33315). The
spreadsheet was transcribed to CSV without modification; no rounding, rescaling,
or reordering was applied.

The accepted manuscript itself is reachable through the same record, and through
the Internet Archive's capture of the Paulino group's old site
(`paulino.princeton.edu/journal_papers/2019/JMPS_19_UnravelingTensegrityTessellationsFor.pdf`,
captured 2024-11-25). The group's site has since moved to
`paulino.scholar.princeton.edu` and the old paths now 404.

### What the files contain

`liu2019_cuboctahedron_nodes.csv` has 40 nodes in the paper's own units, where
the cuboctahedron design domain has its vertices at the permutations of
(+/-1, +/-1, 0). `liu2019_cuboctahedron_members.csv` has 109 members: 13 struts
and 96 cables, each with the self-balanced prestress force from the paper
(struts carry -1, so the forces are normalised to unit strut compression).

The primitive vectors of the tessellation are the columns of `2*I`, that is
(2,0,0), (0,2,0) and (0,0,2), so the unit cell in these units is a 2 x 2 x 2 cube.
They are not stored in a file because three axis-aligned vectors are easier to
read here than in a CSV.

### Checks run against the data

Reproduced by `models/verify_liu2019_cuboctahedron.py`:

| Property | Paper (Table A1) | Measured |
| --- | --- | --- |
| Nodes N_V | 40 | 40 |
| Members N_B | 109 | 109 |
| Struts N_S | 13 | 13 |
| Class | 1 | 1 (max 1 strut per periodic node group) |
| Self-balanced prestress | yes | max nodal residual 8.9e-14 |

Two numbers matter for fabrication and are not in the paper, since it is a
continuum-mechanics study rather than a print: in the paper's units the closest
approach between two strut centrelines is 0.0516, and between a strut centreline
and a non-incident cable centreline it is 0.0392. Both are small relative to the
2-unit cell, which is why `generate_stl.py` prints this block at a larger scale
and with thinner members than the other models. See the "Cuboctahedron
tessellation block" section of [`../README.md`](../README.md).

### Licensing

The CSVs are numeric measurements of a published structure, recorded here for
verification and reproducibility with full attribution. The original
spreadsheet, the article text, and its figures are Elsevier's and are not
redistributed here; use the DOI or the CaltechAUTHORS record above to obtain
them.
