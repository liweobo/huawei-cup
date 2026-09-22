# Data Ledger

| Entity or field | Source | Role | Population | Missingness | Unit or semantics |
| --- | --- | --- | --- | --- | --- |
| SMILES | all three modeling workbooks | exact source entity key | 1,974 train; 50 prediction | none | source-provided structure string; joins use value, never row number |
| 729 descriptors | Molecular_Descriptor.xlsx | predictors | train + prediction | none; all finite | supplied 2D descriptor dictionary covers all columns case-insensitively |
| IC50_nM | ERα_activity.xlsx | source activity target | 1,974 train | none | nM; smaller is stronger activity |
| pIC50 | ERα_activity.xlsx | modeled activity target | 1,974 train | none | supplied continuous transform; larger is stronger activity |
| Caco-2 | ADMET.xlsx | binary endpoint | 1,974 train | none | 1 = better intestinal permeability |
| CYP3A4 | ADMET.xlsx | binary endpoint | 1,974 train | none | 1 = metabolizable, 0 = not metabolizable; desirable direction not stated |
| hERG | ADMET.xlsx | binary endpoint | 1,974 train | none | 1 = cardiotoxic; favorable state is 0 |
| HOB | ADMET.xlsx | binary endpoint | 1,974 train | none | 1 = better oral bioavailability |
| MN | ADMET.xlsx | binary endpoint | 1,974 train | none | 1 = genotoxic; favorable state is 0 |

Every modeling workbook has visible `training` and `test` sheets, header row 1, no hidden sheet, and no formula cells. The blank activity and ADMET test cells are required prediction slots: 100 activity blanks and 250 ADMET blanks. Descriptor train/test cells have no blanks. The descriptor dictionary has visible `Summary` (54×5) and `Detailed` (864×4) sheets; its internal blank metadata cells are descriptive, not modeling missingness.
