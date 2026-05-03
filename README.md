# Delta-First v5.0.1

A validated protocol for causal auditing under ambiguity.

## What is Delta-First?

Delta-First is a method for auditing causal claims when evidence is contested, ambiguous, or incomplete. It uses:
- **H₃ Warrants** (falsification conditions)
- **Friction Scores** (interpretive divergence)
- **MCL Coefficients** (causal linkage strength)

## Quick Start

```bash
# Install dependencies
pip install pydantic jsonschema

# Validate a single audit
python validator.py example_audit.json

# Batch validate all audits in a folder
python batch_validator.py --folder ./audits --output report.csv

## Author
The Bridge Architect

## License
- Code: MIT
- Protocol Specification: CC BY 4.0

##Contact
bigwiginfohub@gmail.com
