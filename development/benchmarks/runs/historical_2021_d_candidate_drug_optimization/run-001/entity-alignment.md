# Entity Alignment

Entity key: exact source `SMILES` string.

- Training: 1,974 rows and 1,974 unique keys in activity, ADMET, and descriptor workbooks.
- Prediction: 50 rows and 50 unique keys in all three workbooks.
- Sets match across workbooks: **true** for both populations.
- Row order also matches, but joins and audits use SMILES values.
- Duplicate IDs: zero in every modeling sheet.
- Training/prediction overlap: 0.
- Alignment status: **PASS**.

No inner join drops a compound. Each target therefore uses all 1,974 legal training rows; no missing label is filled or imputed.
