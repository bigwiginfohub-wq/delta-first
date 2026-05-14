🌐 Live Dashboard:  https://vinsta-org.netlify.app/
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20009717.svg)](https://doi.org/10.5281/zenodo.20009717)
Uploaded on: 03-05-2026
# Delta-First v5.0.1

A validated protocol for causal auditing under ambiguity.

**Status:** Production-ready. Validated across geopolitical, supply chain, and clinical domains.

---

## What is Delta-First?

Delta-First is a method for auditing causal claims when evidence is contested, ambiguous, or incomplete.

It helps answer questions like:
* Is this claim supported by verifiable evidence?
* Where do different interpretations diverge?
* What would falsify this conclusion?

**Core components:**
* **H₃ Warrants** — Explicit falsification conditions
* **Friction Scores** — Measures interpretive divergence (0.0–1.0)
* **MCL Coefficients** — Measures causal linkage strength (0.0–1.0)

---

## Who Is This For?

* Independent auditors
* Researchers analyzing contested claims
* Organizations needing to verify AI outputs
* Policymakers evaluating evidence

**No technical background required. The scripts handle the math.**

---

## Requirements

* Python 3.8 or higher
* pip (Python package manager)

---

## Installation

```bash
# Clone the repository (or download the files manually)
git clone https://github.com/bigwiginfohub-wq/delta-first.git
cd delta-first

# Install dependencies
pip install pydantic jsonschema
```

---

Quick Start

1. Test with the example audit

```bash
python validator.py example_audit.json
```

Expected output:

```
✅ VALIDATION PASSED
   Auditor: example-auditor-001
   Primary Driver: H3
   Integrity Score: 84.0
   Friction Score: 0.67
```

2. Validate your own audit

Create a JSON file (see format below). Then run:

```bash
python validator.py your_audit.json
```

3. Batch validate many audits

```bash
python batch_validator.py --folder ./audits --output report.csv
```

This generates a CSV file with pass/fail results, friction scores, and MCL values for every audit.

---

Audit File Format

Your audit JSON must include these fields:

Field Type Required
auditor_id string Yes
audit_id string Yes
integrity_score number (84.0) Yes
protocol_mode string ("Full Protocol Mode") Yes
primary_driver string ("H1"/"H2"/"H3") Yes
reasoning_trace string Yes
peak_moment string Yes
interpretive_anchor string Yes
h3_warrant string Yes
null_test string Yes
label_impact string ("Easier"/"Harder"/"Neutral") Yes
friction_score_components object Yes
friction_score number (0.0–1.0) Yes
mcl_coefficient number (0.0–1.0) Yes
boundary string (verbatim) Yes

See example_audit.json for a complete example.

---

Understanding the Output

Output Field Meaning
VALIDATION PASSED All checks passed
Auditor Your auditor identifier
Primary Driver H1, H2, or H3
Integrity Score Evidence quality (should be 84.0)
Friction Score Interpretive divergence (higher = more contested)
MCL Coefficient Causal linkage strength

Friction Score interpretation:

· 0.00–0.30: Low divergence
· 0.31–0.65: Moderate divergence
· 0.66–1.00: High divergence

MCL interpretation:

· 0.00–0.30: Weak linkage
· 0.31–0.60: Moderate linkage
· 0.61–1.00: Strong linkage

---

Troubleshooting

Error Solution
No module named pydantic Run pip install pydantic
No module named jsonschema Run pip install jsonschema
JSON parse error Check your JSON syntax (commas, brackets)
Additional properties are not allowed Your JSON has extra fields not in schema
File not found Make sure the file path is correct

---

License

· Code (validator.py, batch_validator.py, schema): MIT License
· Protocol specification: Creative Commons Attribution 4.0 International (CC BY 4.0)

You are free to use, modify, and distribute the code. If you use the protocol in research or publications, please cite this repository.

---

Authors

· Protocol Design & Validation: The Bridge Architect
· Code Implementation: AI Partner

---

## Links

- **Full Protocol Specification:** [protocol_specification.md](protocol_specification.md)
- **Report Issues:** [GitHub Issues](https://github.com/bigwiginfohub-wq/delta-first/issues)
- **Validation Summary:** [VALIDATION.md](VALIDATION.md)
- 
· **Contact: bigwiginfohub@gmail.com**

---

Citation

If you use Delta-First in your work, please cite:

```bibtex
@misc{deltafirst2026,
  title={Delta-First: A Validated Protocol for Causal Auditing Under Ambiguity},
  author={[Your Last Name], [Your Name]},
  year={2026},
  howpublished={\url{https://github.com/bigwiginfohub-wq/delta-first}}
}
```

---

Status

✅ Production-ready
✅ Validated across geopolitical, supply chain, and clinical domains
✅ Inter-rater reliability tested
✅ Open source (MIT)

---

The mirror does not change. You change by seeing yourself in it.
