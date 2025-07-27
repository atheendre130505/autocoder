# error_analyzer.py
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ErrorDiagnosis:
    error_type: str
    severity: str
    suggested_fixes: List[str]
    auto_fixable: bool
    missing_dependencies: List[str]

class ErrorAnalyzer:
    def __init__(self, ai_agent):
        self.ai_agent = ai_agent
        self.common_errors = self._load_error_patterns()
    
    def _load_error_patterns(self) -> Dict[str, Dict]:
        # Minimal implementation: load common error patterns
        return {
            "ModuleNotFoundError": {"severity": "high", "suggested_fixes": ["Install the missing module."]},
            "SyntaxError": {"severity": "medium", "suggested_fixes": ["Check the syntax in your code."]}
        }
    
    def analyze_error(self, code: str, error: str, task: str) -> ErrorDiagnosis:
        # Minimal implementation for error analysis
        # In a real implementation, you might use regex matching against self.common_errors here
        diagnosis = ErrorDiagnosis(
            error_type="Unknown",
            severity="medium",
            suggested_fixes=["Review the error message and check your code."],
            auto_fixable=False,
            missing_dependencies=[]
        )
        for key, pattern in self.common_errors.items():
            if key in error:
                diagnosis.error_type = key
                diagnosis.severity = pattern.get("severity", "medium")
                diagnosis.suggested_fixes = pattern.get("suggested_fixes", [])
                # Example: extract missing module if applicable
                if key == "ModuleNotFoundError":
                    matches = re.findall(r"No module named '([^']+)'", error)
                    diagnosis.missing_dependencies = matches
                break
        return diagnosis
