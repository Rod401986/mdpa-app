import streamlit as st
from datetime import datetime, date
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- FUNCIONES ----------------

def clasificar_mdpa(pas, pad):
    if pas < 135 and pad < 85:
        return "Normotenso en MDPA"
    else:
        return "Hipertensión no controlada en MDPA"


def calcular_promedio(registros):
    # descarta día 1
    filtrados = [r for r in registros if r[0] != 1]

    pas = [r[1] for r in filtrados]
    pad = [r[2] for r in filtrados]

    return sum(pas)/len(pas), sum(pad)/len(pad), filtrados


def generar_pdf(texto):
    file_path = "informe_mdpa.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    contenido = []
    for linea in texto.split("\n"):
        contenido.append(Paragraph(linea, styles["Normal"]))

    doc.build(contenido)
    return file_path


# ---------------- INTERFAZ ----------------

st.title("📱 Control de Presión Arterial en Casa")

st.markdown("Complete sus datos y registre su presión durante 7 días.")

st.info("""
Indicaciones:
- Realizar 2 mediciones por la mañana y 2 por la noche
- Permanecer en reposo 5 minutos antes
- No hablar durante la medición
- Registrar durante 7 días consecutivos
""")

# -------- DATOS PACIENTE --------

nombre = st.text_input("Nombre completo")
dni = st.text_input("DNI")
fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(1900,1,1))

# cálculo automático edad
hoy = date.today()
edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

institucion = "Consultorio Pulsar"

st.subheader("Carga de presión arterial (7 días)")

registros = []

for dia in range(1, 8):
    st.markdown(f"### Día {dia}")

    for momento in ["Mañana", "Noche"]:
        col1, col2 = st.columns(2)

        pas1 = col1.number_input(f"{momento} PAS 1 (día {dia})", key=f"pas1_{dia}_{momento}")
        pad1 = col2.number_input(f"{momento} PAD 1 (día {dia})", key=f"pad1_{dia}_{momento}")

        pas2 = col1.number_input(f"{momento} PAS 2 (día {dia})", key=f"pas2_{dia}_{momento}")
        pad2 = col2.number_input(f"{momento} PAD 2 (día {dia})", key=f"pad2_{dia}_{momento}")

        registros.append((dia, pas1, pad1))
        registros.append((dia, pas2, pad2))


# -------- BOTÓN --------

if st.button("Generar informe MDPA"):

    prom_pas, prom_pad, filtrados = calcular_promedio(registros)
    clasificacion = clasificar_mdpa(prom_pas, prom_pad)

    fecha = datetime.now().strftime("%d/%m/%Y")

    informe = f"""
INFORME DE MONITOREO DOMICILIARIO DE PRESIÓN ARTERIAL (MDPA)

Institución: {institucion}
Fecha: {fecha}

DATOS DEL PACIENTE
Nombre: {nombre}
DNI: {dni}
Fecha de nacimiento: {fecha_nac}
Edad: {edad} años

METODOLOGÍA
Registro domiciliario de presión arterial durante 7 días consecutivos,
con 2 mediciones matutinas y 2 vespertinas.
Se descartan las mediciones del primer día para el análisis.

RESULTADOS
Promedio de presión arterial:
- Sistólica: {prom_pas:.1f} mmHg
- Diastólica: {prom_pad:.1f} mmHg

INTERPRETACIÓN
{clasificacion}

CRITERIOS UTILIZADOS
Valores de referencia para MDPA:
- Normal: <135/85 mmHg
- Hipertensión: ≥135/85 mmHg

CONCLUSIÓN
Se sugiere correlacionar con evaluación clínica y conducta terapéutica.

--------------------------------------------------
Firma y sello médico
"""

    # Mostrar informe
    st.text_area("Informe generado", informe, height=300)

    # -------- GRÁFICO --------
    dias = list(range(1, len(filtrados)+1))
    pas_vals = [r[1] for r in filtrados]
    pad_vals = [r[2] for r in filtrados]

    plt.figure()
    plt.plot(dias, pas_vals, label="PAS")
    plt.plot(dias, pad_vals, label="PAD")
    plt.xlabel("Mediciones (sin día 1)")
    plt.ylabel("mmHg")
    plt.legend()

    st.pyplot(plt)

    # -------- PDF --------
    pdf = generar_pdf(informe)

    with open(pdf, "rb") as f:
        st.download_button("📄 Descargar PDF", f, file_name="informe_mdpa.pdf")
