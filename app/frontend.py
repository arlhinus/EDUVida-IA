"""
Interfaz gráfica de Edu-vida con vista para Estudiantes, Profesores y Gráfico.
"""
import flet as ft
import flet_charts as fch
import requests

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "Edu-vida"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 450
    page.window_height = 750

    token_guardado = None
    rol_guardado = None
    codigo_guardado = None

    # ==========================================
    #  COMPONENTES DE LOGIN Y REGISTRO
    # ==========================================
    txt_codigo = ft.TextField(label="Código de estudiante", width=300)
    txt_password = ft.TextField(label="Contraseña", password=True, width=300)
    lbl_mensaje = ft.Text("", color=ft.Colors.RED)

    reg_nombres = ft.TextField(label="Nombres", width=300)
    reg_apellidos = ft.TextField(label="Apellidos", width=300)
    reg_rut = ft.TextField(label="RUT", width=300)
    reg_codigo = ft.TextField(label="Código de estudiante", width=300)
    reg_curso = ft.TextField(label="Curso", width=300)
    reg_password = ft.TextField(label="Contraseña", password=True, width=300)
    lbl_reg_mensaje = ft.Text("", color=ft.Colors.RED)

    # ==========================================
    #  COMPONENTES DE ESTUDIANTE
    # ==========================================
    txt_comentario = ft.TextField(label="¿Por qué te sientes así?", width=300, multiline=True)
    lbl_alerta = ft.Text("", weight=ft.FontWeight.BOLD, visible=False)
    slider_animo = ft.Slider(min=1, max=5, divisions=4, label="{value}", value=3, width=300)

    # ==========================================
    #  COMPONENTES DE PROFESOR
    # ==========================================
    lista_estudiantes = ft.Column(scroll=ft.ScrollMode.AUTO, height=500)
    lbl_bienvenida_profe = ft.Text("", theme_style=ft.TextThemeStyle.HEADLINE_SMALL)

    # ==========================================
    #  LÓGICA DE LOGIN
    # ==========================================
    def hacer_login(e):
        nonlocal token_guardado, rol_guardado, codigo_guardado
        try:
            response = requests.post(
                f"{API_URL}/usuarios/login",
                json={"codigo": txt_codigo.value, "password": txt_password.value}
            )
            
            if response.status_code == 200:
                data = response.json()
                token_guardado = data["access_token"]
                rol_guardado = data["usuario"]["rol"]
                codigo_guardado = data["usuario"]["codigo"]
                
                if rol_guardado == "estudiante":
                    mostrar_pantalla_animo()
                else:
                    mostrar_pantalla_profesor()
            else:
                lbl_mensaje.value = "Código o contraseña incorrectos"
                lbl_mensaje.color = ft.Colors.RED
                page.update()
        except Exception as ex:
            lbl_mensaje.value = "Error de conexión. ¿Está encendido Uvicorn?"
            page.update()

    # ==========================================
    #  LÓGICA ESTUDIANTE
    # ==========================================
    def registrar_animo(e):
        if not token_guardado: return
        headers = {"Authorization": f"Bearer {token_guardado}"}
        
        nivel_seleccionado = slider_animo.value if slider_animo.value is not None else 3
        data = {"nivel_animo": int(nivel_seleccionado), "comentario": txt_comentario.value}
        
        try:
            response = requests.post(f"{API_URL}/animo/registrar", json=data, headers=headers)
            if response.status_code == 201:
                res_data = response.json()
                lbl_alerta.visible = True
                if res_data.get("alerta"):
                    lbl_alerta.value = res_data["alerta"]["mensaje"]
                    lbl_alerta.color = ft.Colors.RED
                else:
                    lbl_alerta.value = "¡Ánimo registrado con éxito!"
                    lbl_alerta.color = ft.Colors.GREEN
                page.update()
        except Exception as ex:
            print(ex)

    def mostrar_grafico(e):
        if not token_guardado: return
        headers = {"Authorization": f"Bearer {token_guardado}"}
        
        try:
            response = requests.get(f"{API_URL}/animo/historial/{codigo_guardado}", headers=headers)
            if response.status_code == 200:
                historial = response.json()
                page.clean()
                
                contenedor_grafico = ft.Container(height=300, width=350)
                controles = [
                    ft.Text("Mi Progreso Emocional", theme_style=ft.TextThemeStyle.HEADLINE_SMALL, weight=ft.FontWeight.BOLD),
                    ft.Text("Tus últimos registros:", size=14),
                    ft.Divider(),
                ]

                if not historial:
                    controles.append(ft.Text("Aún no tienes registros de ánimo."))
                else:
                    ultimos = historial[:7]
                    ultimos.reverse()
                    
                    puntos = []
                    for i, h in enumerate(ultimos):
                        nivel = h.get("nivel_animo", 3)
                        y_val = nivel - 1
                        puntos.append(fch.LineChartDataPoint(i, y_val))

                    if len(puntos) == 1:
                        puntos.append(fch.LineChartDataPoint(1, puntos[0].y))
                    elif len(puntos) == 0:
                        puntos.append(fch.LineChartDataPoint(0, 0))
                        puntos.append(fch.LineChartDataPoint(1, 1))

                    labels_y = [
                        fch.ChartAxisLabel(value=0, label=ft.Text("1", size=12)),
                        fch.ChartAxisLabel(value=1, label=ft.Text("2", size=12)),
                        fch.ChartAxisLabel(value=2, label=ft.Text("3", size=12)),
                        fch.ChartAxisLabel(value=3, label=ft.Text("4", size=12)),
                        fch.ChartAxisLabel(value=4, label=ft.Text("5", size=12)),
                    ]
                    
                    # 👇 CAMBIO: Etiquetas del Eje X con las fechas reales 👇
                    labels_x = [
                        fch.ChartAxisLabel(
                            value=i, 
                            label=ft.Text(h.get("fecha", "")[8:10] + "/" + h.get("fecha", "")[5:7], size=10)
                        )
                        for i, h in enumerate(ultimos)
                    ]

                    grafico = fch.LineChart(
                        data_series=[fch.LineChartData(points=puntos, color=ft.Colors.BLUE)],
                        min_y=0, max_y=4, min_x=0, max_x=max(1, len(puntos) - 1),
                        left_axis=fch.ChartAxis(label_size=30, labels=labels_y),
                        bottom_axis=fch.ChartAxis(label_size=30, labels=labels_x),
                        expand=True,
                    )
                    
                    contenedor_grafico.content = grafico
                    controles.append(contenedor_grafico)
                    controles.append(ft.Text("Eje X: Fechas de registro | Eje Y: Nivel de ánimo (1 a 5)", size=10, color=ft.Colors.GREY))

                controles.append(ft.Button("Volver", on_click=lambda _: mostrar_pantalla_animo()))
                page.add(ft.Column(controles, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                page.update()
        except Exception as ex:
            print(f"Error al generar gráfico: {ex}")

    # ==========================================
    #  LÓGICA PROFESOR
    # ==========================================
    def ver_historial_estudiante(e, estudiante_codigo, estudiante_nombre):
        headers = {"Authorization": f"Bearer {token_guardado}"}
        try:
            response = requests.get(f"{API_URL}/animo/historial/{estudiante_codigo}", headers=headers)
            if response.status_code == 200:
                historial = response.json()
                page.clean()
                
                controles = [
                    ft.Text(f"Historial de: {estudiante_nombre}", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                    ft.Text(f"Código: {estudiante_codigo}", size=12, color=ft.Colors.GREY),
                    ft.Divider(),
                ]
                
                alertas_bajas = [h for h in historial if h.get("nivel_animo") is not None and h["nivel_animo"] <= 2] if historial else []
                
                if len(alertas_bajas) >= 3:
                    controles.append(
                        ft.Container(
                            content=ft.Text("⚠️ ALERTA: Varios registros de ánimo bajo recientes.", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED, padding=10, border_radius=5
                        )
                    )
                    controles.append(ft.Divider())

                if historial:
                    ultimos = historial[:7]
                    ultimos.reverse()
                    
                    puntos = []
                    for i, h in enumerate(ultimos):
                        nivel = h.get("nivel_animo", 3)
                        puntos.append(fch.LineChartDataPoint(i, nivel - 1))

                    if len(puntos) == 1:
                        puntos.append(fch.LineChartDataPoint(1, puntos[0].y))

                    labels_y = [
                        fch.ChartAxisLabel(value=0, label=ft.Text("1", size=12)),
                        fch.ChartAxisLabel(value=1, label=ft.Text("2", size=12)),
                        fch.ChartAxisLabel(value=2, label=ft.Text("3", size=12)),
                        fch.ChartAxisLabel(value=3, label=ft.Text("4", size=12)),
                        fch.ChartAxisLabel(value=4, label=ft.Text("5", size=12)),
                    ]
                    
                    # 👇 CAMBIO: Etiquetas del Eje X con las fechas reales 👇
                    labels_x = [
                        fch.ChartAxisLabel(
                            value=i, 
                            label=ft.Text(h.get("fecha", "")[8:10] + "/" + h.get("fecha", "")[5:7], size=10)
                        )
                        for i, h in enumerate(ultimos)
                    ]

                    grafico = fch.LineChart(
                        data_series=[fch.LineChartData(points=puntos, color=ft.Colors.BLUE)],
                        min_y=0, max_y=4, min_x=0, max_x=max(1, len(puntos) - 1),
                        left_axis=fch.ChartAxis(label_size=30, labels=labels_y),
                        bottom_axis=fch.ChartAxis(label_size=30, labels=labels_x),
                        expand=True,
                    )
                    
                    contenedor_grafico = ft.Container(height=200, width=350, content=grafico)
                    controles.append(ft.Text("Progreso reciente:", weight=ft.FontWeight.BOLD))
                    controles.append(contenedor_grafico)
                    controles.append(ft.Text("Eje X: Fechas de registro | Eje Y: Nivel de ánimo (1 a 5)", size=10, color=ft.Colors.GREY))
                    controles.append(ft.Divider())

                if not historial:
                    controles.append(ft.Text("El estudiante no tiene registros aún."))
                else:
                    for h in historial:
                        nivel = h.get("nivel_animo", 0)
                        color_nivel = ft.Colors.GREEN if nivel >= 4 else (ft.Colors.ORANGE if nivel == 3 else ft.Colors.RED)
                        controles.append(
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.MOOD, color=color_nivel),
                                title=ft.Text(f"Nivel: {nivel}/5"),
                                subtitle=ft.Text(f"{h.get('comentario') or 'Sin comentario'}\nFecha: {h.get('fecha', '')[:10]}"),
                            )
                        )

                controles.append(ft.Button("Volver al Panel", on_click=lambda _: mostrar_pantalla_profesor()))
                page.add(ft.Column(controles, scroll=ft.ScrollMode.AUTO, expand=True))
                page.update()
        except Exception as ex:
            print(f"Error en historial: {ex}")

    def cargar_lista_estudiantes():
        headers = {"Authorization": f"Bearer {token_guardado}"}
        try:
            response = requests.get(f"{API_URL}/usuarios/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                lista_estudiantes.controls.clear()
                
                if not estudiantes:
                    lista_estudiantes.controls.append(ft.Text("No hay estudiantes registrados."))
                else:
                    for est in estudiantes:
                        res_hist = requests.get(f"{API_URL}/animo/historial/{est['codigo']}", headers=headers)
                        tiene_alerta = False
                        if res_hist.status_code == 200:
                            historial = res_hist.json()
                            if historial:
                                alertas_bajas = [h for h in historial if h.get("nivel_animo") is not None and h["nivel_animo"] <= 2]
                                if len(alertas_bajas) >= 3:
                                    tiene_alerta = True
                                
                        texto_boton = f"⚠️ {est['nombres']} {est['apellidos']} (¡Alerta!)" if tiene_alerta else f"{est['nombres']} {est['apellidos']} ({est['codigo']})"
                        color_boton = ft.Colors.RED if tiene_alerta else ft.Colors.BLUE
                        
                        btn = ft.Button(
                            texto_boton,
                            on_click=lambda e, c=est['codigo'], n=f"{est['nombres']} {est['apellidos']}": ver_historial_estudiante(e, c, n),
                            bgcolor=color_boton, color=ft.Colors.WHITE
                        )
                        lista_estudiantes.controls.append(btn)
                page.update()
        except Exception as ex:
            print(f"Error al cargar estudiantes: {ex}")

    # ==========================================
    #  VISTAS (PANTALLAS)
    # ==========================================
    def mostrar_pantalla_animo():
        page.clean()
        page.add(
            ft.Text(f"¡Hola, {codigo_guardado}!", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("¿Cómo te sientes hoy?", theme_style=ft.TextThemeStyle.HEADLINE_SMALL, weight=ft.FontWeight.BOLD),
            slider_animo,
            txt_comentario,
            ft.Button("Registrar Ánimo", on_click=registrar_animo, width=300),
            ft.Button("Ver mi progreso 📈", on_click=mostrar_grafico, width=300, bgcolor=ft.Colors.BLUE_200),
            lbl_alerta,
            ft.TextButton("Cerrar Sesión", on_click=lambda _: cerrar_sesion())
        )
        page.update()

    def mostrar_pantalla_profesor():
        page.clean()
        lbl_bienvenida_profe.value = f"Panel de Profesor - Código: {codigo_guardado}"
        cargar_lista_estudiantes() 
        
        page.add(
            ft.Text("Edu-vida - Panel Docente", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
            lbl_bienvenida_profe,
            ft.Divider(),
            ft.Text("Selecciona un estudiante para ver su historial:", weight=ft.FontWeight.BOLD),
            lista_estudiantes,
            ft.TextButton("Cerrar Sesión", on_click=lambda _: cerrar_sesion())
        )
        page.update()

    def hacer_registro(e):
        try:
            nuevo_usuario = {
                "rol": "estudiante", 
                "codigo": reg_codigo.value, "nombres": reg_nombres.value, "apellidos": reg_apellidos.value,
                "rut": reg_rut.value, "curso": reg_curso.value, "password": reg_password.value,
                "cumpleanos": None, "necesidades_medicas": None
            }
            response = requests.post(f"{API_URL}/usuarios/registro", json=nuevo_usuario)
            if response.status_code == 201:
                lbl_reg_mensaje.value = "¡Cuenta creada! Ya puedes iniciar sesión."
                lbl_reg_mensaje.color = ft.Colors.GREEN
            else:
                lbl_reg_mensaje.value = response.json().get("detail", "Error")
                lbl_reg_mensaje.color = ft.Colors.RED
            page.update()
        except Exception as ex:
            lbl_reg_mensaje.value = f"Error: {ex}"

    def mostrar_pantalla_registro():
        page.clean()
        page.add(
            ft.Text("Crear una cuenta", theme_style=ft.TextThemeStyle.HEADLINE_SMALL, weight=ft.FontWeight.BOLD),
            reg_nombres, reg_apellidos, reg_rut, reg_codigo, reg_curso, reg_password,
            ft.Button("Registrarse", on_click=hacer_registro, width=300),
            lbl_reg_mensaje,
            ft.TextButton("Volver al Login", on_click=lambda _: mostrar_pantalla_login())
        )
        page.update()

    def cerrar_sesion():
        nonlocal token_guardado, rol_guardado, codigo_guardado
        token_guardado = None
        rol_guardado = None
        codigo_guardado = None
        txt_codigo.value = ""
        txt_password.value = ""
        mostrar_pantalla_login()

    def mostrar_pantalla_login():
        page.clean()
        page.add(login_view)
        page.update()

    # ==========================================
    #  DISEÑO DE LOGIN
    # ==========================================
    login_view = ft.Column(
        [
            ft.Icon(ft.Icons.SCHOOL, size=80, color=ft.Colors.BLUE),
            ft.Text("Edu-vida", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
            ft.Text("Bienestar Estudiantil", size=16),
            ft.Divider(),
            txt_codigo,
            txt_password,
            ft.Button("Iniciar Sesión", on_click=hacer_login, width=300),
            lbl_mensaje,
            ft.TextButton("¿No tienes cuenta? Regístrate aquí", on_click=lambda _: mostrar_pantalla_registro())
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(login_view)

# Ejecutamos la app en modo ventana de escritorio
ft.run(main)