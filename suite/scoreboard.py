#!/usr/bin/env python3
"""Render raw.json from run.py into the Native | PAM | RN scoreboard."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# (scenario, key, label, unit, floor) — every metric is lower-is-better.
# floor: "native"  -> physical floor is the platform-native app (PAM can at best
#                     match it, so the reachable RN/PAM is RN/Native);
#        "zero"    -> the floor is ~0 (idle work); ratios are bounded only by the
#                     measurement resolution (`res`);
#        "algo"    -> computation: the framework may beat idiomatic native code.
METRICS = [
    ("cold_start", "ttid_ms_median", "Cold start TTID (mediana)", "ms", "native", 1),
    ("cold_start", "ttfd_ms_median", "Cold start até conteúdo (mediana)", "ms", "native", 1),
    ("list", "ready_ms", "Lista 10k: tempo até conteúdo", "ms", "native", 1),
    ("list", "p90_ms", "Lista 10k: frame p90", "ms", "native", 1),
    ("list", "p99_ms", "Lista 10k: frame p99", "ms", "native", 1),
    ("list", "janky_pct", "Lista 10k: jank", "%", "native", 0.1),
    ("list", "cpu_ms", "Lista 10k: CPU no scroll", "ms", "native", 10),
    ("list", "pss_kb", "Lista 10k: PSS", "KB", "native", 1),
    ("grid", "ready_ms", "Grade 500 imgs: primeira imagem", "ms", "native", 1),
    ("grid", "p99_ms", "Grade 500 imgs: frame p99", "ms", "native", 1),
    ("grid", "janky_pct", "Grade 500 imgs: jank", "%", "native", 0.1),
    ("grid", "cpu_ms", "Grade 500 imgs: CPU", "ms", "native", 10),
    ("grid", "pss_kb", "Grade 500 imgs: PSS", "KB", "native", 1),
    ("like", "touch_to_pixel_ms_median", "Curtir: toque→pixel (mediana)", "ms", "native", 1),
    ("like", "cpu_ms_per_tap", "Curtir: CPU por toque", "ms", "native", 10),
    ("like", "rerender_nodes_median", "Curtir: nós re-renderizados", "nós", "native", 1),
    ("filter", "key_to_pixel_ms_median", "Filtro: tecla→pixel (mediana)", "ms", "native", 1),
    ("filter", "cpu_ms_per_key", "Filtro: CPU por tecla", "ms", "native", 10),
    ("anim", "cpu_ms", "Animação 60 s: CPU", "ms", "native", 10),
    ("anim", "wakeups_per_min", "Animação 60 s: wakeups/min", "/min", "native", 1),
    ("idle60", "cpu_ms", "Ocioso 60 s: CPU", "ms", "zero", 10),
    ("idle60", "wakeups_per_min", "Ocioso 60 s: wakeups/min", "/min", "zero", 1),
    ("idle60", "pss_kb", "Ocioso: PSS", "KB", "native", 1),
    ("idle60", "threads", "Ocioso: threads", "", "native", 1),
    ("idle600", "cpu_ms", "Ocioso 10 min: CPU", "ms", "zero", 10),
    ("idle600", "wakeups_per_min", "Ocioso 10 min: wakeups/min", "/min", "zero", 1),
    ("idle600", "mah", "Ocioso 10 min: mAh (batterystats)", "mAh", "zero", 0.00001),
    ("bg600", "cpu_ms", "Background 10 min: CPU", "ms", "zero", 10),
    ("bg600", "wakeups_per_min", "Background 10 min: wakeups/min", "/min", "zero", 1),
    ("bg600", "mah", "Background 10 min: mAh", "mAh", "zero", 0.00001),
    ("nav", "pss_growth_kb_cycle1_to_last", "Nav 20 telas: crescimento PSS (ciclo 1→3)", "KB", "zero", 256),
    ("nav", "pss_kb_peak_last", "Nav 20 telas: PSS no pico", "KB", "native", 1),
    ("nav", "push_to_ready_ms_median", "Nav: toque→tela (mediana)", "ms", "native", 1),
    ("video", "cpu_ms", "Vídeo 60 s: CPU do app", "ms", "native", 10),
    ("video", "codec_cpu_pct", "Vídeo 60 s: CPU do codec", "%", "native", 0.1),
    ("video", "wakeups_per_min", "Vídeo 60 s: wakeups/min", "/min", "native", 1),
    ("apk", "apk_bytes", "Tamanho do APK (x86_64)", "B", "native", 1),
    ("feed", "reopen_bytes", "Reabrir com cache: bytes de rede", "B", "zero", 100),
    ("feed", "reopen_ready_ms", "Reabrir com cache: tempo até conteúdo", "ms", "native", 1),
    ("state", "delta_kb", "Estado 100k registros: memória", "KB", "algo", 1),
    ("compute", "search_build", "Busca 100k: preparar", "ms", "algo", 0.1),
    ("compute", "search_query", "Busca 100k: 100 consultas", "ms", "algo", 0.1),
    ("compute", "json_parse", "JSON 5 MB: parse", "ms", "algo", 0.1),
    ("compute", "json_stringify", "JSON 5 MB: serializar", "ms", "algo", 0.1),
    ("compute", "sort", "Ordenar 100k", "ms", "algo", 0.1),
    ("compute", "sha256", "SHA-256 10 MiB", "ms", "algo", 0.1),
    ("compute", "diff", "Diff de listas 100k", "ms", "algo", 0.1),
]


def value(app: dict, scenario: str, key: str):
    if scenario == "apk":
        return app.get("apk_bytes")
    if scenario == "compute":
        op = (app.get("compute") or {}).get("ops", {}).get(key)
        return op["ms"] if op else None
    return (app.get(scenario) or {}).get(key)


def fmt(v, unit=""):
    if v is None:
        return "—"
    if isinstance(v, float) and 0 < abs(v) < 0.1:
        return f"{v:.2g}"
    if isinstance(v, float) and not v.is_integer():
        return f"{v:,.2f}".replace(",", " ")
    return f"{int(v):,}".replace(",", " ")


def ratio(a, b, res):
    if a is None or b is None:
        return None, ""
    lo = False
    if b < res:
        b, lo = res, True
    a = max(a, res)
    return a / b, ("≥" if lo else "")


def render(raw: dict, candidate: dict | None = None, label: str = "PAM cand.") -> str:
    apps = raw.get("apps", {})
    nat, pam, rn = apps.get("native", {}), apps.get("pam", {}), apps.get("rn", {})
    base = pam
    if candidate is not None:
        pam = candidate.get("apps", {}).get("pam", {})
    dev = raw.get("device", {})
    out = [
        f"Dispositivo: {dev.get('ro.product.model')} Android {dev.get('ro.build.version.release')} "
        f"(API {dev.get('ro.build.version.sdk')}, {dev.get('ro.product.cpu.abi')}, {dev.get('refresh_hz')} Hz)"
        + ("  **modo rápido (janelas curtas)**" if raw.get("quick") else ""),
        "",
        ("| Métrica | Nativo | PAM 1.41.0 | " + label + " | RN | PAM/Nativo | RN/PAM | ≥5x | meta 20x | teto |"
         if candidate is not None else
         "| Métrica | Nativo | PAM | RN | PAM/Nativo | RN/PAM | ≥5x | meta 20x | teto |"),
        ("| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: | --- |" if candidate is not None else
         "| --- | ---: | ---: | ---: | ---: | ---: | :---: | :---: | --- |"),
    ]
    for sc, key, label_, unit, floor, res in METRICS:
        label_text = label_
        n, p, r = value(nat, sc, key), value(pam, sc, key), value(rn, sc, key)
        if n is None and p is None and r is None:
            continue
        pn, pn_s = ratio(p, n, res)
        rp, rp_s = ratio(r, p, res)
        rn_, rn_s = ratio(r, n, res)
        if floor == "native":
            ceiling = rn_
            teto = f"físico: nativo (máx RN/PAM ≈ {rn_:.1f}x)" if rn_ else "físico: nativo"
        elif floor == "zero":
            ceiling = None
            teto = f"~0 (resolução {res} {unit})"
        else:
            ceiling = None
            teto = "algorítmico (pode superar o nativo)"
        five = "✅" if rp and rp >= 5 else ("❌" if rp else "—")
        if rp and rp >= 20:
            meta = "✅ atingida"
        elif ceiling is not None and ceiling < 20:
            meta = "físico"
        elif rp:
            meta = "alcançável"
        else:
            meta = "—"
        flag = " ⚠️" if pn and pn > 1.1 and floor != "algo" else ""
        b = value(base, sc, key)
        mid = f"{fmt(b)} | {fmt(p)}" if candidate is not None else fmt(p)
        out.append(
            f"| {label_text} ({unit}) | {fmt(n)} | {mid} | {fmt(r)} | "
            f"{(pn_s + f'{pn:.2f}x') if pn else '—'}{flag} | {(rp_s + f'{rp:.1f}x') if rp else '—'} | {five} | {meta} | {teto} |")
    out += ["", "⚠️ = PAM acima de 1,1x do nativo (prioridade 1 de otimização).", ""]
    errs = [f"- {a}/{sc}: {v['error']}" for a, d in apps.items() for sc, v in d.items()
            if isinstance(v, dict) and "error" in v]
    if errs:
        out += ["Falhas de cenário:", *errs, ""]
    return "\n".join(out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--candidate", help="raw.json of a PAM candidate run (same device)")
    ap.add_argument("--label", default="PAM cand.")
    a = ap.parse_args()
    raw = json.loads(Path(a.raw).read_text())
    cand = json.loads(Path(a.candidate).read_text()) if a.candidate else None
    md = render(raw, cand, a.label)
    if a.out:
        Path(a.out).write_text(md + "\n")
    print(md)
