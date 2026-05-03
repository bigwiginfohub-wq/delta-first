#!/usr/bin/env python3
"""
Delta-First v5.0.1 Batch Validator - CORRECTED
"""

import os, sys, json, csv, argparse
from pathlib import Path
from pydantic import BaseModel, field_validator, model_validator, ValidationError
import jsonschema
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. PYDANTIC v5.0.1 MODEL (CORRECTED)
# ─────────────────────────────────────────────────────────────
class DeltaFirstV501(BaseModel):
    auditor_id: str
    audit_id: str
    integrity_score: float = 84.0
    protocol_mode: str = "Full Protocol Mode"
    primary_driver: str
    reasoning_trace: str
    peak_moment: str
    interpretive_anchor: str
    h3_warrant: str
    null_test: str
    label_impact: str
    friction_score_components: dict
    friction_score: float
    mcl_coefficient: float
    boundary: str

    @field_validator('label_impact')
    def validate_label(cls, v):
        if v not in {"Easier", "Harder", "Neutral"}:
            raise ValueError(f"Invalid label_impact: {v}")
        return v

    @model_validator(mode='before')
    def clamp_and_clean(cls, data):
        # If data is a string, parse it
        if isinstance(data, str):
            data = json.loads(data.replace("```json", "").replace("```", "").strip())
        
        # Clamp friction score to [0.0, 1.0]
        if isinstance(data.get('friction_score'), (int, float)):
            data['friction_score'] = round(max(0.0, min(1.0, float(data['friction_score']))), 2)
        
        # Enforce component bounds
        comps = data.get('friction_score_components', {})
        comps['lens_divergence'] = max(0.0, min(0.30, comps.get('lens_divergence', 0.0)))
        comps['warrant_ambiguity'] = max(0.0, min(0.20, comps.get('warrant_ambiguity', 0.0)))
        comps['validation_confidence'] = max(0.0, min(0.10, comps.get('validation_confidence', 0.0)))
        
        return data

# ─────────────────────────────────────────────────────────────
# 2. JSON SCHEMA (Draft 2020-12)
# ─────────────────────────────────────────────────────────────
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["auditor_id", "audit_id", "integrity_score", "protocol_mode", "primary_driver", 
                 "reasoning_trace", "peak_moment", "interpretive_anchor", "h3_warrant", "null_test", 
                 "label_impact", "friction_score_components", "friction_score", "mcl_coefficient", "boundary"],
    "properties": {
        "auditor_id": {"type": "string"},
        "audit_id": {"type": "string"},
        "integrity_score": {"type": "number", "const": 84.0},
        "protocol_mode": {"type": "string", "const": "Full Protocol Mode"},
        "primary_driver": {"type": "string", "enum": ["H1", "H2", "H3"]},
        "reasoning_trace": {"type": "string"},
        "peak_moment": {"type": "string"},
        "interpretive_anchor": {"type": "string"},
        "h3_warrant": {"type": "string"},
        "null_test": {"type": "string"},
        "label_impact": {"type": "string", "enum": ["Easier", "Harder", "Neutral"]},
        "friction_score_components": {
            "type": "object",
            "required": ["base", "lens_divergence", "warrant_ambiguity", "validation_confidence"],
            "properties": {
                "base": {"type": "number", "const": 0.50},
                "lens_divergence": {"type": "number", "minimum": 0.00, "maximum": 0.30},
                "warrant_ambiguity": {"type": "number", "minimum": 0.00, "maximum": 0.20},
                "validation_confidence": {"type": "number", "minimum": 0.00, "maximum": 0.10}
            },
            "additionalProperties": False
        },
        "friction_score": {"type": "number", "minimum": 0.00, "maximum": 1.00},
        "mcl_coefficient": {"type": "number", "minimum": 0.00, "maximum": 1.00},
        "boundary": {"type": "string", "const": "This analysis maps causal plausibility strictly within the locked window. It cannot verify internal deliberations, off-record communications, or post-window developments. Claims are time-locked."}
    },
    "additionalProperties": False
}
# ─────────────────────────────────────────────────────────────
# 3. BATCH PROCESSING LOGIC (CORRECTED)
# ─────────────────────────────────────────────────────────────
def validate_audit(filepath: Path) -> dict:
    """Validate a single audit JSON file. Returns summary dict."""
    result = {
        "file": filepath.name,
        "auditor_id": None,
        "audit_id": None,
        "primary_driver": None,
        "integrity_score": None,
        "friction_score": None,
        "mcl_coefficient": None,
        "label_impact": None,
        "pydantic_pass": False,
        "schema_pass": False,
        "error": None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Parse JSON
        data = json.loads(content)
        
        # Pydantic validation
        validated = DeltaFirstV501(**data)  # Unpack the dictionary
        result["pydantic_pass"] = True
        result["auditor_id"] = validated.auditor_id
        result["audit_id"] = validated.audit_id
        result["primary_driver"] = validated.primary_driver
        result["integrity_score"] = validated.integrity_score
        result["friction_score"] = validated.friction_score
        result["mcl_coefficient"] = validated.mcl_coefficient
        result["label_impact"] = validated.label_impact
        
        # JSON Schema validation
        jsonschema.validate(data, SCHEMA)
        result["schema_pass"] = True
        
    except ValidationError as e:
        result["error"] = f"Pydantic: {e}"
    except jsonschema.exceptions.ValidationError as e:
        result["error"] = f"Schema: {e.message}"
    except json.JSONDecodeError as e:
        result["error"] = f"JSON Parse: {e}"
    except Exception as e:
        result["error"] = f"Unexpected: {type(e).__name__}: {e}"
    
    return result

def run_batch(directory: str, output_csv: str):
    """Scan directory, validate all *.json, write CSV summary."""
    dir_path = Path(directory)
    json_files = sorted(dir_path.glob("*.json"))
    
    if not json_files:
        print(f"⚠️  No *.json files found in {directory}")
        return
    
    results = []
    for filepath in json_files:
        print(f"🔍 Validating {filepath.name}...", end=" ")
        res = validate_audit(filepath)
        status = "✅ PASS" if (res["pydantic_pass"] and res["schema_pass"]) else "❌ FAIL"
        print(status)
        results.append(res)
    
    # Write CSV (only audit files, not the schema file itself)
    fieldnames = ["file", "auditor_id", "audit_id", "primary_driver", "integrity_score", 
                  "friction_score", "mcl_coefficient", "label_impact", "pydantic_pass", 
                  "schema_pass", "error"]
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            # Only include actual audit files (have auditor_id)
            if r.get("auditor_id"):
                writer.writerow(r)
    
    print_summary(results, output_csv)

def print_summary(results: list, csv_path: str):
    """Print terminal distribution report."""
    # Filter to actual audit files
    audit_results = [r for r in results if r.get("auditor_id")]
    
    total = len(audit_results)
    passed = sum(1 for r in audit_results if r["pydantic_pass"] and r["schema_pass"])
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    valid_friction = [r["friction_score"] for r in audit_results if r["friction_score"] is not None]
    valid_mcl = [r["mcl_coefficient"] for r in audit_results if r["mcl_coefficient"] is not None]
    
    print("\n" + "="*60)
    print(f"📊 DELTA-FIRST v5.0.1 | BATCH VALIDATION SUMMARY")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   CSV Output: {csv_path}")
    print("="*60)
    print(f"📁 Audits Processed : {total}")
    print(f"✅ Pass Rate        : {pass_rate:.1f}% ({passed}/{total})")
    
    if valid_friction:
        print(f"\n📈 Friction Score Distribution:")
        print(f"   Mean   : {sum(valid_friction)/len(valid_friction):.2f}")
        print(f"   Min/Max: {min(valid_friction):.2f} / {max(valid_friction):.2f}")
        print(f"   Buckets: Low(≤0.30): {sum(1 for f in valid_friction if f<=0.30)} | "
              f"Med(0.31-0.65): {sum(1 for f in valid_friction if 0.31<=f<=0.65)} | "
              f"High(≥0.66): {sum(1 for f in valid_friction if f>=0.66)}")
    
    if valid_mcl:
        print(f"\n🔗 MCL Coefficient Distribution:")
        print(f"   Mean   : {sum(valid_mcl)/len(valid_mcl):.2f}")
        print(f"   Min/Max: {min(valid_mcl):.2f} / {max(valid_mcl):.2f}")
        print(f"   Strength: Weak(≤0.30): {sum(1 for m in valid_mcl if m<=0.30)} | "
              f"Mod(0.31-0.60): {sum(1 for m in valid_mcl if 0.31<=m<=0.60)} | "
              f"Strong(≥0.61): {sum(1 for m in valid_mcl if m>=0.61)}")
    
    primary_counts = {}
    for r in audit_results:
        if r["primary_driver"]:
            primary_counts[r["primary_driver"]] = primary_counts.get(r["primary_driver"], 0) + 1
    if primary_counts:
        print(f"\n🎯 Primary Driver Distribution: {primary_counts}")
    
    label_counts = {}
    for r in audit_results:
        if r["label_impact"]:
            label_counts[r["label_impact"]] = label_counts.get(r["label_impact"], 0) + 1
    if label_counts:
        print(f"🏷️  Label Impact Distribution: {label_counts}")
    
    if passed < total:
        print(f"\n⚠️  Failed Audits:")
        for r in audit_results:
            if not (r["pydantic_pass"] and r["schema_pass"]):
                print(f"   • {r['file']}: {r['error']}")
    
    print("="*60)

# ─────────────────────────────────────────────────────────────
# 4. CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delta-First v5.0.1 Batch Validator")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing *.json audit files (default: current dir)")
    parser.add_argument("-o", "--output", default="audit_summary.csv", help="Output CSV filename (default: audit_summary.csv)")
    args = parser.parse_args()
    
    print(f"🚀 Delta-First v5.0.1 Batch Validator")
    print(f"   Scanning: {args.directory}")
    print(f"   Output  : {args.output}\n")
    
    run_batch(args.directory, args.output)