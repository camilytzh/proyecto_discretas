import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF

root = tk.Tk()
root.title("Interés compuesto y amortización francesa")
root.configure(bg="#7cb0ff")

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla  = root.winfo_screenheight()
nuevo_ancho = int(ancho_pantalla * 0.6)
nuevo_alto  = int(alto_pantalla * 0.8)
pos_x = (ancho_pantalla - nuevo_ancho) // 2
pos_y = (alto_pantalla - nuevo_alto) // 2
root.geometry(f"{nuevo_ancho}x{nuevo_alto}+{pos_x}+{pos_y}")
root.resizable(1, 1)

TITLE = tk.Label(root, text="SIMULACIÓN DE PRÉSTAMO BANCARIO",
                 bg="#033888", font=('Arial black', 23), fg="#ffffff")
TITLE.pack(pady=10, fill="x")

tasa_mensual = tk.DoubleVar(value=0.0)
tipo_prestamo_text = tk.StringVar(value="No seleccionado")
DTI_message = tk.StringVar(value=" ")
origen_credito = tk.StringVar(value="banco")

TASAS_BCE = {
    "Productivos": {
        "Productivo Corporativo": 11.05,
        "Productivo Empresarial": 12.83,
        "Productivo PYMES": 12.29
    },
    "Consumo": {
        "Consumo": 16.77,
    },
    "Educacion": {
        "Educativo": 9.50,
        "Educativo Social": 7.50
    },
    "Vivienda": {
        "Vivienda de Interés Público": 4.99,
        "Vivienda de Interés Social": 4.99
    },
    "Inmobiliario y Público": {
        "Inmobiliario": 10.73,
        "Inversión Pública": 9.33
    },
    "Microcrédito": {
        "Microcrédito Minorista": 28.23,
        "Microcrédito Acumulación Simple": 24.89,
        "Microcrédito Acumulación Ampliada": 22.05
    }
}

AUMENTO_POR_TIPO_Y_CATEGORIA = {
    "Productivos": {"A-1":1,"A-2":2,"A-3":4,"B-1":7,"B-2":15,"C-1":30,"C-2":50,"D":80,"E":100},
    "Consumo": {"A-1":1,"A-2":2,"A-3":5,"B-1":9,"B-2":19,"C-1":39,"C-2":59,"D":99,"E":100},
    "Educacion": {"A-1":1,"A-2":2,"A-3":4,"B-1":7,"B-2":15,"C-1":30,"C-2":50,"D":80,"E":100},
    "Vivienda": {"A-1":1,"A-2":2,"A-3":4,"B-1":8,"B-2":17,"C-1":35,"C-2":55,"D":90,"E":100},
    "Microcrédito": {"A-1":1,"A-2":2,"A-3":5,"B-1":10,"B-2":20,"C-1":40,"C-2":60,"D":99,"E":100},
    "Inmobiliario y Público": {"A-1":1,"A-2":2,"A-3":4,"B-1":8,"B-2":16,"C-1":30,"C-2":50,"D":85,"E":100},
}

CATEGORIAS_CREDITICIAS = ["A-1","A-2","A-3","B-1","B-2","C-1","C-2","D","E"]

def calcular_tasa_desgravamen(edad):
    if edad < 30: return 0.0010
    elif edad <= 60: return 0.0013
    else: return 0.0018

def calcular_tasa_incendio(incluye_terremoto=True, incluye_robo=False):
    tasa = 0.0004
    if incluye_terremoto: tasa += 0.00005
    if incluye_robo: tasa += 0.00005
    return tasa

def cuota_francesa(P, i, n):
    return P * (i * (1 + i) ** n) / ((1 + i) ** n - 1)

def interes_periodo(Pk, r_anual, n_por_anio=12):
    return Pk * (r_anual/100) / n_por_anio

def clasificar_dti(dti):
    if dti < 20: return "Excelente (riesgo bajo)"
    elif dti < 36: return "Buena capacidad (riesgo medio)"
    elif dti < 43: return "Aceptable (riesgo alto)"
    else: return "Riesgo crítico (posible rechazo)"

frm = tk.Frame(root, bg="#7cb0ff")
frm.pack(pady=8)

def etiqueta(parent, texto):
    return tk.Label(parent, text=texto, bg="#7cb0ff", font=('Verdana',10))

col1 = tk.Frame(frm, bg="#7cb0ff"); col1.grid(row=0, column=0, padx=10, sticky="n")
etiqueta(col1, "Ingreso mensual ($):").pack(anchor="w")
entry_ingreso = tk.Entry(col1); entry_ingreso.pack(pady=3, fill="x")

etiqueta(col1, "Gastos mensuales ($):").pack(anchor="w")
entry_gastos = tk.Entry(col1); entry_gastos.pack(pady=3, fill="x")

etiqueta(col1, "Monto del préstamo ($):").pack(anchor="w")
entry_monto = tk.Entry(col1); entry_monto.pack(pady=3, fill="x")

etiqueta(col1, "Plazo (meses):").pack(anchor="w")
entry_plazo = tk.Entry(col1); entry_plazo.pack(pady=3, fill="x")

col2 = tk.Frame(frm, bg="#7cb0ff"); col2.grid(row=0, column=1, padx=10, sticky="n")
etiqueta(col2, "Tipo general de crédito:").pack(anchor="w")
combo_categoria = ttk.Combobox(col2, values=list(TASAS_BCE.keys()), state="readonly", width=28)
combo_categoria.pack(pady=3, fill="x")

etiqueta(col2, "Tipo específico:").pack(anchor="w")
combo_tipo = ttk.Combobox(col2, values=[], state="readonly", width=28)
combo_tipo.pack(pady=3, fill="x")

label_seleccion = tk.Label(col2, textvariable=tipo_prestamo_text, bg="#7cb0ff",
                           fg="white", font=('Verdana', 9, 'italic'))
label_seleccion.pack(pady=4, anchor="w")

etiqueta(col2, "Categoría crediticia (A-1…E):").pack(anchor="w")
combo_categoria_crediticia = ttk.Combobox(col2, values=CATEGORIAS_CREDITICIAS, state="readonly", width=10)
combo_categoria_crediticia.pack(pady=3, anchor="w")

col3 = tk.Frame(frm, bg="#7cb0ff"); col3.grid(row=0, column=2, padx=10, sticky="n")
etiqueta(col3, "Edad:").pack(anchor="w")
entry_edad = tk.Entry(col3); entry_edad.pack(pady=3, fill="x")

var_terremoto = tk.BooleanVar(value=False)
var_robo      = tk.BooleanVar(value=False)
tk.Checkbutton(col3, text="Cobertura Terremoto", variable=var_terremoto, bg="#7cb0ff").pack(anchor="w")
tk.Checkbutton(col3, text="Cobertura Robo", variable=var_robo, bg="#7cb0ff").pack(anchor="w")

sep = tk.Label(col3, text="--- Seguros a incluir ---", bg="#7cb0ff", font=('Verdana',9,'bold'))
sep.pack(anchor="w", pady=(6,0))
var_inc_desgrav = tk.BooleanVar(value=False)
var_inc_incend  = tk.BooleanVar(value=False)
tk.Checkbutton(col3, text="Incluir Seguro Desgravamen", variable=var_inc_desgrav, bg="#7cb0ff").pack(anchor="w")
tk.Checkbutton(col3, text="Incluir Seguro Incendios", variable=var_inc_incend, bg="#7cb0ff").pack(anchor="w")

etiqueta(col3, "Valor del inmueble ($):").pack(anchor="w")
entry_valor_inmueble = tk.Entry(col3); entry_valor_inmueble.pack(pady=3, fill="x")
entry_valor_inmueble.configure(state="disabled")

def on_select_categoria(event=None):
    cat = combo_categoria.get()
    if not cat: return
    combo_tipo['values'] = list(TASAS_BCE[cat].keys())
    combo_tipo.set("")
    tipo_prestamo_text.set("No seleccionado")
    tasa_mensual.set(0.0)
    if cat in ["Vivienda", "Inmobiliario y Público"]:
        entry_valor_inmueble.configure(state="normal")
    else:
        entry_valor_inmueble.configure(state="disabled")

combo_categoria.bind("<<ComboboxSelected>>", on_select_categoria)

def on_select_tipo(event=None):
    cat = combo_categoria.get()
    tipo = combo_tipo.get()
    if cat and tipo:
        tasa_anual = TASAS_BCE[cat][tipo]
        tasa_mensual.set((tasa_anual/100)/12)
        tipo_prestamo_text.set(f"{tipo} ({tasa_anual:.2f}% anual)")

combo_tipo.bind("<<ComboboxSelected>>", on_select_tipo)

label_dti = tk.Label(root, text="", bg="#7cb0ff", font=("Verdana", 10))
label_dti.pack(pady=4)

columnas = ("Mes","Cuota S/S","Interés","Amort.","Saldo","Seguro D","Seguro I","Cuota C/S","Cuota+Seguro")
tabla_frame = tk.Frame(root, bg="#7cb0ff")
tabla_frame.pack(pady=8, fill="both", expand=True)

tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=18)
for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, anchor="center", width=120)
tabla.pack(side="left", fill="both", expand=True)

scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
scroll_x = ttk.Scrollbar(root, orient="horizontal", command=tabla.xview)
tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(fill="x")

def calcular():
    try:
        P = float(entry_monto.get())
        t_meses = int(entry_plazo.get())
        ingreso = float(entry_ingreso.get())
        gastos = float(entry_gastos.get())
        edad = int(entry_edad.get())
    except ValueError:
        messagebox.showerror("Error", "Verifica que monto, plazo, ingreso, gastos y edad, sean valores numéricos.")
        return

    if not combo_categoria.get() or not combo_tipo.get() or not combo_categoria_crediticia.get():
        messagebox.showerror("Error", "Selecciona tipo general, tipo específico y categoría crediticia.")
        return

    tipo_general = combo_categoria.get()
    tipo_especifico = combo_tipo.get()
    r_anual_base = TASAS_BCE[tipo_general][tipo_especifico]  
    cat_cred = combo_categoria_crediticia.get()
    aumento_pct = AUMENTO_POR_TIPO_Y_CATEGORIA.get(tipo_general, {}).get(cat_cred, 0)
    r_anual_final = r_anual_base * (1 + aumento_pct/100.0)  
    r_mensual = (r_anual_final/100.0)/12

    if tipo_general in ["Vivienda", "Inmobiliario y Público"]:
        try:
            valor_inmueble = float(entry_valor_inmueble.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese el valor del inmueble.")
            return
    else:
        valor_inmueble = P

    tasa_desgravamen = calcular_tasa_desgravamen(edad)
    tasa_incendio = calcular_tasa_incendio(var_terremoto.get(), var_robo.get())

    if r_mensual <= 0:
        messagebox.showerror("Error", "La tasa resultante debe ser mayor que 0.")
        return

    R_sin_seguro = cuota_francesa(P, r_mensual, t_meses)

    dti = ((gastos + R_sin_seguro)/ingreso)*100 if ingreso>0 else 999

    label_dti.config(text=f"DTI proyectado: {dti:.2f}% → {clasificar_dti(dti)}")
    Sg_mensual = (P * tasa_desgravamen)/t_meses if var_inc_desgrav.get() else 0.0
    Si_mensual = (valor_inmueble * tasa_incendio)/t_meses if var_inc_incend.get() else 0.0
    cuota_total_fija = R_sin_seguro + Sg_mensual + Si_mensual

    for item in tabla.get_children():
        tabla.delete(item)

    saldo = P
    for k in range(1, t_meses+1):
        Ik = interes_periodo(saldo, r_anual_final, 12)
        Ak = R_sin_seguro - Ik
        saldo = max(saldo - Ak, 0.0)

        cuota_con_seguro_mes = R_sin_seguro + Sg_mensual + Si_mensual

        tabla.insert("", "end", values=(
            k,
            f"{R_sin_seguro:,.2f}",
            f"{Ik:,.2f}",
            f"{Ak:,.2f}",
            f"{saldo:,.2f}",
            f"{Sg_mensual:,.2f}",
            f"{Si_mensual:,.2f}",
            f"{cuota_con_seguro_mes:,.2f}",
            f"{cuota_total_fija:,.2f}"
        ))

def exportar_pdf():
    datos = [tabla.item(item)["values"] for item in tabla.get_children()]
    if not datos:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
        return

    ruta = filedialog.asksaveasfilename(defaultextension=".pdf",
                                        filetypes=[("PDF files","*.pdf")],
                                        title="Guardar tabla como PDF")
    if not ruta: return

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Simulacion de Prestamo - Amortizacion Francesa", ln=1, align="C")
    pdf.set_font("Arial", "", 8)

    col_widths = [22, 28, 28, 28, 28, 28, 28, 28, 32]
    for encabezado, w in zip(columnas, col_widths):
        pdf.cell(w, 8, str(encabezado), border=1, align="C")
    pdf.ln()

    for fila in datos:
        for celda, w in zip(fila, col_widths):
            pdf.cell(w, 7, str(celda), border=1, align="C")
        pdf.ln()

    pdf.output(ruta)
    messagebox.showinfo("Éxito", f"PDF guardado en:\n{ruta}")

boton_frame = tk.Frame(root, bg="#7cb0ff")
boton_frame.pack(pady=6)

btn_calc = tk.Button(boton_frame, text="Calcular amortización",
                     command=calcular, bg="#004aad", fg="white",
                     font=('Verdana', 12), padx=10, pady=5)
btn_calc.grid(row=0, column=0, padx=6)

btn_pdf = tk.Button(boton_frame, text="Exportar a PDF",
                    command=exportar_pdf, bg="#4CAF50", fg="white",
                    font=('Verdana', 12), padx=10, pady=5)
btn_pdf.grid(row=0, column=1, padx=6)


root.mainloop()


