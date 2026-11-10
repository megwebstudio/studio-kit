#!/usr/bin/env python3
"""Run the real kit scripts on demo inputs and save their real output.

  python3 tools/capture_examples.py [--json PATH]
  python3 tools/capture_examples.py --deploy-gate-only --json PATH   (refresh only the deploy-gate entries)

Writes assets/examples/*.txt (pasted into README.md by tools/build_readme.py) and, with --json PATH,
the same data as JSON. Nothing here is typed by hand: every line comes from running the actual code.
Fake keys are assembled at runtime and appear only masked in the outputs.
"""
import json
import os
import random
import string
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREE = os.path.join(ROOT, "plugins", "studio-kit")
OUT_TXT = os.path.join(ROOT, "assets", "examples")
OUT_JSON = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else ""
PY = sys.executable


def run(cmd, stdin=None, cwd=None):
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, cwd=cwd, timeout=600)
    return p.returncode, (p.stdout + p.stderr).strip()


def hook(script, payload, cwd):
    code, out = run([PY, os.path.join(FREE, "hooks", script)], stdin=json.dumps(payload), cwd=cwd)
    return json.loads(out) if out.startswith("{") else {"raw": out, "exit": code}


def deploy_gate_examples(demo, examples):
    """deploy-gate on a production deploy, a database migration, and a push in bypassPermissions mode."""
    cmd = "npm run build && npx vercel --prod"
    out = hook("deploy_gate.py", {"tool_name": "Bash", "tool_input": {"command": cmd},
                                  "permission_mode": "default", "cwd": demo}, demo)
    examples["deploy_gate"] = {"input": cmd, "decision": out["hookSpecificOutput"]["permissionDecision"],
                               "reason": out["hookSpecificOutput"]["permissionDecisionReason"]}
    out2 = hook("deploy_gate.py", {"tool_name": "Bash", "tool_input": {"command": "git push origin main"},
                                   "permission_mode": "bypassPermissions", "cwd": demo}, demo)
    examples["deploy_gate_bypass"] = {"input": "git push origin main  (in bypassPermissions mode)",
                                      "decision": out2["hookSpecificOutput"]["permissionDecision"],
                                      "reason": out2["hookSpecificOutput"]["permissionDecisionReason"]}
    cmd3 = "supabase db push"
    out3 = hook("deploy_gate.py", {"tool_name": "Bash", "tool_input": {"command": cmd3},
                                   "permission_mode": "default", "cwd": demo}, demo)
    examples["deploy_gate_migration"] = {"input": cmd3, "decision": out3["hookSpecificOutput"]["permissionDecision"],
                                         "reason": out3["hookSpecificOutput"]["permissionDecisionReason"]}


def main():
    os.makedirs(OUT_TXT, exist_ok=True)
    demo = tempfile.mkdtemp(prefix="studio-kit-demo-")
    run(["git", "init", "-q", "-b", "main", demo])
    examples = {}
    if "--deploy-gate-only" in sys.argv:
        # refresh only the deploy-gate entries of the JSON at --json PATH (the other examples stay as captured)
        deploy_gate_examples(demo, examples)
        with open(OUT_JSON) as fh:
            data = json.load(fh)
        data.update(examples)
        with open(OUT_JSON, "w") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(json.dumps(examples, indent=2))
        return

    # 1. deploy-gate
    deploy_gate_examples(demo, examples)

    # 2. secret-guard on a browser-exposed key
    rng = random.Random(11)
    key = "sk-" + "proj-" + "".join(rng.choice(string.ascii_letters + string.digits) for _ in range(48))
    content = "VITE_OPENAI_API_KEY=%s\n" % key
    out = hook("secret_guard.py", {"tool_name": "Write", "tool_input": {"file_path": ".env.local", "content": content},
                                   "cwd": demo}, demo)
    reason = out["hookSpecificOutput"]["permissionDecisionReason"]
    assert key not in reason, "secret leaked into the example"
    examples["secret_guard"] = {"input": "Write .env.local: VITE_OPENAI_API_KEY=sk-proj-...",
                                "decision": out["hookSpecificOutput"]["permissionDecision"], "reason": reason}

    # 3. concrete-copy linter on a page with AI tells
    page = os.path.join(demo, "index.html")
    with open(page, "w") as fh:
        fh.write("<html><head><title>Elevate Your Dining Journey</title></head><body>"
                 "<h1>Unlock a seamless taste experience</h1>"
                 "<p>Not just a restaurant, it's a lifestyle — crafted with passion.</p>"
                 "<a href='/menu'>Learn more</a></body></html>")
    code, out = run([PY, os.path.join(FREE, "skills", "concrete-copy", "scripts", "copy_lint.py"), page])
    examples["copy_lint"] = {"input": "python3 copy_lint.py index.html", "exit": code,
                             "output": out.replace(demo + "/", "").replace(demo, ".")}

    # 4. five-attacks bundle scan on a build folder with a leaked key
    dist = os.path.join(demo, "dist", "assets")
    os.makedirs(dist)
    with open(os.path.join(dist, "index-4f2a.js"), "w") as fh:
        fh.write('const client=new OpenAI({apiKey:"%s",dangerouslyAllowBrowser:true});' % key)
    code, out = run([PY, os.path.join(FREE, "skills", "five-attacks", "scripts", "scan_bundle.py"),
                     os.path.join(demo, "dist")])
    assert key not in out
    examples["scan_bundle"] = {"input": "python3 scan_bundle.py dist/", "exit": code,
                               "output": out.replace(demo + "/", "").replace(demo, ".")}

    # 5. launch-qa, if the skill is present (needs Playwright + Chromium)
    lq = os.path.join(FREE, "skills", "launch-qa", "scripts", "launch_qa.py")
    if os.path.isfile(lq):
        site = os.path.join(demo, "site")
        os.makedirs(site)
        with open(os.path.join(site, "index.html"), "w") as fh:
            fh.write("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
                     "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                     "<title>Osteria Lume</title><meta name='description' content='Fresh pasta every morning.'>"
                     "</head><body style='margin:0;font-family:system-ui'>"
                     "<header style='padding:24px'><h1>Fresh pasta every morning</h1>"
                     "<a href='/book.html' style='display:inline-block;padding:14px 22px'>Book a table</a></header>"
                     "<div style='width:1600px;height:40px;background:#eee'>wide promo banner</div>"
                     "<img src='/hero.jpg'><a href='/missing.html'>Old menu</a>"
                     "<script>console.error('menu.json failed to load')</script></body></html>")
        with open(os.path.join(site, "book.html"), "w") as fh:
            fh.write("<!doctype html><title>Book</title><p>ok</p>")
        out_dir = os.path.join(demo, "qa-out")
        code, out = run([PY, lq, site, "--out", out_dir])
        examples["launch_qa"] = {"input": "python3 launch_qa.py site/", "exit": code,
                                 "output": out.replace(demo + "/", "").replace(demo, ".")}

    if OUT_JSON:
        with open(OUT_JSON, "w") as fh:
            json.dump(examples, fh, indent=2, ensure_ascii=False)
    for name, ex in examples.items():
        with open(os.path.join(OUT_TXT, name + ".txt"), "w") as fh:
            fh.write("$ %s\n" % ex["input"])
            if "decision" in ex:
                fh.write("decision: %s\n%s\n" % (ex["decision"], ex["reason"]))
            else:
                fh.write("%s\n(exit %s)\n" % (ex["output"], ex["exit"]))
    print("captured: %s" % ", ".join(examples))
    print("demo folder: %s" % demo)


if __name__ == "__main__":
    main()
