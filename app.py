import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib as mpl

mpl.rcParams['font.size'] = 10

# ─────────────────────────────────────────────
# VÝPOČET FÁZOVÉHO POSUNU
# ─────────────────────────────────────────────
def vypocti_fazovy_posun(pouzito_R, pouzito_L, pouzito_C, prevazuje, obvod_typ):
    """
    Sériový obvod: řídící fázor = I (vodorovně)
      - cívka L:  U_L předbíhá I o 90° → φ = +90° (nebo +60° s R)
      - kondenz C: U_C zaostává za I o 90° → φ = -90° (nebo -60° s R)
    Paralelní obvod: řídící fázor = U (vodorovně)
      - cívka L:  I_L zaostává za U o 90° → φ = -90° (nebo -60° s R)
      - kondenz C: I_C předbíhá U o 90° → φ = +90° (nebo +60° s R)
    Vrací φ = úhel proudu vůči napětí (kladný = proud předbíhá napětí).
    """
    if not pouzito_L and not pouzito_C:
        return 0  # jen R nebo nic

    if pouzito_L and pouzito_C:
        if prevazuje == "Cívka (L)":
            return -60   # induktivní charakter → proud zaostává
        elif prevazuje == "Kondenzátor (C)":
            return 60    # kapacitní charakter → proud předbíhá
        else:
            return 0     # rezonance

    if obvod_typ == "Sériový":
        if pouzito_L:
            return -90 if not pouzito_R else -60
        if pouzito_C:
            return 90 if not pouzito_R else 60
    else:  # Paralelní
        if pouzito_L:
            return -90 if not pouzito_R else -60
        if pouzito_C:
            return 90 if not pouzito_R else 60
    return 0


# ─────────────────────────────────────────────
# SCHÉMATICKÁ ZNAČKA CÍVKY (sinusoida)
# ─────────────────────────────────────────────
def nakresli_civku_serie(ax, x_start, x_end, y, barva='black'):
    """Nakreslí cívku jako sérii půloblouků pro sériové zapojení (vodorovně)."""
    pocet_obluku = 4
    sirka = x_end - x_start
    t = np.linspace(0, pocet_obluku * np.pi, 200)
    x_civka = x_start + (t / (pocet_obluku * np.pi)) * sirka
    y_civka = y + 0.35 * np.abs(np.sin(t))
    ax.plot(x_civka, y_civka, color=barva, lw=2)

def nakresli_civku_paralel(ax, x, y_start, y_end, barva='black'):
    """Nakreslí cívku jako sérii půloblouků pro paralelní zapojení (svisle)."""
    pocet_obluku = 4
    vyska = y_end - y_start
    t = np.linspace(0, pocet_obluku * np.pi, 200)
    y_civka = y_start + (t / (pocet_obluku * np.pi)) * vyska
    x_civka = x + 0.35 * np.abs(np.sin(t))
    ax.plot(x_civka, y_civka, color=barva, lw=2)


# ─────────────────────────────────────────────
# SCHÉMA OBVODU
# ─────────────────────────────────────────────
def nakresli_obvod(pouzito_R, pouzito_L, pouzito_C, obvod_typ):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # ── Napěťový zdroj (levá strana, vždy stejný) ──
    # Svislá čára zdroje
    ax.plot([1, 1], [1, 5], 'k-', lw=2)
    # Značka + a -
    ax.plot([0.65, 1.35], [3.3, 3.3], 'k-', lw=2)   # + vodorovná
    ax.plot([1.0, 1.0],   [3.1, 3.5], 'k-', lw=2)   # + svislá
    ax.plot([0.65, 1.35], [2.7, 2.7], 'k-', lw=1.5) # - vodorovná
    ax.text(0.15, 3.0, "U", fontsize=14, weight='bold', color='black')

    komponenty = []
    if pouzito_R:
        komponenty.append('R')
    if pouzito_L:
        komponenty.append('L')
    if pouzito_C:
        komponenty.append('C')
    pocet = len(komponenty)

    # ════════════════════════════════════════════
    # SÉRIOVÉ ZAPOJENÍ
    # ════════════════════════════════════════════
    if obvod_typ == "Sériový":
        # Horní vodič: zdroj → komponenty → zpět
        ax.plot([1, 9], [5, 5], 'k-', lw=2)   # horní
        ax.plot([1, 9], [1, 1], 'k-', lw=2)   # dolní
        ax.plot([9, 9], [1, 5], 'k-', lw=2)   # pravá svislá

        if pocet == 0:
            return fig

        # Rozmístění komponent rovnoměrně na horním vodiči
        x_start = 2.0
        x_end   = 8.5
        sirka_komp = 1.4
        mezery_celkem = x_end - x_start - pocet * sirka_komp
        mezera = mezery_celkem / (pocet + 1)

        for idx, komp in enumerate(komponenty):
            x_l = x_start + mezera * (idx + 1) + sirka_komp * idx  # levý okraj součástky
            x_r = x_l + sirka_komp                                   # pravý okraj
            xc  = (x_l + x_r) / 2                                   # střed

            if komp == 'R':
                # Obdélník rezistoru
                ax.add_patch(Rectangle((x_l, 4.3), sirka_komp, 1.4,
                                       fill=True, facecolor='#ffe0b2',
                                       edgecolor='black', lw=2))
                ax.text(xc, 5.0, "R", ha='center', va='center',
                        fontsize=13, weight='bold')

            elif komp == 'L':
                # Sinusoidální značka cívky
                nakresli_civku_serie(ax, x_l, x_r, 4.6)
                ax.text(xc, 4.2, "L", ha='center', va='top',
                        fontsize=13, weight='bold')

            elif komp == 'C':
                # Dvě svislé čáry kondenzátoru (přerušení vodiče)
                ax.plot([x_l, xc - 0.15], [5, 5], 'k-', lw=2)
                ax.plot([xc + 0.15, x_r], [5, 5], 'k-', lw=2)
                ax.plot([xc - 0.15, xc - 0.15], [4.4, 5.6], 'k-', lw=3)
                ax.plot([xc + 0.15, xc + 0.15], [4.4, 5.6], 'k-', lw=3)
                ax.text(xc, 4.2, "C", ha='center', va='top',
                        fontsize=13, weight='bold')

    # ════════════════════════════════════════════
    # PARALELNÍ ZAPOJENÍ
    # ════════════════════════════════════════════
    else:
        # Hlavní smyčka: zdroj vlevo, uzavření vpravo
        ax.plot([1, 9], [5, 5], 'k-', lw=2)   # horní vodič
        ax.plot([1, 9], [1, 1], 'k-', lw=2)   # dolní vodič
        ax.plot([9, 9], [1, 5], 'k-', lw=2)   # pravá svislá

        if pocet == 0:
            return fig

        # Rozmístění větví rovnoměrně mezi x=2.5 a x=8.5
        x_start = 2.5
        x_end   = 8.0
        if pocet == 1:
            pozice_x = [(x_start + x_end) / 2]
        else:
            krok_x = (x_end - x_start) / (pocet - 1)
            pozice_x = [x_start + i * krok_x for i in range(pocet)]

        for idx, komp in enumerate(komponenty):
            xc = pozice_x[idx]   # střed větve

            # Svislé dráty k součástce (shora a zdola)
            ax.plot([xc, xc], [5, 4.0], 'k-', lw=2)   # shora dolů k součástce
            ax.plot([xc, xc], [2.0, 1], 'k-', lw=2)   # od součástky dolů

            if komp == 'R':
                ax.add_patch(Rectangle((xc - 0.5, 2.0), 1.0, 2.0,
                                       fill=True, facecolor='#ffe0b2',
                                       edgecolor='black', lw=2))
                ax.text(xc, 3.0, "R", ha='center', va='center',
                        fontsize=13, weight='bold')

            elif komp == 'L':
                # Svislá sinusoidální cívka
                nakresli_civku_paralel(ax, xc - 0.35, 2.0, 4.0)
                ax.text(xc + 0.55, 3.0, "L", ha='center', va='center',
                        fontsize=13, weight='bold')

            elif komp == 'C':
                # Dvě vodorovné čáry kondenzátoru (přerušení svislého vodiče)
                ax.plot([xc, xc], [4.0, 3.2], 'k-', lw=2)
                ax.plot([xc, xc], [2.8, 2.0], 'k-', lw=2)
                ax.plot([xc - 0.45, xc + 0.45], [3.2, 3.2], 'k-', lw=3)
                ax.plot([xc - 0.45, xc + 0.45], [2.8, 2.8], 'k-', lw=3)
                ax.text(xc + 0.6, 3.0, "C", ha='center', va='center',
                        fontsize=13, weight='bold')

    return fig


# ─────────────────────────────────────────────
# FÁZOROVÝ DIAGRAM
# ─────────────────────────────────────────────
def nakresli_fazorovy_diagram(phi, pouzito_R, pouzito_L, pouzito_C, prevazuje, obvod_typ):
    fig, ax = plt.subplots(figsize=(5, 5))

    ax.axhline(0, color='gray', lw=0.8, linestyle='--')
    ax.axvline(0, color='gray', lw=0.8, linestyle='--')

     # ── délky fázorů (normalizované pro kresbu) ──────────────────────
    L_ref  = 0.7   # referenční fázor (I nebo U)
    L_R    = 0.6   # odporová složka

    # Pro RLC: větší složka dostane plnou délku, menší dostane polovinu
    # Výsledná reaktanční složka = rozdíl (vizuálně sedí)
    if pouzito_L and pouzito_C:
        L_vetsi = 0.65
        L_mensi = L_vetsi * 0.5   # ~polovina

        if "Cívka" in prevazuje:
            L_L    = L_vetsi
            L_C    = L_mensi
        elif "Kondenzátor" in prevazuje:
            L_L    = L_mensi
            L_C    = L_vetsi
        else:
            # rezonance — stejně dlouhé, výsledek = 0
            L_L    = 0.65
            L_C    = 0.65

        L_reak = abs(L_L - L_C)   # výsledná reaktanční složka = rozdíl délek

        if "Cívka" in prevazuje:
            smer_reak = +1 if obvod_typ == "Sériový" else -1
        elif "Kondenzátor" in prevazuje:
            smer_reak = -1 if obvod_typ == "Sériový" else +1
        else:
            smer_reak = 0

    elif pouzito_L:
        L_L    = 0.65
        L_C    = 0.0
        L_reak = L_L
        smer_reak = +1 if obvod_typ == "Sériový" else -1

    elif pouzito_C:
        L_L    = 0.0
        L_C    = 0.65
        L_reak = L_C
        smer_reak = -1 if obvod_typ == "Sériový" else +1

    else:
        L_L    = 0.0
        L_C    = 0.0
        L_reak = 0.0
        smer_reak = 0

    def sipka(ax, x0, y0, x1, y1, barva, tloustka=2, styl='-'):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(
                        arrowstyle='->', color=barva, lw=tloustka,
                        linestyle=styl
                    ))

    def carkovana_rovnobezka(ax, x0, y0, x1, y1, barva='gray'):
        ax.plot([x0, x1], [y0, y1], color=barva, lw=1, linestyle='dotted')

    # ══════════════════════════════════════════════════════════════════
    if obvod_typ == "Sériový":
    # ══════════════════════════════════════════════════════════════════
        # Referenční fázor I — vodorovně vpravo (červeně)
        sipka(ax, 0, 0, L_ref, 0, 'red', tloustka=2.5)
        ax.text(L_ref + 0.05, 0.05, 'I', color='red', fontsize=13, weight='bold')

        if pouzito_R and not pouzito_L and not pouzito_C:
            # ── jen R ──────────────────────────────────────────────
            # U_R = U, vodorovně, φ = 0
            sipka(ax, 0, 0, L_R, 0, 'blue', tloustka=2.5)
            ax.text(L_R / 2, 0.1, 'U = U_R', color='blue', fontsize=11,
                    ha='center', weight='bold')

        elif not pouzito_R and pouzito_L and not pouzito_C:
            # ── jen L ──────────────────────────────────────────────
            # U_L nahoru, φ = +90°
            sipka(ax, 0, 0, 0, L_L, 'blue', tloustka=2.5)
            ax.text(0.08, L_L + 0.05, 'U = U_L', color='blue', fontsize=11,
                    weight='bold')
            # oblouček φ od I (vpravo) k U (nahoru)
            uhly = np.linspace(0, np.pi / 2, 60)
            ax.plot(0.25 * np.cos(uhly), 0.25 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.08, 0.3, 'φ=90°', color='green', fontsize=10, weight='bold')

        elif not pouzito_R and not pouzito_L and pouzito_C:
            # ── jen C ──────────────────────────────────────────────
            # U_C dolů, φ = -90°
            sipka(ax, 0, 0, 0, -L_C, 'blue', tloustka=2.5)
            ax.text(0.08, -L_C - 0.1, 'U = U_C', color='blue', fontsize=11,
                    weight='bold')
            # oblouček φ od I (vpravo) k U (dolů) — záporný směr
            uhly = np.linspace(0, -np.pi / 2, 60)
            ax.plot(0.25 * np.cos(uhly), 0.25 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.08, -0.32, 'φ=-90°', color='green', fontsize=10, weight='bold')

        elif pouzito_R and pouzito_L and not pouzito_C:
            # ── RL ─────────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, '#1565C0', tloustka=1.8, styl='dashed')
            ax.text(L_R / 2, -0.12, 'U_R', color='#1565C0', fontsize=10,
                    ha='center', weight='bold')
            sipka(ax, 0, 0, 0, L_L, '#1976D2', tloustka=1.8)
            ax.text(0.07, L_L / 2, 'U_L', color='#1976D2', fontsize=10,
                    weight='bold')
            # výsledné U — rovnoběžník: čárkované doplnění
            carkovana_rovnobezka(ax, L_R, 0, L_R, L_L)   # svislá od konce U_R
            carkovana_rovnobezka(ax, 0, L_L, L_R, L_L)   # vodorovná od konce U_L
            sipka(ax, 0, 0, L_R, L_L, 'blue', tloustka=3)
            ax.text(L_R + 0.06, L_L + 0.05, 'U', color='blue', fontsize=13,
                    weight='bold')
            # oblouček φ od I k U
            phi_rad = np.arctan2(L_L, L_R)
            uhly = np.linspace(0, phi_rad, 60)
            ax.plot(0.28 * np.cos(uhly), 0.28 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.22 * np.cos(phi_rad / 2) + 0.05,
                    0.22 * np.sin(phi_rad / 2) + 0.05,
                    f'φ={phi}°', color='green', fontsize=10, weight='bold')

        elif pouzito_R and not pouzito_L and pouzito_C:
            # ── RC ─────────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, '#1565C0', tloustka=1.8, styl='dashed')
            ax.text(L_R / 2, 0.1, 'U_R', color='#1565C0', fontsize=10,
                    ha='center', weight='bold')
            sipka(ax, 0, 0, 0, -L_C, '#0D47A1', tloustka=1.8)
            ax.text(0.07, -L_C / 2, 'U_C', color='#0D47A1', fontsize=10,
                    weight='bold')
            # výsledné U — rovnoběžník
            carkovana_rovnobezka(ax, L_R, 0, L_R, -L_C)
            carkovana_rovnobezka(ax, 0, -L_C, L_R, -L_C)
            sipka(ax, 0, 0, L_R, -L_C, 'blue', tloustka=3)
            ax.text(L_R + 0.06, -L_C - 0.08, 'U', color='blue', fontsize=13,
                    weight='bold')
            # oblouček φ od I k U (záporný úhel)
            phi_rad = np.arctan2(-L_C, L_R)
            uhly = np.linspace(0, phi_rad, 60)
            ax.plot(0.28 * np.cos(uhly), 0.28 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.22 * np.cos(phi_rad / 2) + 0.05,
                    0.22 * np.sin(phi_rad / 2) - 0.08,
                    f'φ={phi}°', color='green', fontsize=10, weight='bold')

        elif not pouzito_R and pouzito_L and pouzito_C:
            # ── LC bez R ───────────────────────────────────────────
            sipka(ax, 0, 0, 0, L_L, '#1976D2', tloustka=1.8)
            ax.text(0.07, L_L / 2, 'U_L', color='#1976D2', fontsize=10,
                    weight='bold')
            sipka(ax, 0, 0, 0, -L_C, '#0D47A1', tloustka=1.8)
            ax.text(0.07, -L_C / 2, 'U_C', color='#0D47A1', fontsize=10,
                    weight='bold')
            # výsledný fázor — svisle, délka = rozdíl
            vy = smer_reak * L_reak
            sipka(ax, 0, 0, 0, vy, 'blue', tloustka=3)
            ax.text(0.08, vy + 0.05 * smer_reak, 'U', color='blue', fontsize=13,
                    weight='bold')
            phi_label = "+90°" if vy > 0 else "-90°"
            uhly = np.linspace(0, np.pi / 2 * smer_reak, 60)
            ax.plot(0.25 * np.cos(uhly), 0.25 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.08, 0.3 * smer_reak, f'φ={phi_label}', color='green',
                    fontsize=10, weight='bold')

        else:
            # ── RLC ────────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, '#1565C0', tloustka=1.8, styl='dashed')
            ax.text(L_R / 2, -0.12, 'U_R', color='#1565C0', fontsize=10,
                    ha='center', weight='bold')
            sipka(ax, 0, 0, 0, L_L, '#1976D2', tloustka=1.8)
            ax.text(0.07, L_L / 2, 'U_L', color='#1976D2', fontsize=10,
                    weight='bold')
            sipka(ax, 0, 0, 0, -L_C, '#0D47A1', tloustka=1.8)
            ax.text(0.07, -L_C / 2, 'U_C', color='#0D47A1', fontsize=10,
                    weight='bold')
            # výsledná reaktanční složka
            vy = smer_reak * L_reak
            # rovnoběžník: U_R + výsledná reaktance → U
            carkovana_rovnobezka(ax, L_R, 0, L_R, vy)
            carkovana_rovnobezka(ax, 0, vy, L_R, vy)
            sipka(ax, 0, 0, L_R, vy, 'blue', tloustka=3)
            ax.text(L_R + 0.06, vy + 0.05 * smer_reak, 'U', color='blue',
                    fontsize=13, weight='bold')
            # oblouček φ od I k U
            phi_rad = np.arctan2(vy, L_R)
            uhly = np.linspace(0, phi_rad, 60)
            ax.plot(0.28 * np.cos(uhly), 0.28 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.22 * np.cos(phi_rad / 2) + 0.05,
                    0.22 * np.sin(phi_rad / 2) + 0.05 * smer_reak,
                    f'φ={phi}°', color='green', fontsize=10, weight='bold')

    # ══════════════════════════════════════════════════════════════════
    else:  # Paralelní
    # ══════════════════════════════════════════════════════════════════
        # Referenční fázor U — vodorovně vpravo (modře)
        sipka(ax, 0, 0, L_ref, 0, 'blue', tloustka=2.5)
        ax.text(L_ref + 0.05, 0.05, 'U', color='blue', fontsize=13, weight='bold')

        if pouzito_R and not pouzito_L and not pouzito_C:
            # ── jen R ──────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, 'red', tloustka=2.5)
            ax.text(L_R / 2, -0.12, 'I = I_R', color='red', fontsize=11,
                    ha='center', weight='bold')

        elif not pouzito_R and pouzito_L and not pouzito_C:
            # ── jen L ──────────────────────────────────────────────
            # I_L dolů, φ = -90°
            sipka(ax, 0, 0, 0, -L_L, 'red', tloustka=2.5)
            ax.text(0.08, -L_L - 0.1, 'I = I_L', color='red', fontsize=11,
                    weight='bold')
            uhly = np.linspace(0, -np.pi / 2, 60)
            ax.plot(0.25 * np.cos(uhly), 0.25 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.08, -0.32, 'φ=-90°', color='green', fontsize=10, weight='bold')

        elif not pouzito_R and not pouzito_L and pouzito_C:
            # ── jen C ──────────────────────────────────────────────
            # I_C nahoru, φ = +90°
            sipka(ax, 0, 0, 0, L_C, 'red', tloustka=2.5)
            ax.text(0.08, L_C + 0.05, 'I = I_C', color='red', fontsize=11,
                    weight='bold')
            uhly = np.linspace(0, np.pi / 2, 60)
            ax.plot(0.25 * np.cos(uhly), 0.25 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.08, 0.3, 'φ=+90°', color='green', fontsize=10, weight='bold')

        elif pouzito_R and pouzito_L and not pouzito_C:
            # ── RL ─────────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, '#B71C1C', tloustka=1.8, styl='dashed')
            ax.text(L_R / 2, 0.1, 'I_R', color='#B71C1C', fontsize=10,
                    ha='center', weight='bold')
            sipka(ax, 0, 0, 0, -L_L, '#7B1FA2', tloustka=1.8)
            ax.text(0.07, -L_L / 2, 'I_L', color='#7B1FA2', fontsize=10,
                    weight='bold')
            carkovana_rovnobezka(ax, L_R, 0, L_R, -L_L)
            carkovana_rovnobezka(ax, 0, -L_L, L_R, -L_L)
            sipka(ax, 0, 0, L_R, -L_L, 'red', tloustka=3)
            ax.text(L_R + 0.06, -L_L - 0.08, 'I', color='red', fontsize=13,
                    weight='bold')
            phi_rad = np.arctan2(-L_L, L_R)
            uhly = np.linspace(0, phi_rad, 60)
            ax.plot(0.28 * np.cos(uhly), 0.28 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.22 * np.cos(phi_rad / 2) + 0.05,
                    0.22 * np.sin(phi_rad / 2) - 0.08,
                    f'φ={phi}°', color='green', fontsize=10, weight='bold')

        elif pouzito_R and not pouzito_L and pouzito_C:
            # ── RC ─────────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, '#B71C1C', tloustka=1.8, styl='dashed')
            ax.text(L_R / 2, -0.12, 'I_R', color='#B71C1C', fontsize=10,
                    ha='center', weight='bold')
            sipka(ax, 0, 0, 0, L_C, '#E53935', tloustka=1.8)
            ax.text(0.07, L_C / 2, 'I_C', color='#E53935', fontsize=10,
                    weight='bold')
            carkovana_rovnobezka(ax, L_R, 0, L_R, L_C)
            carkovana_rovnobezka(ax, 0, L_C, L_R, L_C)
            sipka(ax, 0, 0, L_R, L_C, 'red', tloustka=3)
            ax.text(L_R + 0.06, L_C + 0.05, 'I', color='red', fontsize=13,
                    weight='bold')
            phi_rad = np.arctan2(L_C, L_R)
            uhly = np.linspace(0, phi_rad, 60)
            ax.plot(0.28 * np.cos(uhly), 0.28 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.22 * np.cos(phi_rad / 2) + 0.05,
                    0.22 * np.sin(phi_rad / 2) + 0.05,
                    f'φ={phi}°', color='green', fontsize=10, weight='bold')

        elif not pouzito_R and pouzito_L and pouzito_C:
            # ── LC bez R ───────────────────────────────────────────
            sipka(ax, 0, 0, 0, -L_L, '#7B1FA2', tloustka=1.8)
            ax.text(0.07, -L_L / 2, 'I_L', color='#7B1FA2', fontsize=10,
                    weight='bold')
            sipka(ax, 0, 0, 0, L_C, '#E53935', tloustka=1.8)
            ax.text(0.07, L_C / 2, 'I_C', color='#E53935', fontsize=10,
                    weight='bold')
            vy = smer_reak * L_reak
            sipka(ax, 0, 0, 0, vy, 'red', tloustka=3)
            ax.text(0.08, vy + 0.05 * smer_reak, 'I', color='red', fontsize=13,
                    weight='bold')
            phi_label = "+90°" if vy > 0 else "-90°"
            uhly = np.linspace(0, np.pi / 2 * smer_reak, 60)
            ax.plot(0.25 * np.cos(uhly), 0.25 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.08, 0.3 * smer_reak, f'φ={phi_label}', color='green',
                    fontsize=10, weight='bold')

        else:
            # ── RLC ────────────────────────────────────────────────
            sipka(ax, 0, 0, L_R, 0, '#B71C1C', tloustka=1.8, styl='dashed')
            ax.text(L_R / 2, -0.12, 'I_R', color='#B71C1C', fontsize=10,
                    ha='center', weight='bold')
            sipka(ax, 0, 0, 0, L_C, '#E53935', tloustka=1.8)
            ax.text(0.07, L_C / 2, 'I_C', color='#E53935', fontsize=10,
                    weight='bold')
            sipka(ax, 0, 0, 0, -L_L, '#7B1FA2', tloustka=1.8)
            ax.text(0.07, -L_L / 2, 'I_L', color='#7B1FA2', fontsize=10,
                    weight='bold')
            vy = smer_reak * L_reak
            carkovana_rovnobezka(ax, L_R, 0, L_R, vy)
            carkovana_rovnobezka(ax, 0, vy, L_R, vy)
            sipka(ax, 0, 0, L_R, vy, 'red', tloustka=3)
            ax.text(L_R + 0.06, vy + 0.05 * smer_reak, 'I', color='red',
                    fontsize=13, weight='bold')
            phi_rad = np.arctan2(vy, L_R)
            uhly = np.linspace(0, phi_rad, 60)
            ax.plot(0.28 * np.cos(uhly), 0.28 * np.sin(uhly), 'g-', lw=1.5)
            ax.text(0.22 * np.cos(phi_rad / 2) + 0.05,
                    0.22 * np.sin(phi_rad / 2) + 0.05 * smer_reak,
                    f'φ={phi}°', color='green', fontsize=10, weight='bold')

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('Reálná osa')
    ax.set_ylabel('Imaginární osa')
    ax.set_title(f'Fázorový diagram  |  φ = {phi}°', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_aspect('equal')

    return fig

# ─────────────────────────────────────────────
# ČASOVÉ PRŮBĚHY
# ─────────────────────────────────────────────
def nakresli_casove_prubehy(phi):
    t = np.linspace(0, 0.04, 1000)
    omega = 2 * np.pi * 50
    phi_rad = np.radians(phi)

    u = 10 * np.sin(omega * t)
    i = 8  * np.sin(omega * t + phi_rad)

    fig, ax = plt.subplots(figsize=(10, 4))
    # Napětí modře, proud červeně
    ax.plot(t * 1000, u, color='blue',  linewidth=2, label='Napětí u(t) [V]')
    ax.plot(t * 1000, i, color='red',   linewidth=2, label='Proud i(t) [A]')

    if phi != 0:
        t_max_u = (1 / (4 * 50)) * 1000
        t_max_i = t_max_u - (phi / 360) * (1 / 50) * 1000
        y_sipka = -10.5
        ax.annotate('', xy=(t_max_i, y_sipka), xytext=(t_max_u, y_sipka),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax.text((t_max_u + t_max_i) / 2, y_sipka - 1.0,
                f"φ = {phi}°", ha='center', color='green', fontsize=11)

    ax.set_xlabel('Čas [ms]')
    ax.set_ylabel('Hodnota')
    ax.set_title('Časové průběhy napětí a proudu')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_ylim(-13, 13)

    return fig


# ─────────────────────────────────────────────
# HLAVNÍ APLIKACE
# ─────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Fázový posun RLC", layout="wide")
    st.title("⚡ Interaktivní vizualizace fázového posunu")
    st.subheader("Výuková pomůcka pro elektrotechniku – RLC obvody")

    with st.sidebar:
        st.header("⚙️ Konfigurace obvodu")
        obvod_typ = st.radio("Typ zapojení:", ["Sériový", "Paralelní"])
        st.markdown("---")
        st.markdown("**Vyber komponenty:**")
        pouzito_R = st.checkbox("Rezistor (R)", value=True)
        pouzito_L = st.checkbox("Cívka (L)")
        pouzito_C = st.checkbox("Kondenzátor (C)")

        prevazuje = "Žádný"
        if pouzito_L and pouzito_C:
            st.markdown("---")
            prevazuje = st.radio("Dominantní komponenta:",
                                 ["Cívka (L)", "Kondenzátor (C)",
                                  "Stejný vliv (rezonance)"])

        # ── přepínače zobrazení ──────────────────────────────────
        st.markdown("---")
        st.markdown("**Zobrazit:**")
        zobraz_fazory = st.checkbox("📊 Fázorový diagram", value=False)
        zobraz_casovy = st.checkbox("📈 Časový průběh",    value=False)

    phi = vypocti_fazovy_posun(pouzito_R, pouzito_L, pouzito_C,
                               prevazuje, obvod_typ)

    if phi == 0:
        st.info("⚖️ Fázový posun: **0°** – napětí a proud jsou ve fázi.")
    elif phi < 0:
        st.warning(f"🔵 Fázový posun: **{phi}°** – proud **zaostává** za napětím (induktivní charakter).")
    else:
        st.success(f"🔴 Fázový posun: **{phi}°** – proud **předbíhá** napětí (kapacitní charakter).")

    # ── schéma — vždy viditelné ──────────────────────────────────
    if not zobraz_fazory:
        # schéma přes celou šířku když je fázor skrytý
        st.subheader("Schéma obvodu")
        fig_obvod = nakresli_obvod(pouzito_R, pouzito_L, pouzito_C, obvod_typ)
        st.pyplot(fig_obvod)
        plt.close(fig_obvod)
    else:
        # schéma vlevo, fázorový diagram vpravo
        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Schéma obvodu")
            fig_obvod = nakresli_obvod(pouzito_R, pouzito_L, pouzito_C, obvod_typ)
            st.pyplot(fig_obvod)
            plt.close(fig_obvod)
        with col2:
            st.subheader("Fázorový diagram")
            fig_ph = nakresli_fazorovy_diagram(phi, pouzito_R, pouzito_L,
                                               pouzito_C, prevazuje, obvod_typ)
            st.pyplot(fig_ph)
            plt.close(fig_ph)

    # ── časový průběh — pouze pokud zaškrtnuto ───────────────────
    if zobraz_casovy:
        st.subheader("Časový průběh")
        fig_time = nakresli_casove_prubehy(phi)
        st.pyplot(fig_time)
        plt.close(fig_time)

if __name__ == "__main__":
    main()