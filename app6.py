# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 22:32:07 2025

@author: marti
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 16:53:21 2025
@author: marti
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Configuración de estilos globales ---
plt.rcParams.update({'font.size': 8})
st.set_page_config(layout="wide")

# --- Sidebar con parámetros ---
st.sidebar.header("Parámetros del Dashboard")

crecimiento_facturas = st.sidebar.slider("Crecimiento mensual de facturas (%)", 0.0, 20.0, 5.0) / 100
tasa_A = st.sidebar.slider("Tasa base Factura A (%)", 6.0, 15.0, 9.0)
tasa_B = st.sidebar.slider("Tasa base Factura B (%)", 8.0, 18.0, 12.0)
tasa_C = st.sidebar.slider("Tasa base Factura C (%)", 10.0, 25.0, 15.0)
variacion_tasa = st.sidebar.slider("Variación aleatoria tasas (%)", 0.0, 5.0, 2.0)

prob_A = st.sidebar.slider("% Facturas riesgo A", 0, 100, 50)
prob_B = st.sidebar.slider("% Facturas riesgo B", 0, 100 - prob_A, 30)
prob_C = 100 - prob_A - prob_B

senior_pct = st.sidebar.slider("% Deuda Senior", 0.0, 1.0, 0.60)
junior_pct = st.sidebar.slider("% Capital Junior", 0.0, 1.0, 0.30)
equity_pct = 1.0 - senior_pct - junior_pct

senior_rate = st.sidebar.slider("Tasa anual Deuda Senior (%)", 2.0, 12.0, 7.0) / 100
junior_rate = st.sidebar.slider("Tasa anual Capital Junior (%)", 5.0, 18.0, 12.0) / 100

comision_originador = st.sidebar.slider("Comisión Originador (% por factura)", 0.1, 0.5, 0.2) / 100

participacion_A = st.sidebar.slider("Participación Socio A", 0.0, 1.0, 0.5)
participacion_B = 1.0 - participacion_A

incobrabilidad = st.sidebar.slider("% Facturas Incobrables", 0.0, 10.0, 3.0) / 100
seguro_cobertura = 0.90
seguro_dias = 180
tasa_portafolio = (tasa_A * prob_A + tasa_B * prob_B + tasa_C * prob_C) / 100
seguro_prima = st.sidebar.slider("Prima Seguro Crédito (%)", 0.25, 0.55, 0.35) / 100

# --- Simulación base ---
meses = 12
facturas_iniciales = 100
resumen = []
facturas_por_riesgo = {'A': 0, 'B': 0, 'C': 0}

for mes in range(1, meses + 1):
    total_facturas = int(facturas_iniciales * ((1 + crecimiento_facturas) ** (mes - 1)))
    montos = []
    tasas = []
    origen_A = 0
    tasas_A, tasas_B, tasas_C = [], [], []

    for _ in range(total_facturas):
        riesgo = np.random.choice(['A', 'B', 'C'], p=[prob_A/100, prob_B/100, prob_C/100])
        facturas_por_riesgo[riesgo] += 1

        tasa_base = {'A': tasa_A, 'B': tasa_B, 'C': tasa_C}[riesgo]
        variacion = np.random.uniform(-variacion_tasa, variacion_tasa)
        tasa_final = max(tasa_base + variacion, 0) / 100
        monto = np.random.normal(15000, 3000)
        monto = max(monto, 1000)
        montos.append(monto)
        tasas.append(tasa_final)

        if riesgo == 'A':
            tasas_A.append(tasa_final)
        elif riesgo == 'B':
            tasas_B.append(tasa_final)
        else:
            tasas_C.append(tasa_final)

        origen_A += monto * comision_originador

    total_exportado = sum(montos)
    total_financiado = sum(montos)
    ingreso_bruto = sum([m * t / 12 for m, t in zip(montos, tasas)])
    perdidas = total_financiado * incobrabilidad * (1 - seguro_cobertura)
    recupero_seguro = total_financiado * incobrabilidad * seguro_cobertura / ((1 + tasa_portafolio) ** (seguro_dias / 360))
    costo_seguro = total_exportado * seguro_prima
    costo_senior = total_financiado * senior_pct * senior_rate / 12
    costo_junior = total_financiado * junior_pct * junior_rate / 12
    flujo_equity = ingreso_bruto - perdidas + recupero_seguro - costo_seguro - costo_senior - costo_junior
    base_equity = total_financiado * equity_pct

    retorno_senior = senior_rate * 100 / 12
    retorno_junior = junior_rate * 100 / 12
    retorno_equity = (flujo_equity / base_equity) * 100 if base_equity else 0

    retorno_A = (flujo_equity * participacion_A) / (base_equity * participacion_A) * 100
    retorno_B = (flujo_equity * participacion_B) / (base_equity * participacion_B) * 100
    ingreso_A = flujo_equity * participacion_A
    ingreso_B = flujo_equity * participacion_B

    tasa_A_prom = np.mean(tasas_A) * 100 if tasas_A else 0
    tasa_B_prom = np.mean(tasas_B) * 100 if tasas_B else 0
    tasa_C_prom = np.mean(tasas_C) * 100 if tasas_C else 0

    resumen.append({
        "Mes": mes,
        "Facturas": total_facturas,
        "Monto Financiado": total_financiado,
        "Ingreso Bruto": ingreso_bruto,
        "Perdidas": perdidas,
        "Recupero Seguro": recupero_seguro,
        "Costo Seguro": costo_seguro,
        "Costo Senior": costo_senior,
        "Costo Junior": costo_junior,
        "Flujo a Equity": flujo_equity,
        "Ingreso A": ingreso_A,
        "Ingreso B": ingreso_B,
        "Retorno A (%)": retorno_A,
        "Retorno B (%)": retorno_B,
        "Ingreso Originador": origen_A,
        "Tasa A": tasa_A_prom,
        "Tasa B": tasa_B_prom,
        "Tasa C": tasa_C_prom,
        "Retorno Senior": retorno_senior,
        "Retorno Junior": retorno_junior,
        "Retorno Equity": retorno_equity
    })

# --- DataFrame resultado ---
df = pd.DataFrame(resumen)

# --- KPIs ---
st.title("Simulación Financiamiento Facturas - Dashboard Interactivo")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Financiado", f"${df['Monto Financiado'].sum():,.0f}")
kpi2.metric("Ingreso Total Originador", f"${df['Ingreso Originador'].sum():,.0f}")
kpi3.metric("Pérdidas Totales", f"${df['Perdidas'].sum():,.0f}")
kpi4.metric("Flujo Total a Equity", f"${df['Flujo a Equity'].sum():,.0f}")

# --- Gráficos ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Ingreso Socio A vs Socio B")
    fig1, ax1 = plt.subplots()
    ax1.bar(df["Mes"] - 0.2, df["Ingreso A"], width=0.4, label="Socio A")
    ax1.bar(df["Mes"] + 0.2, df["Ingreso B"], width=0.4, label="Socio B")
    ax1.set_ylabel("USD")
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

with col2:
    st.markdown("#### Ingreso Originador vs Socio A")
    fig2, ax2 = plt.subplots()
    ax2.plot(df["Mes"], df["Ingreso Originador"], label="Originador", marker='^')
    ax2.plot(df["Mes"], df["Ingreso A"], label="Socio A", marker='d')
    ax2.set_ylabel("USD")
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)

with col3:
    st.markdown("#### Flujo neto a Equity")
    fig3, ax3 = plt.subplots()
    ax3.bar(df["Mes"], df["Flujo a Equity"], color="purple")
    ax3.set_ylabel("USD")
    ax3.grid(True)
    st.pyplot(fig3)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("#### Distribución de Facturas por Riesgo")
    fig4, ax4 = plt.subplots()
    labels = list(facturas_por_riesgo.keys())
    sizes = list(facturas_por_riesgo.values())
    ax4.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax4.axis('equal')
    st.pyplot(fig4)

with col5:
    st.markdown("#### Pérdidas por Incobrabilidad")
    fig5, ax5 = plt.subplots()
    ax5.plot(df["Mes"], df["Perdidas"], color="red", marker='x')
    ax5.set_ylabel("USD")
    ax5.grid(True)
    st.pyplot(fig5)

with col6:
    st.markdown("#### Pérdida + Costo Seguro vs Recupero")
    fig6, ax6 = plt.subplots()
    total_costos = df["Perdidas"] + df["Costo Seguro"]
    ax6.bar(df["Mes"] - 0.2, total_costos, width=0.4, label="Pérdida + Costo Seguro", color='red')
    ax6.bar(df["Mes"] + 0.2, df["Recupero Seguro"], width=0.4, label="Recupero", color='green')
    ax6.set_ylabel("USD")
    ax6.grid(True)
    ax6.legend()
    st.pyplot(fig6)

col7, col8, col9 = st.columns(3)

with col7:
    st.markdown("#### Evolución del Monto Financiado")
    fig7, ax7 = plt.subplots()
    ax7.plot(df["Mes"], df["Monto Financiado"], color="green", marker='D')
    ax7.set_ylabel("USD")
    ax7.grid(True)
    st.pyplot(fig7)

with col8:
    st.markdown("#### Evolución Tasas por Riesgo")
    fig8, ax8 = plt.subplots()
    ax8.plot(df["Mes"], df["Tasa A"], label="Tasa A")
    ax8.plot(df["Mes"], df["Tasa B"], label="Tasa B")
    ax8.plot(df["Mes"], df["Tasa C"], label="Tasa C")
    ax8.set_ylabel("% Anual")
    ax8.grid(True)
    ax8.legend()
    st.pyplot(fig8)

with col9:
    st.markdown("#### Retorno por Nivel de Capital")
    fig9, ax9 = plt.subplots()
    ax9.plot(df["Mes"], df["Retorno Senior"], label="Deuda Senior")
    ax9.plot(df["Mes"], df["Retorno Junior"], label="Capital Junior")
    ax9.plot(df["Mes"], df["Retorno Equity"], label="Equity")
    ax9.set_ylabel("% Mensual")
    ax9.grid(True)
    ax9.legend()
    st.pyplot(fig9)

# Tabla final
st.markdown("#### Resumen mensual")
st.dataframe(df.style.format("{:.2f}"))
