"""Self-made figures for the "hearing frequency" post, rendered in Chinese and English.

  fig10  auditory-filter bandwidth: Zwicker CB vs Glasberg & Moore ERB
  fig11  (a) ERB vs STFT vs 1/3-octave bandwidth, (b) gammatone impulse responses
  fig12  temporal integration of loudness (equal-Leq noise bursts + energy-integrator sketch)
  fig16  beats vs roughness: compressed envelope at the output of a 500 Hz gammatone filter

Usage:  python3 make_figs.py      (needs numpy, matplotlib and the Noto Sans CJK SC font)
Writes figs/figNN_<name>-zh.png and figs/figNN_<name>-en.png next to this script.
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parent / "figs"

INK = "#0b0b0b"
TXT2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
BLUE_DARK = "#1c5cab"
BAND = "#cde2fb"

T = {
    "zh": {
        "f10_x": "中心频率 (Hz)", "f10_y": "带宽 (Hz)",
        "f10_cb": "临界频带 CB (Zwicker & Terhardt, 1980)",
        "f10_erb": "等效矩形带宽 ERB (Glasberg & Moore, 1990)",
        "f11a_title": "(a) 滤波器带宽随中心频率的变化",
        "f11_x": "中心频率 (Hz)", "f11_y": "带宽 B (Hz)", "f11_y2": "≈ 时间窗 1/B (ms)",
        "f11_erb": "人耳听觉滤波器 (ERB)", "f11_cq": "1/3 倍频程 (常数 Q)", "f11_stft": "STFT (20 ms 汉宁窗)",
        "f11_lbl_erb": "人耳 ERB", "f11_lbl_cq": "1/3 倍频程",
        "f11_low": "低频: ERB 变化慢 → 接近 STFT",
        "f11_high": "高频: ERB ∝ 频率 (Q ≈ 8–9)\n→ 接近常数 Q / 小波",
        "f11b_title": "(b) 各中心频率处听觉滤波器的冲激响应",
        "f11b_sub": "4 阶 gammatone, 带宽 1.019×ERB · 浅蓝底: 包络高于峰值 10% 的时段 · 虚线: 包络",
        "f11_dur": "有效时长", "time_ms": "时间 (ms)",
        "f12a_title": "(a) 等效声级相同、时长不同的白噪声",
        "f12b_title": "(b) 能量积分示意 (τ = 100 ms)",
        "f12b_x": "持续时间 (ms)", "f12b_y": "相对响度级 (dB)",
        "f12b_note": "短于 τ 时, 时长每增加 10 倍\n响度级约增加 10 dB",
        "f16_title_l": "500 Hz + 503 Hz:差频 3 Hz", "f16_title_r": "500 Hz + 540 Hz:差频 40 Hz",
        "f16_y": "包络 (压缩后, 相对值)",
        "f16_note": "简化模型: 500 Hz 处 4 阶 gammatone 滤波器输出的包络, 取 0.3 次方压缩",
    },
    "en": {
        "f10_x": "Centre frequency (Hz)", "f10_y": "Bandwidth (Hz)",
        "f10_cb": "Critical band, CB (Zwicker & Terhardt, 1980)",
        "f10_erb": "Equivalent rectangular bandwidth, ERB (Glasberg & Moore, 1990)",
        "f11a_title": "(a) Filter bandwidth vs centre frequency",
        "f11_x": "Centre frequency (Hz)", "f11_y": "Bandwidth B (Hz)", "f11_y2": "≈ time window 1/B (ms)",
        "f11_erb": "Auditory filter (ERB)", "f11_cq": "1/3 octave (constant Q)", "f11_stft": "STFT (20 ms Hann)",
        "f11_lbl_erb": "ERB", "f11_lbl_cq": "1/3 octave",
        "f11_low": "Low f: close to STFT",
        "f11_high": "High f: ERB ∝ f (Q ≈ 8–9)\n→ close to constant-Q",
        "f11b_title": "(b) Impulse responses of auditory filters",
        "f11b_sub": "4th-order gammatone, bandwidth 1.019×ERB · shaded: envelope > 10% of peak · dashed: envelope",
        "f11_dur": "duration", "time_ms": "Time (ms)",
        "f12a_title": "(a) White-noise bursts with equal Leq",
        "f12b_title": "(b) Energy-integration sketch (τ = 100 ms)",
        "f12b_x": "Duration (ms)", "f12b_y": "Relative loudness level (dB)",
        "f12b_note": "Below τ, loudness level rises\nby about 10 dB per decade",
        "f16_title_l": "500 Hz + 503 Hz: 3 Hz difference", "f16_title_r": "500 Hz + 540 Hz: 40 Hz difference",
        "f16_y": "Envelope (compressed, rel.)",
        "f16_note": "Simplified model: envelope at the output of a 4th-order gammatone filter at 500 Hz, raised to the power 0.3",
    },
}


def setup(lang):
    plt.rcParams.update({
        "font.family": ["Noto Sans CJK SC"] if lang == "zh" else ["Helvetica Neue", "Arial Unicode MS"],
        "font.size": 15,
        "axes.unicode_minus": False,
        "axes.edgecolor": "#8a8984",
        "axes.linewidth": 1.0,
        "xtick.color": TXT2,
        "ytick.color": TXT2,
        "axes.labelcolor": INK,
        "text.color": INK,
    })


def erb(f_hz):
    """Glasberg & Moore (1990) equivalent rectangular bandwidth, Hz."""
    return 24.7 * (4.37 * f_hz / 1000.0 + 1.0)


def cb(f_hz):
    """Zwicker & Terhardt (1980) critical bandwidth, Hz."""
    return 25 + 75 * (1 + 1.4 * (f_hz / 1000.0) ** 2) ** 0.69


def hz_label(v):
    return f"{v/1000:g} kHz" if v >= 1000 else f"{v:g} Hz"


def hz_tick(v, _):
    return f"{v/1000:g}k" if v >= 1000 else f"{v:g}"


def gammatone(cf, fs, dur, n=4):
    t = np.arange(0, dur, 1 / fs)
    b = 1.019 * erb(cf)
    env = t ** (n - 1) * np.exp(-2 * np.pi * b * t)
    tp = (n - 1) / (2 * np.pi * b)
    env = env / (tp ** (n - 1) * np.exp(-2 * np.pi * b * tp))
    return t, env, env * np.cos(2 * np.pi * cf * t)


def style_log_axes(ax, xticks, yticks):
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(hz_tick))
    ax.yaxis.set_major_locator(FixedLocator(yticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def fig10(lang):
    s = T[lang]
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    f = np.logspace(np.log10(50), np.log10(16000), 500)
    ax.plot(f, cb(f), color=ORANGE, lw=2.6, label=s["f10_cb"])
    ax.plot(f, erb(f), color=BLUE, lw=3.0, label=s["f10_erb"])
    ax.set_xlim(50, 16000)
    ax.set_ylim(20, 5000)
    style_log_axes(ax, [50, 100, 200, 500, 1000, 2000, 5000, 10000],
                   [20, 50, 100, 200, 500, 1000, 2000, 5000])
    ax.set_xlabel(s["f10_x"])
    ax.set_ylabel(s["f10_y"])
    ax.legend(loc="upper left", fontsize=11.5, frameon=True, framealpha=1.0, edgecolor=GRID)
    ax.text(15000, 30, "CB = 25 + 75 [1 + 1.4 f²]$^{0.69}$\nERB = 24.7 (4.37 f + 1)      (f in kHz)",
            fontsize=11, color=TXT2, ha="right", va="bottom")
    fig.tight_layout()
    fig.savefig(OUT / f"fig10_cb_erb-{lang}.png", facecolor="white")
    plt.close(fig)


def fig11(lang):
    s = T[lang]
    fig = plt.figure(figsize=(7.2, 10.4), dpi=200)

    ax = fig.add_axes([0.125, 0.615, 0.715, 0.335])
    f = np.logspace(np.log10(50), np.log10(16000), 500)
    stft_bw = np.full_like(f, 1.5 / 0.020)       # Hann ENBW = 1.5 / T -> 75 Hz
    cq_bw = f * (2 ** (1 / 6) - 2 ** (-1 / 6))   # 1/3 octave, ~23 % of f
    ax.plot(f, stft_bw, color=ORANGE, lw=2.4, solid_capstyle="round", zorder=3)
    ax.plot(f, cq_bw, color=AQUA, lw=2.4, solid_capstyle="round", zorder=3)
    ax.plot(f, erb(f), color=BLUE, lw=3.4, solid_capstyle="round", zorder=4)
    ax.set_xlim(50, 16000)
    ax.set_ylim(10, 5000)
    style_log_axes(ax, [50, 100, 200, 500, 1000, 2000, 5000, 10000],
                   [10, 20, 50, 100, 200, 500, 1000, 2000, 5000])
    ax.spines["right"].set_visible(True)
    ax.set_xlabel(s["f11_x"])
    ax.set_ylabel(s["f11_y"])
    ax.set_title(s["f11a_title"], loc="left", fontsize=16, pad=10)

    with np.errstate(divide="ignore"):
        sec = ax.secondary_yaxis("right", functions=(lambda b: 1000.0 / b, lambda t: 1000.0 / t))
    sec.yaxis.set_major_locator(FixedLocator([100, 50, 20, 10, 5, 2, 1, 0.5, 0.2]))
    sec.yaxis.set_minor_locator(NullLocator())
    sec.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    sec.set_ylabel(s["f11_y2"], color=TXT2)
    sec.tick_params(colors=TXT2)

    handles = [Line2D([], [], color=BLUE, lw=3.4, label=s["f11_erb"]),
               Line2D([], [], color=AQUA, lw=2.4, label=s["f11_cq"]),
               Line2D([], [], color=ORANGE, lw=2.4, label=s["f11_stft"])]
    ax.legend(handles=handles, loc="upper left", fontsize=12, frameon=True, framealpha=1.0,
              edgecolor=GRID, borderpad=0.6, handlelength=1.8)
    ax.text(2300, 190, s["f11_lbl_erb"], fontsize=13, color=INK, va="center")
    ax.text(330, 520, s["f11_lbl_cq"], fontsize=13, color=INK, va="center")
    ax.text(56, 92, "STFT", fontsize=13, color=INK, va="bottom")
    ax.text(135 if lang == "zh" else 105, 12.5, s["f11_low"], fontsize=12 if lang == "zh" else 11,
            color=TXT2, va="bottom")
    ax.text(15000, 12.5, s["f11_high"], fontsize=12 if lang == "zh" else 11, color=TXT2,
            ha="right", va="bottom")

    bx = fig.add_axes([0.06, 0.07, 0.62, 0.37])
    fs = 200_000
    for k, cf in enumerate([125, 500, 2000, 8000]):
        t, env, g = gammatone(cf, fs, 0.040)
        y0 = k * 1.35
        above = np.where(env >= 0.1)[0]
        t_on, t_off = t[above[0]] * 1e3, t[above[-1]] * 1e3
        bx.fill_between([t_on, t_off], y0 - 0.6, y0 + 0.6, color=BAND, lw=0, zorder=0)
        bx.plot(t * 1e3, y0 + 0.55 * g, color=BLUE_DARK, lw=0.9, zorder=2)
        bx.plot(t * 1e3, y0 + 0.55 * env, color=TXT2, lw=1.2, ls=(0, (3, 2)), zorder=3)
        bx.annotate(f"CF = {hz_label(cf)}\nERB ≈ {erb(cf):.0f} Hz\n{s['f11_dur']} ≈ {t_off - t_on:.1f} ms",
                    xy=(1.035, y0), xycoords=("axes fraction", "data"), fontsize=12.5,
                    va="center", ha="left", color=INK, annotation_clip=False)
    bx.set_xlim(0, 40)
    bx.set_ylim(-0.75, 3 * 1.35 + 0.75)
    bx.set_yticks([])
    bx.set_xlabel(s["time_ms"])
    for side in ("top", "right", "left"):
        bx.spines[side].set_visible(False)
    bx.grid(True, axis="x", color=GRID, lw=0.8)
    bx.set_axisbelow(True)
    bx.set_title(s["f11b_title"], loc="left", fontsize=16, pad=30)
    bx.text(0, 1.035, s["f11b_sub"], transform=bx.transAxes, fontsize=10.5 if lang == "zh" else 9.2,
            color=TXT2, va="bottom")

    fig.savefig(OUT / f"fig11_gammatone-{lang}.png", facecolor="white")
    plt.close(fig)


def fig12(lang):
    s = T[lang]
    rng = np.random.default_rng(1)
    fs = 8000
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=200,
                                 gridspec_kw={"width_ratios": [1.25, 1]})

    durs = [6, 25, 100, 400]
    for k, d in enumerate(durs):
        n = int(fs * d / 1000)
        x = rng.standard_normal(n)
        x /= np.sqrt(np.mean(x ** 2))            # same RMS -> same Leq over the burst
        t = np.arange(n) / fs * 1000 + 20
        y0 = (len(durs) - 1 - k) * 1.0
        ax.plot(t, y0 + 0.11 * x, color=BLUE_DARK, lw=0.5)
        ax.text(10, y0, f"{d} ms", ha="right", va="center", fontsize=12, color=INK)
    ax.set_xlim(-40, 440)
    ax.set_ylim(-0.6, 3.6)
    ax.set_yticks([])
    ax.set_xticks([20, 120, 220, 320, 420])
    ax.set_xticklabels(["0", "100", "200", "300", "400"])
    ax.set_xlabel(s["time_ms"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_title(s["f12a_title"], loc="left", fontsize=14, pad=10)

    tau = 100.0
    d = np.logspace(np.log10(3), np.log10(1000), 300)
    rel = 10 * np.log10(1 - np.exp(-d / tau))
    bx.plot(d, rel, color=BLUE, lw=3)
    bx.axvline(tau, color=TXT2, lw=1, ls=(0, (3, 2)))
    bx.text(tau * 1.08, -22, "τ", color=TXT2, fontsize=13)
    bx.set_xscale("log")
    bx.xaxis.set_major_locator(FixedLocator([5, 10, 20, 50, 100, 200, 500, 1000]))
    bx.xaxis.set_minor_locator(NullLocator())
    bx.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    bx.set_ylim(-25, 2)
    bx.set_xlabel(s["f12b_x"])
    bx.set_ylabel(s["f12b_y"])
    bx.grid(True, color=GRID, lw=0.8)
    bx.set_axisbelow(True)
    bx.spines["top"].set_visible(False)
    bx.spines["right"].set_visible(False)
    bx.text(85, -21, s["f12b_note"], fontsize=11, color=TXT2, ha="right")
    bx.set_title(s["f12b_title"], loc="left", fontsize=14, pad=10)

    fig.tight_layout()
    fig.savefig(OUT / f"fig12_temporal_integration-{lang}.png", facecolor="white")
    plt.close(fig)


def fig16(lang):
    s = T[lang]
    fs = 16000
    dur = 1.0
    t = np.arange(0, dur, 1 / fs)
    _, _, g = gammatone(500, fs, 0.05)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), dpi=200, sharey=True)
    for ax, f2, title in zip(axes, (503, 540), (s["f16_title_l"], s["f16_title_r"])):
        x = np.sin(2 * np.pi * 500 * t) + np.sin(2 * np.pi * f2 * t)
        y = np.convolve(x, g)[: len(t)]
        spec = np.fft.fft(y)
        h = np.zeros(len(y))
        h[0] = 1
        h[1: len(y) // 2] = 2
        if len(y) % 2 == 0:
            h[len(y) // 2] = 1
        env = np.abs(np.fft.ifft(spec * h)) ** 0.3
        env /= env.max()
        ax.plot(t * 1000, env, color=BLUE_DARK, lw=1.1)
        ax.set_xlim(0, 960)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel(s["time_ms"])
        ax.set_title(title, loc="left", fontsize=13.5, pad=8)
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].set_ylabel(s["f16_y"])
    fig.text(0.5, 0.01, s["f16_note"], ha="center", va="bottom", fontsize=10.5, color=TXT2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / f"fig16_beats_roughness-{lang}.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for lang in ("zh", "en"):
        setup(lang)
        fig10(lang)
        fig11(lang)
        fig12(lang)
        fig16(lang)
    print("saved to", OUT)
