"""Evaluate the scalar MATLAB source lines directly using the scalar subset these files use."""
from pathlib import Path
import json
import math
import random
import re
import sys
sys.path.insert(0, "numerics")
from c2c import closed_form as cf

run = Path(__file__).resolve().parents[1]
matlab = Path("numerics/matlab")
names = {"pftaT2Case1": cf.pfta_t2_case1, "pftbT2Case1": cf.pftb_t2_case1,
         "period2_profit": cf.period2_profit, "SpftaT1": cf.spfta_t1, "SpftbT1": cf.spftb_t1,
         "NpftaT1": cf.npfta_t1, "NpftbT1": cf.npftb_t1, "FindGeneral_exo": cf.find_general_exo}
scalar = {}
for name in names:
    path, = matlab.rglob(name + ".m")
    source = re.sub(r"%[^\n]*", "", path.read_text()).replace("...\n", " ")
    header, *body = [line.strip().strip(";") for line in source.splitlines() if line.strip()]
    outputs, function, inputs = re.fullmatch(r"function\s+(.+?)\s*=\s*(\w+)\((.*?)\)", header).groups()
    assert function == name
    py = ["def " + name + "(" + inputs + "):"]
    depth = 1
    for line in body:
        if line == "end":
            depth -= 1
            continue
        if line.startswith("switch "):
            switch = line[7:]
            continue
        if line.startswith("case "):
            if line == "case 'S'":
                line = "if " + switch + " == 'S':"
            else:
                depth -= 1
                line = "elif " + switch + " == 'N':"
        elif line == "otherwise" or line == "else":
            depth -= 1
            line = "else:"
        elif line.startswith("if "):
            line += ":"
        elif line.startswith("error("):
            line = "raise ValueError('unexpected scenario')"
        line = line.replace("~]", "_]").replace("[~", "[_").replace("^", "**")
        py.append("    " * depth + line)
        if line.endswith(":"):
            depth += 1
    py.append("    return " + outputs.strip("[]"))
    exec("\n".join(py), scalar)
rng = random.Random(2226)
metrics = {name: [0, 0.0] for name in names}
branches = set()
for i in range(300):
    ca, cb = sorted(rng.uniform(.3, 1.2) for _ in range(2))
    pa, pb, qa, qb = [rng.uniform(1.4, 4.5) for _ in range(4)]
    if i % 10 == 0:
        ca, cb, qa, qb = .5, 1., 2., 4.
    theta = [0, 1, rng.random()][i % 3]
    gamma = [0., 1.e-5, 2., rng.uniform(.01, 25)][i % 4]
    beta, mu, sig = .06, 10., rng.uniform(.1, 7)
    params = pa, pb, qa, qb, theta, ca, cb, beta, mu, sig, gamma
    q = qa, qb, theta, ca, cb, beta, mu, sig
    w, ra, rb = rng.random(), rng.uniform(0, 4), rng.uniform(0, 4)
    cases = [(name, params) for name in names if name.endswith("T1")]
    cases += [("pftaT2Case1", q), ("pftbT2Case1", (qa, qb, cb, beta, mu, sig)),
              ("FindGeneral_exo", params + (w, 1-w))]
    cases += [("period2_profit", q + (scenario, gamma, ra, rb)) for scenario in ("S", "N")]
    branches.add((ca/qa > cb/qb, cf.first_period_s(*params)[-1], cf.first_period_n(*params)[-1]))
    for name, arguments in cases:
        a, b = scalar[name](*arguments), names[name](*arguments)
        if not isinstance(a, tuple):
            a, b = (a,), (b,)
        for x, y in zip(a, b, strict=True):
            assert math.isclose(x, y, rel_tol=1e-12, abs_tol=5e-12), (name, x, y)
            metrics[name][0] += 1
            metrics[name][1] = max(metrics[name][1], abs(x - y))
print(json.dumps({"markets": 300, "scalar_comparisons": sum(e[0] for e in metrics.values()),
                  "by_file": metrics, "branch_combinations_seen": len(branches)}, indent=2))
