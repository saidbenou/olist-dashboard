from pathlib import Path

import pandas as pd

from etl.db import engine


def parse_queries(path: str) -> list[tuple[str, str]]:
    blocks, name, lines = [], None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("-- KPI:"):
            if name:
                blocks.append((name, "\n".join(lines)))
            name, lines = line.removeprefix("-- KPI:").strip(), []
        elif name and not line.startswith("--"):
            lines.append(line)
    if name:
        blocks.append((name, "\n".join(lines)))
    return blocks


if __name__ == "__main__":
    out = ["# Valeurs de référence\n",
           "Chaque mesure DAX du dashboard doit afficher la même valeur que ce tableau.\n"]
    for name, query in parse_queries("sql/02_verifications.sql"):
        df = pd.read_sql(query, engine)
        print(f"\n== {name}\n{df.to_string(index=False)}")
        out.append(f"\n## {name}\n\n{df.to_markdown(index=False, floatfmt='.2f')}\n")
    Path("docs").mkdir(exist_ok=True)
    Path("docs/valeurs_reference.md").write_text("\n".join(out), encoding="utf-8")
    print("\nOK – docs/valeurs_reference.md écrit.")
