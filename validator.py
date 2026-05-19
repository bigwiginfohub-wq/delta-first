import json
import re
from pydantic import BaseModel, field_validator, model_validator, ValidationError

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
           raise ValueError("Invalid label_impact enum")
        return v

    @model_validator(mode='before')
    def clamp_and_clean(cls, data):
        if not isinstance(data, (dict, str)):
           raise ValueError("Payload must be a JSON object")

        if isinstance(data, str):
            data = re.sub(r'^```json\s*|\s*```$', '', data.strip(), flags=re.MULTILINE)
            data = json.loads(data)
        
        if isinstance(data.get('friction_score'), (int, float)):
            data['friction_score'] = max(0.0, min(1.0, float(data['friction_score'])))
        
        comps = data.get('friction_score_components', {})
        comps['lens_divergence'] = max(0.0, min(0.30, comps.get('lens_divergence', 0.0)))
        comps['warrant_ambiguity'] = max(0.0, min(0.20, comps.get('warrant_ambiguity', 0.0)))
        comps['validation_confidence'] = max(0.0, min(0.10, comps.get('validation_confidence', 0.0)))
        
        return data


# This is the part you need to add at the bottom
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validator.py <audit_json_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        validated = DeltaFirstV501(**data)
        print("✅ VALIDATION PASSED")
        print(f"   Auditor: {validated.auditor_id}")
        print(f"   Primary Driver: {validated.primary_driver}")
        print(f"   Integrity Score: {validated.integrity_score}")
        print(f"   Friction Score: {validated.friction_score}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    except ValidationError as e:
        print(f"❌ VALIDATION FAILED: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
