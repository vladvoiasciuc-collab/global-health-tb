import ast
from pathlib import Path

APP = Path(__file__).parent.parent / "app"

# Allowed imports between layers (dependency rule)
ALLOWED = {
    "domain": set(),
    "repositories": {"domain", "models"},
    "services": {"domain", "repositories"},
    "controllers": {"domain", "services", "dependencies"},
    "dependencies": {"services", "repositories", "database"},
}


def _layer_of(path: Path) -> str | None:
    rel = path.relative_to(APP)
    if rel.parts[0] in ALLOWED:
        return rel.parts[0]
    return None


def test_dependency_rule():
    """No layer may import from a higher layer."""
    for py in APP.rglob("*.py"):
        layer = _layer_of(py)
        if layer is None:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app."):
                imported = node.module.split(".")[1]
                if imported not in ALLOWED.get(layer, set()) and imported != layer:
                    raise AssertionError(
                        f"{py.relative_to(APP)} (layer '{layer}') imports '{imported}' which is not allowed"
                    )
