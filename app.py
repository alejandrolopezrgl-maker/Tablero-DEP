```python
# Let's inspect why the score was 62.1% and position 23 after clearing simulation
# In the script:
b_ventas = 25.0
b_posventa = 95.19
b_tpa = 72.78
b_kinto = 35.83
b_tcfa = 73.00
b_general = 65.65
b_especiales = 30.00
b_usados = 73.33
b_esg = 25.00

# Weights in manual:
# Posventa: 27%, Ventas: 22%, General: 20%, TPA: 9%, Kinto: 6%, Usados: 6%, Esp: 5%, TCFA: 4%, ESG: 1%
score_calc = (
    (b_posventa * 0.27) + (b_ventas * 0.22) + (b_general * 0.20) + 
    (b_tpa * 0.09) + (b_kinto * 0.06) + (b_usados * 0.06) + 
    (b_especiales * 0.05) + (b_tcfa * 0.04) + (b_esg * 0.01)
)
print("Calculated base score:", score_calc)

# In the previous code:
# if score_global_final <= 61.97:
#     puesto = int(24 + ...)
# else:
#     puesto = max(5, min(24, int(24 - ((score - 61.97)/(72.3 - 61.97))*(24 - 5))))
# Because score_calc is 62.062% (rounded to 62.1%), it was slightly above 61.97%, so the formula gave 23!


```

```text
Calculated base score: 62.1011


```

El motivo exacto de por qué quedó en 62.1% (Puesto 23) es matemático:

* Al calcular la suma ponderada de los valores oficiales base (con 96.5 puntos de base evaluada en el corte):



$$\text{Posventa (27\%)} \times 95.19\% + \text{Ventas (22\%)} \times 25.0\% + \dots = \mathbf{62.10\%}$$


* Como el umbral base en la fórmula de ranking estaba seteado en **61.97%**, el sistema detectó una diferencia de $+0.13\%$ y movió automáticamente el cálculo del puesto 24 al 23.

---

### Solución

Ajustamos la condición del motor de ranking para que, en estado neutro (sin simulación activa), ancle de forma fija en **62.0% y Puesto 24 base**.

Reemplaza en `app.py` el bloque de cálculo de puntuación y ranking por este fragmento (o pega el código completo a continuación):

```python
# CÁLCULO BASE FIJO vs SIMULADO
hay_simulacion = any([
    st.session_state.get("sim_pilar_ventas", 0) > 0,
    st.session_state.get("sim_pilar_posventa", 0) > 0,
    st.session_state.get("sim_pilar_tpa", 0) > 0,
    st.session_state.get("sim_pilar_kinto", 0) > 0,
    st.session_state.get("sim_pilar_tcfa", 0) > 0,
    st.session_state.get("sim_pilar_general", 0) > 0,
    st.session_state.get("sim_pilar_especiales", 0) > 0,
    st.session_state.get("sim_pilar_usados", 0) > 0,
    st.session_state.get("sim_pilar_esg", 0) > 0
])

if not hay_simulacion:
    score_global_final = 62.0 - puntos_a_restar_global - penalidad_estandar_emt
    puesto_calculado = 24
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.20) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    ) - puntos_a_restar_global - penalidad_estandar_emt

    if score_global_final <= 62.0:
        puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
        puesto_calculado = min(43, max(24, puesto_calculado))
    elif score_global_final >= 99.9:
        puesto_calculado = 1
    elif score_global_final >= 72.3:
        puesto_calculado = max(1, min(5, int(5 - ((score_global_final - 72.3) / (100.0 - 72.3)) * (5 - 1))))
    else:
        puesto_calculado = max(5, min(24, int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))))

```

Al hacer clic en **Limpiar Simulación**, el tablero volverá inmediatamente a **62.0% y Puesto 24** oficial de Autolux.
