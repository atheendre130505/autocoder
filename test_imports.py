# test_imports.py
print("Testing imports...")

try:
    from config import get_config
    print("✅ config import successful")
except Exception as e:
    print(f"❌ config import failed: {e}")

try:
    from execution_engine import AutonomousExecutor, ExecutionResult
    print("✅ execution_engine import successful")
except Exception as e:
    print(f"❌ execution_engine import failed: {e}")

try:
    from safety_controls import validate_command
    print("✅ safety_controls import successful")
except Exception as e:
    print(f"❌ safety_controls import failed: {e}")

try:
    from error_analyzer import ErrorAnalyzer
    print("✅ error_analyzer import successful")
except Exception as e:
    print(f"❌ error_analyzer import failed: {e}")

try:
    from ai_agents import autonomous_develop_with_execution
    print("✅ ai_agents import successful")
except Exception as e:
    print(f"❌ ai_agents import failed: {e}")

print("Import testing complete")
