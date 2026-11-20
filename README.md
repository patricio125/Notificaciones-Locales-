# Notificaciones-Locales-
Manera local Lenguajes:Python y Sql

Copyright (c) 2026 Patricio Waston. Todos los derechos reservados / All Rights Reserved.

🇺🇸 Queda estrictamente prohibida la copia, modificación, distribución, sublicencia 
o uso comercial de este código fuente, total o parcialmente, sin el permiso 
previo y por escrito del autor. Este repositorio se publica únicamente con fines 
de visualización y evaluación de portafolio profesional.

🇦🇷 The copying, modification, distribution, sublicensing, or commercial use of 
this source code, in whole or in part, is strictly prohibited without the prior 
written permission of the author. This repository is published solely for 
visualization and professional portfolio evaluation purposes.

import os
import sqlite3
import random
import time
from datetime import datetime
from plyer import notification

# --- 1. DICCIONARIO DE NOTIFICACIONES POR HORARIO PICO ---
config_notificaciones = {
    "mañana": {
        "frases": {
            "es": [
                "☀️ ¡Buen día! Tu asistente de DyslexiaLiFT está listo.",
                "🎯 ¿Damos un paso más hoy? Repasemos tus objetivos.",
                "🚀 Un nuevo día para avanzar a tu propio ritmo. ¡Empecemos!"
            ],
            "en": [
                "☀️ Good morning! Your DyslexiaLiFT assistant is ready.",
                "🎯 Shall we take another step today? Let's review your goals.",
                "🚀 A new day to move at your own pace. Let's start!"
            ]
        },
        "horario": (8, 9)  # 08:00 AM - 09:00 AM
    },
    "mediodia": {
        "frases": {
            "es": [
                "📝 Es un excelente momento para practicar. Realizá tu test de hoy.",
                "💡 La constancia hace la diferencia. ¡Sumá unos minutos de práctica!",
                "⏳ Tómate un breve momento para realizar tu ejercicio de seguimiento."
            ],
            "en": [
                "📝 It's a great time to practice. Take today's test.",
                "💡 Consistency makes the difference. Add a few minutes of practice!",
                "⏳ Take a brief moment to complete your tracking exercise."
            ]
        },
        "horario": (12, 14)  # 12:00 PM - 02:00 PM
    },
    "tarde": {
        "frases": {
            "es": [
                "⭐ Inspirate con grandes casos de superación en la sección Famosos.",
                "🏆 Recordá que cada gran logro comenzó con la decisión de intentarlo.",
                "💪 Conocé cómo otros convirtieron sus desafíos en fortalezas."
            ],
            "en": [
                "⭐ Get inspired by great success stories in the Celebrities section.",
                "🏆 Remember that every great achievement started with the decision to try.",
                "💪 Learn how others turned their challenges into strengths."
            ]
        },
        "horario": (19, 21)  # 07:00 PM - 09:00 PM
    },
    "noche": {
        "frases": {
            "es": [
                "🌙 Has hecho un excelente trabajo hoy. ¡Que tengas un buen descanso!",
                "✨ Momento de desconectar. Mañana seguimos avanzando juntos.",
                "💤 Descansá bien, el aprendizaje también necesita su pausa."
            ],
            "en": [
                "🌙 You did a great job today. Have a good rest!",
                "✨ Time to disconnect. Tomorrow we keep moving forward together.",
                "💤 Rest well, learning also needs its break."
            ]
        },
        "horario": (22, 24)  # 10:00 PM - 12:00 AM
    }
}

ultima_categoria_lanzada = None


def _obtener_ruta_db(user_data_dir=None):
    """Devuelve la ruta de dyslexialift.db evitando caer en '.' sin permisos en Android."""
    if user_data_dir:
        return os.path.join(user_data_dir, "dyslexialift.db")

    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and getattr(app, "user_data_dir", None):
            return os.path.join(app.user_data_dir, "dyslexialift.db")
    except Exception:
        pass

    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    candidata = os.path.join(base_dir, "dyslexialift.db")
    if os.path.exists(candidata):
        return candidata

    return os.path.join(os.path.expanduser("~"), "dyslexialift.db")


def _asegurar_tabla_ajustes(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS ajustes (clave TEXT PRIMARY KEY, valor TEXT)")


def obtener_idioma_guardado(user_data_dir=None):
    """Lee el idioma activo guardado en la BD SQLite."""
    db_path = _obtener_ruta_db(user_data_dir)
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with sqlite3.connect(db_path, timeout=2.0) as cn:
            cur = cn.cursor()
            _asegurar_tabla_ajustes(cur)
            cur.execute("SELECT valor FROM ajustes WHERE clave = 'idioma'")
            row = cur.fetchone()
            if row and row[0]:
                return row[0].lower()
    except Exception as e:
        print(f"⚠️ Error leyendo idioma: {e}")

    return "es"


def _leer_ultima_categoria_guardada(user_data_dir=None):
    """Recupera la última categoría lanzada desde SQLite para evitar duplicados tras reinicios."""
    db_path = _obtener_ruta_db(user_data_dir)
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with sqlite3.connect(db_path, timeout=2.0) as cn:
            cur = cn.cursor()
            _asegurar_tabla_ajustes(cur)
            cur.execute("SELECT valor FROM ajustes WHERE clave = 'ultima_notif_cat'")
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
    except Exception as e:
        print(f"⚠️ Error leyendo última categoría: {e}")
    return None


def _guardar_ultima_categoria(categoria, user_data_dir=None):
    db_path = _obtener_ruta_db(user_data_dir)
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with sqlite3.connect(db_path, timeout=2.0) as cn:
            cur = cn.cursor()
            _asegurar_tabla_ajustes(cur)
            cur.execute(
                "INSERT OR REPLACE INTO ajustes (clave, valor) VALUES ('ultima_notif_cat', ?)",
                (categoria,),
            )
            cn.commit()
    except Exception as e:
        print(f"⚠️ Error guardando última categoría: {e}")


def verificar_y_lanzar_notificacion(dt=None, user_data_dir=None):
    global ultima_categoria_lanzada

    if ultima_categoria_lanzada is None:
        ultima_categoria_lanzada = _leer_ultima_categoria_guardada(user_data_dir)

    hora_actual = datetime.now().hour
    cat_encontrada = None

    for cat, datos in config_notificaciones.items():
        inicio, fin = datos["horario"]
        if inicio <= hora_actual < fin:
            cat_encontrada = cat
            break

    if cat_encontrada is None:
        if ultima_categoria_lanzada is not None:
            ultima_categoria_lanzada = None
            _guardar_ultima_categoria("", user_data_dir)
        return

    if cat_encontrada != ultima_categoria_lanzada:
        idioma = obtener_idioma_guardado(user_data_dir)
        frases_dict = config_notificaciones[cat_encontrada]["frases"]
        lista_frases = frases_dict.get(idioma, frases_dict.get("es", []))

        frase = random.choice(lista_frases) if lista_frases else "DyslexiaLiFT"

        try:
            notification.notify(
                title="DyslexiaLiFT",
                message=frase,
                app_name="DyslexiaLiFT",
                timeout=10
            )
            ultima_categoria_lanzada = cat_encontrada
            _guardar_ultima_categoria(cat_encontrada, user_data_dir)
            print(f"✅ Notificación lanzada [{cat_encontrada.upper()}] ({idioma.upper()}): {frase}")
        except Exception as e:
            print(f"⚠️ Error al lanzar notificación: {e}")


# Bucle de ejecución limpia si este archivo corre de forma independiente como servicio
if __name__ == "__main__":
    print("🚀 Servicio de Notificaciones iniciado sin interfaz gráfica.")
    verificar_y_lanzar_notificacion()
    while True:
        time.sleep(900)  # Revisa cada 15 minutos
        verificar_y_lanzar_notificacion()
