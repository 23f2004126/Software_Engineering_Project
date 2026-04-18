import ast
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MATRIX_PATH = ROOT / "apitest.yaml"
SOURCE_FILES = [
    (ROOT / "app" / "main.py", ""),
    (ROOT / "app" / "ml" / "router.py", "/api/ml"),
]


def _load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def _parse_source_routes() -> list[dict]:
    routes = []
    for file_path, prefix in SOURCE_FILES:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if not isinstance(decorator.func, ast.Attribute):
                    continue
                if decorator.func.attr not in {"get", "post", "put", "patch", "delete"}:
                    continue
                if not isinstance(decorator.func.value, ast.Name):
                    continue
                if decorator.func.value.id not in {"app", "router"}:
                    continue
                if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                    continue

                method = decorator.func.attr.upper()
                path = prefix + str(decorator.args[0].value)
                auth = False

                defaults = node.args.defaults
                args = node.args.args
                first_default_index = len(args) - len(defaults)
                for index, arg in enumerate(args):
                    if index < first_default_index:
                        continue
                    default = defaults[index - first_default_index]
                    default_text = ast.get_source_segment(source, default) or ""
                    if "Depends(get_current_user)" in default_text:
                        auth = True

                routes.append({"method": method, "path": path, "auth": auth})
    return routes


def test_matrix_matches_backend_route_inventory():
    matrix = _load_matrix()
    source_routes = _parse_source_routes()

    source_counter = Counter((route["method"], route["path"]) for route in source_routes)
    source_unique = set(source_counter.keys())
    documented_unique = {(route["method"], route["path"]) for route in matrix["endpoints"]}

    assert documented_unique == source_unique
    assert matrix["meta"]["source_definition_count"] == len(source_routes)
    assert matrix["meta"]["unique_route_count"] == len(source_unique)


def test_duplicate_routes_and_effective_auth_are_documented():
    matrix = _load_matrix()
    source_routes = _parse_source_routes()

    source_counter = Counter((route["method"], route["path"]) for route in source_routes)
    source_duplicates = sorted(
        [
            {
                "method": method,
                "path": path,
                "source_occurrences": count,
            }
            for (method, path), count in source_counter.items()
            if count > 1
        ],
        key=lambda item: (item["path"], item["method"]),
    )
    documented_duplicates = sorted(
        matrix["duplicate_route_keys"],
        key=lambda item: (item["path"], item["method"]),
    )

    assert documented_duplicates == source_duplicates

    first_seen_auth = {}
    for route in source_routes:
        first_seen_auth.setdefault((route["method"], route["path"]), route["auth"])

    for documented in matrix["endpoints"]:
        route_key = (documented["method"], documented["path"])
        assert documented["auth"] == first_seen_auth[route_key]
