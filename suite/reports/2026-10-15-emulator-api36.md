Dispositivo: sdk_gphone64_x86_64 Android 16 (API 36, x86_64, 60.0 Hz)

| Métrica | Nativo | PAM 1.43.0 | PAM 1.44.0-cand | RN | PAM/Nativo | RN/PAM | ≥5x | meta 20x | teto |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: | --- |
| Cold start TTID (mediana) (ms) | 353 | 368 | 391.50 | 416.50 | 1.11x ⚠️ | 1.1x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.2x) |
| Cold start até conteúdo (mediana) (ms) | 400 | 473.45 | 490.55 | 605.40 | 1.23x ⚠️ | 1.2x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.5x) |
| Lista 10k: tempo até conteúdo (ms) | 376 | 2 798.20 | 991.10 | 653.80 | 2.64x ⚠️ | 0.7x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.7x) |
| Lista 10k: frame p90 (ms) | 16 | 16 | 16 | 16 | 1.00x | 1.0x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.0x) |
| Lista 10k: frame p99 (ms) | 16 | 16 | 16 | 16 | 1.00x | 1.0x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.0x) |
| Lista 10k: jank (%) | 1.50 | 1.57 | 1.57 | 0.12 | 1.05x | 0.1x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 0.1x) |
| Lista 10k: CPU no scroll (ms) | 4 270 | 4 400 | 5 420 | 8 260 | 1.27x ⚠️ | 1.5x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.9x) |
| Lista 10k: PSS (KB) | 25 941 | 356 364 | 204 650 | 201 817 | 7.89x ⚠️ | 1.0x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 7.8x) |
| Grade 500 imgs: primeira imagem (ms) | 1 069.80 | 1 139.60 | 1 107.50 | 2 389.40 | 1.04x | 2.2x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 2.2x) |
| Grade 500 imgs: frame p99 (ms) | 109 | 89 | 97 | 16 | 0.89x | 0.2x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 0.1x) |
| Grade 500 imgs: jank (%) | 4.85 | 5.78 | 4.83 | 1.27 | 1.00x | 0.3x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 0.3x) |
| Grade 500 imgs: CPU (ms) | 9 940 | 18 300 | 19 410 | 6 220 | 1.95x ⚠️ | 0.3x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 0.6x) |
| Grade 500 imgs: PSS (KB) | 106 012 | 78 701 | 79 811 | 207 822 | 0.75x | 2.6x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 2.0x) |
| Curtir: toque→pixel (mediana) (ms) | 32.65 | 45.20 | 45.50 | 64.10 | 1.39x ⚠️ | 1.4x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 2.0x) |
| Curtir: CPU por toque (ms) | 0 | 20 | 20 | 30 | ≥2.00x ⚠️ | 1.5x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 3.0x) |
| Curtir: nós re-renderizados (nós) | 1 | — | — | 2 | — | — | — | físico | físico: nativo (máx RN/PAM ≈ 2.0x) |
| Filtro: tecla→pixel (mediana) (ms) | 33.80 | 73.50 | 70.50 | 49.10 | 2.09x ⚠️ | 0.7x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.5x) |
| Filtro: CPU por tecla (ms) | 10 | 20 | 20 | 30 | 2.00x ⚠️ | 1.5x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 3.0x) |
| Animação 60 s: CPU (ms) | 4 320 | 3 980 | 4 010 | 6 600 | 0.93x | 1.6x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.5x) |
| Animação 60 s: wakeups/min (/min) | 34 152.40 | 29 209.60 | 33 357.50 | 34 253.10 | 0.98x | 1.0x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.0x) |
| Ocioso 60 s: CPU (ms) | 10 | 10 | 10 | 480 | 1.00x | 48.0x | ✅ | ✅ atingida | ~0 (resolução 10 ms) |
| Ocioso 60 s: wakeups/min (/min) | 10 | 9 | 10.90 | 6 362.60 | 1.09x | 583.7x | ✅ | ✅ atingida | ~0 (resolução 1 /min) |
| Ocioso: PSS (KB) | 22 173 | 43 772 | 44 058 | 167 727 | 1.99x ⚠️ | 3.8x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 7.6x) |
| Ocioso: threads () | 19 | 22 | 21 | 30 | 1.11x ⚠️ | 1.4x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.6x) |
| Ocioso 10 min: CPU (ms) | 0 | 20 | 10 | 4 480 | ≥1.00x | 448.0x | ✅ | ✅ atingida | ~0 (resolução 10 ms) |
| Ocioso 10 min: wakeups/min (/min) | 0.80 | 0.80 | 1.30 | 4 513 | ≥1.30x ⚠️ | 3471.5x | ✅ | ✅ atingida | ~0 (resolução 1 /min) |
| Ocioso 10 min: mAh (batterystats) (mAh) | 4.4e-05 | — | 4e-05 | 0.0042 | 0.91x | 106.0x | ✅ | ✅ atingida | ~0 (resolução 1e-05 mAh) |
| Background 10 min: CPU (ms) | 20 | 50 | 60 | 890 | 3.00x ⚠️ | 14.8x | ✅ | alcançável | ~0 (resolução 10 ms) |
| Background 10 min: wakeups/min (/min) | 3.70 | 4 | 4.10 | 576.20 | 1.11x ⚠️ | 140.5x | ✅ | ✅ atingida | ~0 (resolução 1 /min) |
| Nav 20 telas: crescimento PSS (ciclo 1→3) (KB) | 222 | 5 158 | 2 958 | 16 274 | ≥11.55x ⚠️ | 5.5x | ✅ | alcançável | ~0 (resolução 256 KB) |
| Nav 20 telas: PSS no pico (KB) | 47 080 | 78 186 | 78 020 | 275 674 | 1.66x ⚠️ | 3.5x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 5.9x) |
| Nav: toque→tela (mediana) (ms) | 28 | 11 | 11 | 51.50 | 0.39x | 4.7x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.8x) |
| Vídeo 60 s: CPU do app (ms) | 2 730 | 3 980 | 4 100 | 3 150 | 1.50x ⚠️ | 0.8x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.2x) |
| Vídeo 60 s: CPU do codec (%) | 5.80 | 7.10 | 7.10 | 5.80 | 1.22x ⚠️ | 0.8x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.0x) |
| Vídeo 60 s: wakeups/min (/min) | 43 303 | 28 445.90 | 30 095.80 | 47 362.10 | 0.70x | 1.6x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 1.1x) |
| Tamanho do APK (x86_64) (B) | 1 160 060 | 15 637 927 | 15 638 147 | 32 190 074 | 13.48x ⚠️ | 2.1x | ❌ | alcançável | físico: nativo (máx RN/PAM ≈ 27.7x) |
| Reabrir com cache: bytes de rede (B) | 0 | 0 | 0 | 0 | ≥1.00x | ≥1.0x | ❌ | alcançável | ~0 (resolução 100 B) |
| Reabrir com cache: tempo até conteúdo (ms) | 856.10 | 1 064.90 | 1 022.50 | 745 | 1.19x ⚠️ | 0.7x | ❌ | físico | físico: nativo (máx RN/PAM ≈ 0.9x) |
| Estado 100k registros: memória (KB) | 22 461 | 76 708 | 76 507 | 27 192 | 3.41x | 0.4x | ❌ | alcançável | algorítmico (pode superar o nativo) |
| Busca 100k: preparar (ms) | 80.36 | 3.86 | 3.54 | 247.29 | 0.04x | 70.0x | ✅ | ✅ atingida | algorítmico (pode superar o nativo) |
| Busca 100k: 100 consultas (ms) | 654 | 471.42 | 438.96 | 2 121.26 | 0.67x | 4.8x | ❌ | alcançável | algorítmico (pode superar o nativo) |
| JSON 5 MB: parse (ms) | 61.52 | 26.99 | 26.59 | 42.34 | 0.43x | 1.6x | ❌ | alcançável | algorítmico (pode superar o nativo) |
| JSON 5 MB: serializar (ms) | 100.01 | 23.02 | 22.90 | 291.68 | 0.23x | 12.7x | ✅ | alcançável | algorítmico (pode superar o nativo) |
| Ordenar 100k (ms) | 92.99 | 237.00 | 238.37 | 216.27 | 2.56x | 0.9x | ❌ | alcançável | algorítmico (pode superar o nativo) |
| SHA-256 10 MiB (ms) | 23.89 | 26.31 | 26.43 | 1 436.39 | 1.11x | 54.3x | ✅ | ✅ atingida | algorítmico (pode superar o nativo) |
| Diff de listas 100k (ms) | 5.97 | 12.99 | 13.18 | 17.11 | 2.21x | 1.3x | ❌ | alcançável | algorítmico (pode superar o nativo) |

⚠️ = PAM acima de 1,1x do nativo (prioridade 1 de otimização).

