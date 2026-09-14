# 2024年中国研究生数学建模竞赛 C 题

## Title

数据驱动下磁性元件的磁芯损耗建模

## Extraction status

Source: `../raw/数据驱动下磁性元件的磁芯损耗建模.docx` (ART-001).
This is a faithful text extraction of the supplied problem statement. Formula
objects, some symbols, and embedded figures are marked
`[EXTRACTION_UNCERTAIN]` when paragraph text alone cannot preserve them.
No modeling recommendation is added here.

## Background and definitions

The problem concerns magnetic components used in power conversion. Core loss is
power loss in magnetic materials under high-frequency alternating magnetic
flux. The statement distinguishes loss-separation models and empirical models,
including the Steinmetz equation (SE). It defines the measured quantities in
the experimental setup: temperature, frequency, excitation waveform, magnetic
field/flux quantities, and core-loss density.

The supplied statement says that core loss depends nonlinearly and jointly on
temperature, material, frequency, excitation waveform, and magnetic-flux
density. The exact displayed equations and symbols are retained only as
`[EXTRACTION_UNCERTAIN]` here and must be read from the raw DOCX before any
mathematical claim.

## Data description in the statement

The statement describes Attachment 1 as a training set with four tables for
four anonymized core materials. It describes temperature values 25, 50, 70,
and 90 °C; frequency range 50,000–500,000 Hz; core-loss density in W/m³;
excitation waveforms sinusoidal, triangular, and trapezoidal; and sampled
magnetic flux-density values over one period.

Attachment 2 is a test set for waveform classification and contains sample
identifiers, temperature, frequency, material and flux-density samples.
Attachment 3 is a test set for core-loss prediction and contains sample
identifiers, temperature, frequency, material and flux-density samples without
the training target. Attachment 4 is the supplied answer spreadsheet.

## Explicit questions

### Question 1 — Excitation waveform classification

Analyze magnetic-flux-density distribution and waveform-shape features, build a
classification model for sinusoidal/triangular/trapezoidal waveforms, classify
Attachment 2, fill the classification result in Attachment 4 column 2, report
the counts of the three waveforms, and show specified sample IDs in the paper.

### Question 2 — Steinmetz-equation correction

For one material and sinusoidal waveform, analyze temperature variation and
construct a temperature-aware correction to the Steinmetz equation. Compare its
prediction error with the original Steinmetz equation using the specified
training subset.

### Question 3 — Core-loss factor analysis

Analyze the independent and pairwise synergistic effects of temperature,
excitation waveform, and core material on core loss; assess their influence and
identify conditions under which loss may be minimized.

### Question 4 — Data-driven core-loss prediction

Build a data-driven core-loss prediction model using Attachment 1, analyze
prediction accuracy and generalization, predict Attachment 3, fill Attachment 4
column 3 to one decimal place, and report specified sample IDs in the paper.

### Question 5 — Optimization conditions for magnetic components

Use the Question 4 prediction model as an objective while considering
transmission magnetic energy, represented in the statement by the product of
frequency and magnetic-flux-density peak. Identify conditions over temperature,
frequency, waveform, flux-density peak, and material that minimize core loss and
maximize the transmission-energy proxy.

## References and notes

The statement includes references on magnetic loss, Steinmetz models, and
non-sinusoidal excitation. It also includes a note about responsible use and
disclosure of AI-assisted work. Those are source facts, not instructions to
the benchmark runner.
