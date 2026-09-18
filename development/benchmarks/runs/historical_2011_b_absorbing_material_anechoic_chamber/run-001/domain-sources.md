# External domain knowledge

No problem-specific search was used. Requested source directory and exact DOC were the only historical-problem URLs fetched; the forbidden solution tree was never accessed.

| Source | Claim | Why needed | Confidence |
|---|---|---|---|
| OpenStax, University Physics Vol.3 §1.2, https://openstax.org/books/university-physics-volume-3/pages/1-2-the-law-of-reflection | Incident and reflected angles are equal, measured from the normal | Close facet reflection and derive image geometry | HIGH; fetched page explicitly states the law; excerpts/hash in `source-provenance/domain-retrieval.json` |
| NumPy reference, https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.leggauss.html | Gauss-Legendre n-point rule integrates polynomials through degree 2n−1 on [−1,1] | Finite-patch integration and refinement | HIGH; fetched documentation checked; use orders below 100, consistent with documented caveat |

The image/unfolding sum, attenuation products, and tail bounds are derived in `mathematical-model.md`; they are not falsely attributed to the original statement or an external worked answer. Reflection coefficient, cosine emitter, inverse-square/cosine irradiance, power definitions and all chamber constants come from **PROBLEM_GIVEN_FACT**.

Tooling: local Aspose.Words 26.9 evaluation parser and olefile 0.47 installed under ignored run-local `.tmp/` from PyPI (a mirror retry also completed). Evaluation watermark kept in extraction renders; no temporary license requested, no source file uploaded. Python NumPy/SciPy/Matplotlib are calculation tools, not external parameter sources. Original bibliography transcribed only; no referenced book or 2011B solution consulted.
