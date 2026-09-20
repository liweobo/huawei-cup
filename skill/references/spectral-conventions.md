# Spectral Convention And Normalization Contract

Use this contract only when a task actually uses sampled signals, a DFT/FFT/IFFT, a frequency-domain filter or transfer function, frequency-domain convolution, complex baseband, phase, PSD/ASD, frequency-domain amplitude or power, or a time-frequency transform. Ordinary tabular regression, classification, optimization, and time-series work that never enters a frequency domain does not need this contract.

The contract records the mathematical representation around a transform. It does not choose an estimator, implement an FFT, design a filter, or require a particular library. A NumPy, SciPy, MATLAB, or other implementation is acceptable when its mapping and normalization are recorded.

## Minimum declaration

Create an instance from [`../templates/spectral-convention.yaml`](../templates/spectral-convention.yaml) when the activation boundary is crossed. At minimum record:

- signal type (`REAL` or `COMPLEX`) and sampled/discrete domain;
- `sampling_rate`, `sampling_interval`, `sample_count`, and `observation_duration`;
- time and frequency units, including any explicit `omega = 2*pi*f` conversion;
- transform type, length, axis, forward normalization, inverse normalization, and library provenance;
- the physical frequency grid, negative-frequency ordering, and one-sided/two-sided interpretation;
- amplitude quantity, complex power definition, and whether the claim is absolute or relative;
- phase representation and whether unwrap is used;
- bin spacing separately from effective or claimed resolution;
- window, window normalization, leakage assessment, and zero-padding meaning;
- aliasing check and at least one relevant validation evidence item.

The sampling identity is explicit: `dt = 1/Fs`, `T = N*dt`, and `Delta_f = Fs/L` for transform length `L`. A different duration convention may be used only when it is stated and justified. A missing sampling rate must not be silently replaced with a guessed physical frequency axis.

## Frequency and transform conventions

`f` is cycles per second (Hz). `omega` is radians per second. They are related by `omega = 2*pi*f`; the factor must appear in the formula or metadata when a formula and a grid use different units. An FFT bin is an index mapped to a physical frequency, not itself a frequency unit. For a two-sided DFT with `L` points, the unshifted grid is `[0, 1, ..., floor(L/2), ..., -2, -1] * Fs/L` under the usual library convention; `fftshift` must be applied to the frequency array and spectrum together.

Forward and inverse normalization must be stated. For example, the common convention is an unscaled forward DFT and an inverse DFT divided by `L`. Absolute amplitude or power comparisons are not reproducible from the word “FFT” alone. Complex signal power normally uses `|x|^2` or `conj(x)*x`, unless a task-specific physical definition supports another quantity. A literal source expression such as `x^2` is retained as `SOURCE_LITERAL` while the engineering interpretation is recorded separately; it is never silently corrected.

One-sided and two-sided spectra are different quantities. For a real signal, interior bins may require doubling for a one-sided power or density quantity, but the factor depends on the transform normalization, quantity type, DC/Nyquist handling, and density definition. The contract therefore records the sidedness and does not hard-code a universal multiplier.

## Window, leakage, padding, and resolution

Finite observations can leak a non-integral-period component into neighboring bins. A window or longer observation may change that leakage, but side lobes cannot be called additional physical components without evidence. If a non-rectangular window is used for an absolute amplitude or power claim, record the relevant coherent-gain or power normalization.

Zero padding refines the displayed frequency grid. It does not create new observations or improve the physical resolving capability by itself. `bin_spacing = Fs/L` is a grid spacing; effective resolution also depends on observation duration, window main-lobe width, and the estimator. A report that calls `Fs/L` “resolution” must say it means bin spacing or supply a separate resolution basis.

Check the target band against the Nyquist range. If a target frequency is above `Fs/2`, record an anti-alias mechanism or limit the physical interpretation. A visually clean FFT peak is not proof of an unaliased source frequency.

## Phase and preprocessing

Record wrapped versus unwrapped phase, phase range, reference, and whether the quantity is a phase difference or an instantaneous phase. A key unwrap step needs a validity condition or a synthetic/known-sequence check. Mean removal, detrending, filtering, resampling, interpolation, normalization, and segmentation must state how they affect DC, amplitude, power, phase, and bandwidth when those quantities are used.

For multidimensional data, record the time axis explicitly. A plausible spectrum computed along a channel or batch axis is still wrong if the declared transform axis and actual axis differ.

## Conditional PSD/ASD rules

PSD and ASD are activated only when the task reports a density. A communication BER or transfer-function calculation does not need PSD fields merely because an FFT appears in the implementation. If PSD is claimed, record its definition, one/two-sided convention, bandwidth or bin-width normalization, and units such as `quantity^2/Hz`. ASD uses the corresponding `quantity/sqrt(Hz)` form. A plot that looks like a spectrum is not automatically a density.

## Validation and reviewer guards

At least one relevant synthetic or identity check is required: known-tone frequency recovery, FFT-to-IFFT reconstruction, Parseval/energy consistency, or a known transfer-function case. The helper [`../scripts/spectral_conventions.py`](../scripts/spectral_conventions.py) provides deterministic checks and reviewer codes:

`FREQUENCY_AXIS_UNVERIFIED`, `FREQUENCY_UNIT_MISMATCH`, `TRANSFORM_NORMALIZATION_UNVERIFIED`, `COMPLEX_POWER_DEFINITION_INVALID`, `SPECTRUM_SIDEDNESS_UNVERIFIED`, `ZERO_PADDING_AS_RESOLUTION_GAIN`, `BIN_SPACING_AS_RESOLUTION`, `ALIASING_UNVERIFIED`, `PHASE_UNWRAP_UNVERIFIED`, and `SPECTRAL_DENSITY_NORMALIZATION_INVALID`. It also reports `WINDOW_NORMALIZATION_UNVERIFIED` and `TRANSFORM_AXIS_UNVERIFIED` for two common implementation omissions.

The derived status is `SPECTRAL_CONVENTION_VERIFIED` only when the declaration is structurally valid, the sampling identities and required guards pass, and validation evidence is present. Missing or inconsistent declarations are `SPECTRAL_CONVENTION_PARTIAL` or `SPECTRAL_CONVENTION_UNVERIFIED`; they cannot support an absolute quantitative spectral claim.

This contract complements Mechanism Closure. Mechanism Closure asks whether a physical or dynamic model is closed under its assumptions. This contract asks whether sampling and frequency-domain mathematics are represented consistently. Either or both may be active for one task.
