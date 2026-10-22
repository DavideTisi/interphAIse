"""Build the README SVGs and editable Mermaid sources using only the standard library.

Run from the repository root: python scripts/build_workflow_diagrams.py
The diagrams describe scientific roles; model provenance is reported separately.
No network, experiment archive mutation or scientific calculation is performed.
"""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/diagrams"
DIAGRAMS = [
    {
        "name": "discovery-workflow",
        "title": "Thermodynamic discovery",
        "subtitle": "Does numerical feedback improve the next material choice?",
        "human": "Candidate pool, objective, information shown and evaluation budget",
        "nodes": [
            ("LLM", ["Propose a coating", "and a hypothesis"], ["Choose an untested ID"], True),
            ("CODE", ["Validate the choice", "and charge a query"], ["Save ID and rationale"], False),
            ("THERMODYNAMICS", ["Reveal stability", "and reaction scores"], ["Frozen score table", "Check insulation too"], False),
            ("LLM", ["Assess the evidence", "and choose again"], ["Keep or revise the idea"], True),
        ],
        "feedback": "Stability, contact reactions and insulation inform the next hypothesis",
        "footer": "Correct-feedback arm shown. Controls remove, shuffle or pre-empt feedback; random is the baseline.",
        "description": "Humans fix the candidate pool, objective, information and budget. The LLM proposes a coating and chemical hypothesis. Code validates and records the choice and charges the query. The evaluator reveals the selected candidate's precomputed stability, contact-reaction and insulation scores. The LLM assesses this evidence to choose again within the budget. Controls and random search test the value of feedback.",
    },
    {
        "name": "petmad-workflow",
        "title": "Prospective interface tests",
        "subtitle": "Do the LLM's adhesion forecasts survive a new physical calculation?",
        "human": "Buildable menu, reference results, contact geometries and calculation budget",
        "nodes": [
            ("LLM", ["Choose a coating", "and predict adhesion"], ["Two ranges + weaker contact"], True),
            ("CODE", ["Archive forecasts", "before calculations"], ["Save the decision-time evidence"], False),
            ("ATOMISTIC CALCULATION", ["Calculate adhesion", "at both contacts"], ["ASE + PET-MAD", "Validate primary results"], False),
            ("LLM", ["Assess predictions", "and revise the idea"], ["Read validated feedback"], True),
        ],
        "feedback": "Validated adhesion and weaker-contact results inform the next choice",
        "footer": "Predictions are saved first. Withheld sensitivity results are released only after the final summary.",
        "description": "Humans fix a buildable menu, reference results, contact geometries and budget. The LLM selects a coating and predicts adhesion ranges for both contacts and the weaker contact. Code archives the choice and forecasts before new energies exist. ASE and PET-MAD calculate adhesion on the frozen interfaces; primary results are validated. The LLM assesses its predictions and chooses again within the pilot budget. Sensitivity results remain withheld until the final summary. Model names belong to the archived experiment provenance, not to these role labels.",
    },
]


def text(x, y, value, size=16, weight=400, color="#172b3a", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')


def svg(spec):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="406" '
        'viewBox="0 0 1000 406" role="img" aria-labelledby="title description">',
        f'<title id="title">{escape(spec["title"])}</title>',
        f'<desc id="description">{escape(spec["description"])}</desc>',
        '<defs>',
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#667786"/></marker>',
        '<marker id="feedback-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#087f8c"/></marker>',
        '</defs>',
        '<rect width="1000" height="406" rx="12" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif">',
        text(28, 39, spec["title"], 26, 700),
        text(28, 67, spec["subtitle"], 17, color="#526472"),
        text(28, 106, "Humans define", 15, 700),
        text(146, 106, spec["human"], 15, color="#526472"),
        '<path d="M28 121 H972" stroke="#d9e0e5"/>',
    ]
    for i, (role, title, detail, is_llm) in enumerate(spec["nodes"]):
        x = 28 + i * 246
        cx = x + 103
        fill, stroke = ("#e3f3f1", "#087f8c") if is_llm else ("#f1f4f7", "#8a99a8")
        parts.append(f'<rect x="{x}" y="142" width="206" height="144" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        role_color = "#0b5a63" if is_llm else "#526472"
        parts.append(text(cx, 164, role, 11.5, 700, color=role_color, anchor="middle"))
        for j, line in enumerate(title):
            parts.append(text(cx, 195 + j * 24, line, 18, 600, anchor="middle"))
        for j, line in enumerate(detail):
            parts.append(text(cx, 247 + j * 19, line, 13, color="#526472", anchor="middle"))
        if i < 3:
            parts.append(f'<path d="M{x + 211} 214 H{x + 239}" fill="none" stroke="#667786" stroke-width="1.8" marker-end="url(#arrow)"/>')
    parts += [
        '<path d="M869 291 V320 H131 V291" fill="none" stroke="#087f8c" stroke-width="2" marker-end="url(#feedback-arrow)"/>',
        text(500, 347, "Feedback: " + spec["feedback"], 16, 600, color="#087f8c", anchor="middle"),
        text(500, 382, spec["footer"], 13.5, color="#526472", anchor="middle"),
        '</g>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def mermaid(spec):
    lines = [f'%% {spec["title"]}', f'%% {spec["subtitle"]}', 'flowchart LR',
             f'    H["Humans define<br/>{escape(spec["human"])}"]']
    llm, tools = [], []
    for i, (role, title, detail, is_llm) in enumerate(spec["nodes"], 1):
        node = f"N{i}"
        label = "<br/>".join(escape(line) for line in [role, *title, *detail])
        lines.append(f'    {node}("{label}")' if is_llm else f'    {node}["{label}"]')
        (llm if is_llm else tools).append(node)
    lines += [
        '    H -. "Frozen protocol" .-> N1',
        '    N1 --> N2 --> N3 --> N4',
        f'    N4 -- "Feedback: {escape(spec["feedback"])}" --> N1',
        '    classDef llm fill:#e3f3f1,stroke:#087f8c,color:#0b3b40',
        '    classDef tools fill:#f1f4f7,stroke:#8a99a8,color:#172b3a',
        '    class ' + ','.join(llm) + ' llm',
        '    class ' + ','.join(tools) + ' tools',
        f'%% {spec["footer"]}',
    ]
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for spec in DIAGRAMS:
        for suffix, build in (("svg", svg), ("mmd", mermaid)):
            path = OUT / f'{spec["name"]}.{suffix}'
            path.write_text(build(spec), encoding="utf-8")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
