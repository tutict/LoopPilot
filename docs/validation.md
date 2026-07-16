# Validation

LoopPilot has no runtime dependency. The tools in this document are maintenance-only
checks for repository syntax and structure; they do not establish behavioral or host
compatibility.

## Static Checks

Create a temporary Python environment outside the repository, then run:

```text
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate.py
git diff --check
```

`scripts/validate.py` uses PyYAML rather than a handwritten YAML parser. It checks
required files, Skill frontmatter, YAML mappings and duplicate keys, Markdown code
fences, final newlines, trailing whitespace, relative links, the declared Skill word
range, and extractable Mermaid blocks.

## Mermaid Rendering

Extract the diagrams to a temporary directory and render both with the pinned CLI:

```text
python scripts/validate.py --extract-mermaid .tmp/mermaid
npx --yes --package @mermaid-js/mermaid-cli@11.16.0 mmdc -i .tmp/mermaid/README-1.mmd -o .tmp/mermaid/README-1.svg
npx --yes --package @mermaid-js/mermaid-cli@11.16.0 mmdc -i .tmp/mermaid/docs-lifecycle-1.mmd -o .tmp/mermaid/docs-lifecycle-1.svg
```

Confirm both commands exit successfully and both SVG files are non-empty. Keep the
temporary sources and render outputs outside commits.

## Continuous Integration

The `Validate` GitHub Actions workflow repeats the Python tests, static validator,
Mermaid renders, output-size checks, and `git diff --check` on pushes and pull
requests. A local pass does not imply that a remote workflow run passed; report each
environment separately.

## Validation Boundary

These checks do not measure implicit activation accuracy, completion behavior,
replanning quality, or compatibility with a named host. Record those results only
from observed evaluation traces using the templates under `evaluations/`.
