import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from datetime import datetime

# Constantes
API_URL = "http://api.openweathermap.org/data/2.5/weather"
API_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
API_KEY = "1a316a90103fc496433cb58a974a17ff"
CONFIG_FILE = "config.json"


def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {"theme": "darkly"}


def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as archivo:
        json.dump(config, archivo)


def obtener_pronostico(ciudad, api_key=API_KEY, idioma="es"):
    try:
        params = {
            "q": ciudad,
            "appid": api_key,
            "units": "metric",
            "lang": idioma
        }
        respuesta = requests.get(API_FORECAST_URL, params=params)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error al conectar con la API: {e}")
        return None


def mostrar_pronostico(datos, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    if not datos or "list" not in datos:
        ttk.Label(frame, text="No se pudo obtener el pronóstico.", bootstyle="danger").pack(pady=10)
        return

    pronostico = datos["list"]
    dias_mostrados = 5
    for i in range(0, dias_mostrados * 8, 8):
        dia = pronostico[i]
        fecha_original = dia["dt_txt"].split(" ")[0]
        fecha_formateada = datetime.strptime(fecha_original, "%Y-%m-%d").strftime("%d/%m/%Y")
        temperatura = dia["main"]["temp"]
        descripcion = dia["weather"][0]["description"].capitalize()
        icono = dia["weather"][0]["icon"]

        url_icono = f"http://openweathermap.org/img/wn/{icono}@2x.png"
        respuesta_icono = requests.get(url_icono)
        imagen_icono = Image.open(BytesIO(respuesta_icono.content))
        imagen_icono = imagen_icono.resize((60, 60), Image.Resampling.LANCZOS)
        icono_tk = ImageTk.PhotoImage(imagen_icono)

        # Crear un frame para cada día
        dia_frame = ttk.Frame(frame, padding=10, bootstyle="secondary")
        dia_frame.pack(side="left", padx=20, pady=10)  # Espaciado entre cuadros

        # Centrar los elementos dentro del cuadro
        ttk.Label(
            dia_frame,
            text=fecha_formateada,
            font=("Arial", 10, "bold"),
            foreground="#FFA500",  # Color naranja para las fechas
            anchor="center",
            justify="center",
        ).pack(pady=5)
        ttk.Label(dia_frame, image=icono_tk).pack(pady=5)
        ttk.Label(dia_frame, text=f"{temperatura:.2f}°C", font=("Arial", 12), bootstyle="info", anchor="center").pack(pady=5)
        ttk.Label(
            dia_frame,
            text=descripcion,
            font=("Arial", 10),
            bootstyle="light",
            anchor="center",  # Centrar el texto
            justify="center",  # Asegurar que el texto esté centrado
        ).pack(pady=5)

        dia_frame.image = icono_tk


def interfaz_grafica():
    config = cargar_configuracion()
    tema_actual = config["theme"]

    # Crear la ventana principal
    ventana = ttk.Window(themename=tema_actual)
    ventana.title("Pronóstico del Clima")
    ventana.geometry("725x450")

    # Agregar el ícono a la ventana
    try:
        ventana.iconbitmap("Icono.ico") # Cambia "icono.png" por el nombre de tu archivo
    except Exception as e:
        print(f"No se pudo cargar el ícono: {e}")

    def consultar_pronostico():
        ciudad = entrada_ciudad.get().strip()
        if not ciudad:
            messagebox.showerror("Error", "Por favor, ingrese una ciudad.")
            return

        datos = obtener_pronostico(ciudad)
        if datos:
            mostrar_pronostico(datos, frame_pronostico)
        else:
            messagebox.showerror("Error", "No se pudo obtener el pronóstico.")

    def cambiar_tema(event):
        nuevo_tema = tema_seleccionado.get()
        ventana.style.theme_use(nuevo_tema)
        config["theme"] = nuevo_tema
        guardar_configuracion(config)

    etiqueta = ttk.Label(ventana, text="Ingrese el nombre de la ciudad:", font=("Arial", 12, "bold"))
    etiqueta.pack(pady=10)

    entrada_ciudad = ttk.Entry(ventana, width=30, bootstyle="info")
    entrada_ciudad.pack(pady=5)

    boton_consultar = ttk.Button(ventana, text="Consultar Pronóstico", command=consultar_pronostico, bootstyle="success")
    boton_consultar.pack(pady=10)

    tema_seleccionado = ttk.StringVar(value=tema_actual)
    temas_disponibles = ventana.style.theme_names()
    menu_temas = ttk.Combobox(
        ventana,
        textvariable=tema_seleccionado,
        values=temas_disponibles,
        state="readonly",
        bootstyle="info"
    )
    menu_temas.pack(pady=10)
    menu_temas.bind("<<ComboboxSelected>>", cambiar_tema)

    # Contenedor principal para centrar los cuadros
    frame_pronostico = ttk.Frame(ventana, padding=10, bootstyle="secondary")
    frame_pronostico.pack(pady=10, fill="x", anchor="center")

    ventana.mainloop()


if __name__ == "__main__":
    interfaz_grafica()