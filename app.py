import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Dashboard Médico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# ESTILO GENERAL
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #1E1E1E;
    color: white;
}

.stApp {
    background-color: #1E1E1E;
}

h1, h2, h3, h4 {
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGAR BASE
# =====================================================

base1 = pd.read_excel("Dashboard.xlsx")
base1["mes"] = (
    base1["mes"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# =====================================================
# LIMPIEZA
# =====================================================

base1.columns = base1.columns.str.strip()

base1 = base1.loc[
    :,
    ~base1.columns.str.contains("^Unnamed")
]

# =====================================================
# ORDEN DE MESES
# =====================================================
orden_meses = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio"
]







base1["mes"] = pd.Categorical(
    base1["mes"],
    categories=orden_meses,
    ordered=True
)

# =====================================================
# CONVERTIR PORCENTAJES
# =====================================================

porcentajes = [
    "% Cumplimiento",
    "% Rendimiento",
    "% formulas",
    "% laboratorios",
    "%Ayudas Diagnosticas",
    "% De remisiones",
    "Total  de resolutividad"
]

for col in porcentajes:
    base1[col] = base1[col] * 100

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Filtros")

especialidad = st.sidebar.multiselect(
    "Seleccione especialidad",
    options=base1["especialidad"].unique(),
    default=base1["especialidad"].unique()
)

medico = st.sidebar.multiselect(
    "Seleccione médico",
    options=base1["NOMBRE DEL MEDICO"].unique(),
    default=base1["NOMBRE DEL MEDICO"].unique()
)

meses = st.sidebar.multiselect(
    "Seleccione mes",
    options=orden_meses,
    default=orden_meses
)

# =====================================================
# FILTRAR BASE
# =====================================================

df = base1[
    (base1["especialidad"].isin(especialidad)) &
    (base1["NOMBRE DEL MEDICO"].isin(medico)) &
    (base1["mes"].isin(meses))
]

# =====================================================
# TITULO
# =====================================================

st.title("Dashboard Ejecutivo Médico")

st.markdown("---")

# =====================================================
# KPIs
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Cumplimiento Promedio",
        f"{df['% Cumplimiento'].mean():.1f}%"
    )

with col2:
    st.metric(
        "Rendimiento Promedio",
        f"{df['% Rendimiento'].mean():.1f}%"
    )

with col3:
    st.metric(
        "Resolutividad",
        f"{df['Total  de resolutividad'].mean():.1f}%"
    )

with col4:
    st.metric(
        "Total Remisiones",
        int(df["Total  Remisiones"].sum())
    )

st.markdown("---")

# =====================================================
# TABLA CUMPLIMIENTO
# =====================================================

st.subheader("Tabla Resumen de Cumplimiento Médico")

tabla_cumplimiento = df.pivot_table(
    index=[
        "especialidad",
        "NOMBRE DEL MEDICO"
    ],
    columns="mes",
    values="% Cumplimiento",
    aggfunc="mean"
).reset_index()

tabla_cumplimiento.columns = (
    ["Especialidad", "Médico"] +
    [col.capitalize() for col in tabla_cumplimiento.columns[2:]]
)

columnas_existentes = [
    col for col in ["Enero", "Febrero", "Marzo", "Abril","Mayo","Junio","julio"]
    if col in tabla_cumplimiento.columns
]

tabla_cumplimiento["Promedio General"] = (
    tabla_cumplimiento[columnas_existentes]
    .mean(axis=1)
)

# Formatear todas las columnas numéricas excepto Especialidad y Médico

for col in tabla_cumplimiento.columns:
    if col not in ["Especialidad", "Médico"]:
        tabla_cumplimiento[col] = tabla_cumplimiento[col].apply(
            lambda x: f"{x:.1f}%" if pd.notnull(x) else ""
        )



estilo_cump = tabla_cumplimiento.style \
    .set_properties(**{
        'background-color': '#1E1E1E',
        'color': 'white',
        'border-color': 'gray',
        'text-align': 'center'
    }) \
    .set_table_styles([
        {
            'selector': 'th',
            'props': [
                ('background-color', '#102030'),
                ('color', 'white'),
                ('border', '1px solid gray')
            ]
        }
    ])

st.write(estilo_cump)

# =====================================================
# GRAFICA CUMPLIMIENTO
# =====================================================

st.title("Cumplimiento Médico")

fig = px.line(
    df,
    x="mes",
    y="% Cumplimiento",
    color="NOMBRE DEL MEDICO",
    markers=True
)

fig.update_layout(
    title={
        "text": "% Cumplimiento por Médico",
        "x": 0.5
    },

    paper_bgcolor="#1E1E1E",
    plot_bgcolor="#1E1E1E",

    font=dict(color="white"),

    legend=dict(
        font=dict(
            color="white",
            size=12
        ),

        title=dict(
            text="Médicos",
            font=dict(
                color="white"
            )
        )
    ),

    xaxis=dict(
        color="white"
    ),

    yaxis=dict(
        color="white"
    ),

    height=650
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# INTERPRETACIÓN CUMPLIMIENTO
# =====================================================

st.subheader("Interpretación Ejecutiva")

promedio = df["% Cumplimiento"].mean()

maximo = df["% Cumplimiento"].max()

minimo = df["% Cumplimiento"].min()

texto = f"""
Durante el periodo analizado, el porcentaje promedio de cumplimiento fue de
{promedio:.1f}%.

Adicionalmente, se identificó un valor máximo de cumplimiento de
{maximo:.1f}% y un mínimo de {minimo:.1f}%,
evidenciando diferencias operativas entre los profesionales evaluados.
"""

st.markdown(f"""
<div style="
background-color:#102030;
padding:20px;
border-radius:10px;
color:white;
font-size:17px;
line-height:1.8;
">

{texto}

</div>
""", unsafe_allow_html=True)

# =====================================================
# RENDIMIENTO
# =====================================================

st.markdown("---")

st.title("Rendimiento Médico")

# =====================================================
# TABLA RENDIMIENTO
# =====================================================

st.subheader("Tabla Resumen de Rendimiento Médico")

tabla_rendimiento = df.pivot_table(
    index=[
        "especialidad",
        "NOMBRE DEL MEDICO"
    ],
    columns="mes",
    values="% Rendimiento",
    aggfunc="mean"
).reset_index()

tabla_rendimiento.columns = (
    ["Especialidad", "Médico"] +
    [col.capitalize() for col in tabla_rendimiento.columns[2:]]
)

columnas_existentes_r = [
    col for col in ["Enero", "Febrero", "Marzo", "Abril","Mayo","Junio","julio"]
    if col in tabla_rendimiento.columns
]

tabla_rendimiento["Promedio General"] = (
    tabla_rendimiento[columnas_existentes_r]
    .mean(axis=1)
)

for col in tabla_rendimiento.columns:
    if col not in ["Especialidad", "Médico"]:
        tabla_rendimiento[col] = tabla_rendimiento[col].apply(
            lambda x: f"{x:.1f}%" if pd.notnull(x) else ""
        )
estilo_r = tabla_rendimiento.style \
    .set_properties(**{
        'background-color': '#1E1E1E',
        'color': 'white',
        'border-color': 'gray',
        'text-align': 'center'
    }) \
    .set_table_styles([
        {
            'selector': 'th',
            'props': [
                ('background-color', '#102030'),
                ('color', 'white'),
                ('border', '1px solid gray')
            ]
        }
    ])

st.write(estilo_r)

# =====================================================
# GRAFICA RENDIMIENTO
# =====================================================

fig2 = px.line(
    df,
    x="mes",
    y="% Rendimiento",
    color="NOMBRE DEL MEDICO",
    markers=True
)

fig2.update_layout(
    title={
        "text": "% Rendimiento por Médico",
        "x": 0.5
    },

    paper_bgcolor="#1E1E1E",
    plot_bgcolor="#1E1E1E",

    font=dict(color="white"),

    legend=dict(
        font=dict(
            color="white",
            size=12
        ),

        title=dict(
            text="Médicos",
            font=dict(
                color="white"
            )
        )
    ),

    xaxis=dict(
        color="white"
    ),

    yaxis=dict(
        color="white"
    ),

    height=650
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================================
# INTERPRETACIÓN RENDIMIENTO
# =====================================================

st.subheader("Interpretación Ejecutiva")

promedio_r = df["% Rendimiento"].mean()

texto_r = f"""
Durante el periodo analizado, el rendimiento promedio del personal médico fue de
{promedio_r:.1f}%.

El comportamiento general evidencia estabilidad operativa y diferencias entre
los profesionales evaluados.
"""

st.markdown(f"""
<div style="
background-color:#102030;
padding:20px;
border-radius:10px;
color:white;
font-size:17px;
line-height:1.8;
">

{texto_r}

</div>
""", unsafe_allow_html=True)

# =====================================================
# PROCEDIMIENTOS
# =====================================================

st.markdown("---")

st.title("Procedimientos Médicos")

# =====================================================
# TABLA PROCEDIMIENTOS
# =====================================================

st.subheader("Tabla Resumen de Procedimientos")

proc1 = df[[
    "especialidad",
    "NOMBRE DEL MEDICO",
    "mes",
    "% formulas"
]].copy()

proc1["Procedimiento"] = "Fórmulas"
proc1 = proc1.rename(columns={"% formulas": "Porcentaje"})

proc2 = df[[
    "especialidad",
    "NOMBRE DEL MEDICO",
    "mes",
    "% laboratorios"
]].copy()

proc2["Procedimiento"] = "Laboratorios"
proc2 = proc2.rename(columns={"% laboratorios": "Porcentaje"})

proc3 = df[[
    "especialidad",
    "NOMBRE DEL MEDICO",
    "mes",
    "%Ayudas Diagnosticas"
]].copy()

proc3["Procedimiento"] = "Ayudas Diagnósticas"
proc3 = proc3.rename(columns={"%Ayudas Diagnosticas": "Porcentaje"})

procedimientos = pd.concat([
    proc1,
    proc2,
    proc3
])

tabla_proc = procedimientos.pivot_table(
    index=[
        "especialidad",
        "NOMBRE DEL MEDICO",
        "Procedimiento"
    ],
    columns="mes",
    values="Porcentaje",
    aggfunc="mean"
).reset_index()

tabla_proc.columns = (
    ["Especialidad", "Médico", "Procedimiento"] +
    [col.capitalize() for col in tabla_proc.columns[3:]]
)

for col in tabla_proc.columns[3:]:

    tabla_proc[col] = tabla_proc[col].apply(
        lambda x: f"{x:.1f}%"
        if pd.notnull(x)
        else ""
    )

estilo_proc = tabla_proc.style \
    .set_properties(**{
        'background-color': '#1E1E1E',
        'color': 'white',
        'border-color': 'gray',
        'text-align': 'center'
    })

st.write(estilo_proc)

# =====================================================
# GRAFICA PROCEDIMIENTOS
# =====================================================

procedimientos_graf = df.groupby(
    ["mes", "NOMBRE DEL MEDICO"]
)[
    [
        "% formulas",
        "% laboratorios",
        "%Ayudas Diagnosticas"
    ]
].mean().reset_index()

procedimientos_long = procedimientos_graf.melt(
    id_vars=["mes", "NOMBRE DEL MEDICO"],
    var_name="Procedimiento",
    value_name="Porcentaje"
)

fig3 = px.bar(
    procedimientos_long,
    y="NOMBRE DEL MEDICO",
    x="Porcentaje",
    color="Procedimiento",
    orientation="h",
    barmode="stack",
    text_auto=".1f"
)

fig3.update_traces(
    texttemplate="%{x:.1f}%",
    textposition="inside",
    textfont=dict(
        color="white",
        size=11
    )
)

fig3.update_layout(
    title={
        "text": "Distribución de Procedimientos Médicos",
        "x": 0.5
    },

    paper_bgcolor="#1E1E1E",
    plot_bgcolor="#1E1E1E",

    font=dict(
        color="white"
    ),

    legend=dict(
        font=dict(
            color="white",
            size=12
        ),

        title=dict(
            text="Procedimientos",
            font=dict(
                color="white"
            )
        )
    ),

    xaxis=dict(
        color="white"
    ),

    yaxis=dict(
        color="white"
    ),

    height=850
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =====================================================
# INTERPRETACIÓN PROCEDIMIENTOS
# =====================================================

st.subheader("Interpretación Ejecutiva")

texto_proc = """
La distribución porcentual de procedimientos médicos evidencia diferencias
operativas entre los profesionales evaluados.

Se observó variabilidad en la utilización de fórmulas médicas,
órdenes de laboratorio y ayudas diagnósticas,
permitiendo identificar diferentes patrones de atención clínica.
"""

st.markdown(f"""
<div style="
background-color:#102030;
padding:20px;
border-radius:10px;
color:white;
font-size:17px;
line-height:1.8;
">

{texto_proc}

</div>
""", unsafe_allow_html=True)

# =====================================================
# RESOLUTIVIDAD Y REMISIONES
# =====================================================


# ==========================================
# TABLA RESOLUTIVIDAD Y REMISIONES
# ==========================================

st.markdown("---")

st.title("Resolutividad y Remisiones")


st.subheader("Tabla Resumen de Resolutividad y Remisiones")

# Resolutividad
res1 = df[[
    "especialidad",
    "NOMBRE DEL MEDICO",
    "mes",
    "Total  de resolutividad"
]].copy()

res1["Indicador"] = "Resolutividad"
res1 = res1.rename(
    columns={"Total  de resolutividad": "Porcentaje"}
)

# Remisiones
res2 = df[[
    "especialidad",
    "NOMBRE DEL MEDICO",
    "mes",
    "% De remisiones"
]].copy()

res2["Indicador"] = "Remisiones"
res2 = res2.rename(
    columns={"% De remisiones": "Porcentaje"}
)

# Unir ambas tablas
tabla_resol = pd.concat([res1, res2])

# Crear tabla dinámica
tabla_resol = tabla_resol.pivot_table(
    index=[
        "especialidad",
        "NOMBRE DEL MEDICO",
        "Indicador"
    ],
    columns="mes",
    values="Porcentaje",
    aggfunc="mean"
).reset_index()

# Renombrar columnas
tabla_resol.columns = (
    ["Especialidad", "Médico", "Indicador"] +
    [str(col).capitalize() for col in tabla_resol.columns[3:]]
)

# Formato porcentaje
for col in tabla_resol.columns:
    if col not in ["Especialidad", "Médico", "Indicador"]:
        tabla_resol[col] = tabla_resol[col].apply(
            lambda x: f"{x:.1f}%" if pd.notnull(x) else ""
        )

# Estilo
estilo_resol = tabla_resol.style \
    .set_properties(**{
        'background-color': '#1E1E1E',
        'color': 'white',
        'border-color': 'gray',
        'font-size': '13px',
        'text-align': 'center'
    }) \
    .set_table_styles([
        {
            'selector': 'th',
            'props': [
                ('background-color', '#102030'),
                ('color', 'white'),
                ('border', '1px solid gray')
            ]
        }
    ])

st.write(estilo_resol)





resol = df.groupby("mes")[
    [
        "% De remisiones",
        "Total  de resolutividad"
    ]
].mean().reset_index()

fig4 = px.line(
    resol,
    x="mes",
    y=[
        "% De remisiones",
        "Total  de resolutividad"
    ],
    markers=True
)

fig4.update_traces(
    mode="lines+markers+text",
    texttemplate="%{y:.1f}%",
    textposition="top center",
    line=dict(width=4),
    marker=dict(size=10)
)

fig4.data[0].line.color = "green"
fig4.data[0].marker.color = "green"

fig4.data[1].line.color = "deepskyblue"
fig4.data[1].marker.color = "deepskyblue"

fig4.update_layout(
    title={
        "text": "Comportamiento de Resolutividad y Remisiones",
        "x": 0.5
    },

    paper_bgcolor="#1E1E1E",
    plot_bgcolor="#1E1E1E",

    font=dict(
        color="white"
    ),

    legend=dict(
        font=dict(
            color="white",
            size=12
        ),

        title=dict(
            text="Indicadores",
            font=dict(
                color="white"
            )
        )
    ),

    xaxis=dict(
        title="Mes",
        color="white"
    ),

    yaxis=dict(
        title="Porcentaje (%)",
        color="white"
    ),

    height=650
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =====================================================
# INTERPRETACIÓN RESOLUTIVIDAD
# =====================================================

st.subheader("Interpretación Ejecutiva")

prom_rem = resol["% De remisiones"].mean()

prom_resol = resol["Total  de resolutividad"].mean()

texto_resol = f"""
Durante el periodo analizado, se observó un promedio de resolutividad
de {prom_resol:.1f}%, acompañado de un promedio de remisiones
de {prom_rem:.1f}%.

El comportamiento general evidencia estabilidad en la capacidad resolutiva
institucional.
"""

st.markdown(f"""
<div style="
background-color:#102030;
padding:20px;
border-radius:10px;
color:white;
font-size:17px;
line-height:1.8;
">

{texto_resol}

</div>
""", unsafe_allow_html=True)