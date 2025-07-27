# test_cli.py
print("Testing CLI imports...")

try:
    import typer
    print("✅ typer import successful")
except Exception as e:
    print(f"❌ typer import failed: {e}")

try:
    from rich.console import Console
    print("✅ rich import successful")
except Exception as e:
    print(f"❌ rich import failed: {e}")

try:
    import main
    print("✅ main.py import successful")
except Exception as e:
    print(f"❌ main.py import failed: {e}")
    import traceback
    traceback.print_exc()

print("CLI import test complete")
