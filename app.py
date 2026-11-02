import streamlit as st
import base64
from PIL import Image
from estructuras import ObjetoPerdido, ListaEnlazadaObjetos, TablaHashObjetos, PilaHistorial, ColaReclamos

# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(page_title="Objetos Perdidos y Encontrados - Universidad", layout="wide", page_icon="🎓")

# --- DISEÑO GLOBAL Y VISUALES (CSS + FONTAWESOME) ---
st.markdown("""
    <style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    .main {
        background-color: #F8F9FA;
    }
    
    /* Estilo del botón verde desplegable de Publicación */
    [data-testid="stExpander"] summary {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px;
        padding: 12px 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    [data-testid="stExpander"] summary:hover {
        background-color: #1B5E20 !important;
    }
    [data-testid="stExpander"] summary p {
        color: white !important;
        font-weight: bold;
        font-size: 16px;
    }

    /* Contenedores de Tarjetas (Cards) elegantes */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-radius: 10px;
        border: 1px solid #E0E0E0 !important;
        padding: 15px;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }

    /* Estilización general de Botones de Acción */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        padding: 0.4rem 1rem;
    }

    /* Estilo especial para los botones de Navegación en la Barra Lateral */
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #FFFFFF;
        color: #2E7D32;
        border: 1px solid #A5D6A7;
        font-weight: 600;
        text-align: left;
        padding: 12px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #E8F5E9;
        border-color: #2E7D32;
        color: #1B5E20;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR ESTRUCTURAS EN LA SESIÓN ---
if 'lista_objetos' not in st.session_state:
    st.session_state.lista_objetos = ListaEnlazadaObjetos()
    st.session_state.tabla_hash = TablaHashObjetos()
    st.session_state.pila_historial = PilaHistorial()
    st.session_state.cola_reclamos = ColaReclamos()

    st.session_state.usuarios_db = {"admin@uni.edu": "1234"}
    
    st.session_state.autenticado = False
    st.session_state.usuario_actual = ""
    st.session_state.form_abierto = False
    st.session_state.expander_key = 0

# Asegurar que la vista actual esté inicializada
if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = "🏠 Inicio / Búsqueda"

    # Datos de prueba iniciales
    obj_prueba = ObjetoPerdido("OBJ-001", "Calculadora Casio", "Útiles", "2026-06-01", "10:30", "Aula 204", "ENCONTRADO", "Juan Pérez", "Tel: 0981123456 | Obs: Encontrada cerca de la pizarra", None)
    st.session_state.lista_objetos.agregar(obj_prueba)
    st.session_state.tabla_hash.insertar(obj_prueba)
    st.session_state.pila_historial.apilar("Se registró el objeto OBJ-001")

# --- BARRA LATERAL: ACCESO DE PERSONAL Y NAVEGACIÓN ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <i class="fa-solid fa-right-to-bracket" style="font-size: 2.5rem; color: #8BC34A;"></i>
            <h3 style="color: white; margin: 10px 0 0 0; font-size: 1.2rem;">Panel de Control</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔐 Acceso de Personal", expanded=True):
        tab_login_lat, tab_reg_lat = st.tabs(["🔑 Ingresar", "📝 Registrarse"])
        
        with tab_login_lat:
            with st.form("form_login_lateral"):
                c_correo = st.text_input("Correo electrónico")
                c_pass = st.text_input("Contraseña", type="password")
                btn_ingresar = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                
                if btn_ingresar:
                    if c_correo in st.session_state.usuarios_db and st.session_state.usuarios_db[c_correo] == c_pass:
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = c_correo
                        st.success("¡Bienvenido!")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
                        
        with tab_reg_lat:
            with st.form("form_registro_lateral", clear_on_submit=True):
                nuevo_correo = st.text_input("Nuevo correo")
                nuevo_pass = st.text_input("Crear contraseña", type="password")
                conf_pass = st.text_input("Repetir contraseña", type="password")
                btn_registrarse = st.form_submit_button("Dar de alta", use_container_width=True)
                
                if btn_registrarse:
                    if nuevo_correo and nuevo_pass:
                        if nuevo_correo in st.session_state.usuarios_db:
                            st.warning("El correo ya está registrado.")
                        elif nuevo_pass != conf_pass:
                            st.error("Las contraseñas no coinciden.")
                        else:
                            st.session_state.usuarios_db[nuevo_correo] = nuevo_pass
                            st.success("¡Cuenta creada con éxito!")
                    else:
                        st.error("Complete los campos.")
        if st.session_state.autenticado:
            st.success(f"Sesión activa:\n**{st.session_state.usuario_actual}**")
            if st.button("Cerrar Sesión", use_container_width=True):
                st.session_state.autenticado = False
                st.session_state.usuario_actual = ""
                st.rerun()

    st.markdown("---")
    st.markdown("""
        <p style="color: white; font-weight: bold; margin-bottom: 10px;">
            <i class="fa-solid fa-compass" style="color: #8BC34A;"></i> Navegación
        </p>
    """, unsafe_allow_html=True)
    
    # Botones de navegación limpios (sin emojis)
    if st.button("Inicio / Búsqueda", use_container_width=True, key="nav_btn_inicio"):
        st.session_state.vista_actual = "🏠 Inicio / Búsqueda"
        st.rerun()

    if st.button("Inventario Completo", use_container_width=True, key="nav_btn_inventario"):
        st.session_state.vista_actual = "📋 Ver Todos los Objetos (Inventario)"
        st.rerun()

# Asignación correcta de la variable menu
menu = st.session_state.vista_actual

# --- ENCABEZADO INSTITUCIONAL CON IMAGEN DE FONDO ---
def obtener_imagen_base64(ruta_imagen):
    try:
        with open(ruta_imagen, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

img_path = "encabez.png" 
img_base64 = obtener_imagen_base64(img_path)

if img_base64:
    background_css = f"linear-gradient(rgba(0, 40, 10, 0.45), rgba(0, 40, 10, 0.45)), url('data:image/png;base64,{img_base64}')"
else:
    background_css = "linear-gradient(135deg, #2E7D32 0%, #8BC34A 100%)"

st.markdown(
    f"""
    <style>
    .banner-uni-fondo {{
        background-image: {background_css};
        background-size: cover;
        background-position: center;
        padding: 50px 40px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }}
    .banner-uni-fondo h1 {{
        margin: 0;
        font-size: 2.3rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 5px rgba(0,0,0,0.7);
    }}
    .banner-uni-fondo p {{
        margin: 8px 0 0 0;
        font-size: 1.15rem;
        color: #F1F8E9;
        text-shadow: 0 1px 3px rgba(0,0,0,0.7);
    }}
    </style>

    <div class="banner-uni-fondo">
        <h1>OBJETOS PERDIDOS Y ENCONTRADOS</h1>
        <p>¿Has encontrado o perdido algo? - Publica y busca objetos</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# VISTA 1: INICIO Y BÚSQUEDA
# ==========================================
if menu == "🏠 Inicio / Búsqueda":
    
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
            <h3 style="color: #2E7D32; display: flex; align-items: center; gap: 10px; margin-bottom: 0;">
                <i class="fa-solid fa-magnifying-glass"></i> Búsqueda Rápida
            </h3>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size: 13px; color: #666; margin-top: 5px;'>Ingrese el código de objeto registrado.</p>", unsafe_allow_html=True)
        
        busqueda_codigo = st.text_input("Código de clasificación", placeholder="Ej. OBJ-001", key="input_busqueda_codigo")
        if st.button("Buscar en el Sistema", type="primary", use_container_width=True):
            if busqueda_codigo:
                resultado = st.session_state.tabla_hash.buscar(busqueda_codigo)
                if resultado:
                    st.success(f"¡Objeto localizado: **{resultado.nombre}**!")
                    
                    cont_txt = resultado.contacto
                    obs_txt = ""
                    if " | Obs: " in resultado.contacto:
                        cont_txt, obs_txt = resultado.contacto.split(" | Obs: ")

                    st.info(f"""
                    - **Categoría:** {resultado.categoria}
                    - **Estado:** {resultado.estado}
                    - **Lugar:** {resultado.lugar}
                    - **Registrado por:** {resultado.registrado_por}
                    - **Contacto:** {cont_txt}
                    """)
                    if obs_txt:
                        st.warning(f"**Descripción:** {obs_txt}")
                    if resultado.imagen:
                        st.image(resultado.imagen, width=200, caption="Fotografía del objeto")
                else:
                    st.error("No se encontró ningún objeto registrado con ese código.")
            else:
                st.warning("Por favor ingrese un código válido.")

    with col2:
        st.markdown("""
            <h3 style="color: #2E7D32; display: flex; align-items: center; gap: 10px; margin-bottom: 0;">
                <i class="fa-solid fa-pen-to-square"></i> Registrar Objeto
            </h3>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size: 13px; color: #666; margin-top: 5px;'>Personal autorizado para dar de alta nuevos reportes.</p>", unsafe_allow_html=True)
        
        with st.expander("PUBLICAR UN NUEVO OBJETO", expanded=st.session_state.form_abierto, key=f"expander_pub_{st.session_state.expander_key}"):
            if st.session_state.autenticado:
                total_objetos = len(st.session_state.lista_objetos.obtener_todos())
                codigo_automatico = f"OBJ-{total_objetos + 1:03d}"
                st.info(f"📌 Código automático asignado: **{codigo_automatico}**")

                with st.form("form_publicar", clear_on_submit=True):
                    c_nombre = st.text_input("Nombre del objeto")
                    c_estado = st.selectbox("Estado", ["PERDIDO", "ENCONTRADO"])
                    c_categoria = st.selectbox("Categoría", ["Electrónica", "Útiles", "Ropa", "Documentos", "Otros"])
                    c_lugar = st.text_input("Lugar donde se encontró/perdió")
                    
                    c_registrado_por = st.text_input("Nombre de quien ingresa")
                    tipo_contacto = st.radio("Tipo de contacto", ["Teléfono", "Correo electrónico"])
                    c_valor_contacto = st.text_input("Número o correo")
                    
                    foto_subida = st.file_uploader("Subir fotografía (Opcional)", type=["png", "jpg", "jpeg"])
                    
                    c_observacion = ""
                    if c_estado == "PERDIDO" and foto_subida is None:
                        c_observacion = st.text_area("📝 Descripción u observación clave (Obligatoria si no hay foto)")
                    
                    btn_enviar = st.form_submit_button("Guardar y Publicar", use_container_width=True)
                    if btn_enviar:
                        if c_nombre and c_registrado_por and c_valor_contacto:
                            contacto_completo = f"{tipo_contacto}: {c_valor_contacto}"
                            if c_observacion:
                                contacto_completo += f" | Obs: {c_observacion}"

                            imagen_final = None
                            if foto_subida is not None:
                                img = Image.open(foto_subida)
                                img.thumbnail((500, 500))
                                imagen_final = img

                            nuevo = ObjetoPerdido(
                                codigo_automatico, c_nombre, c_categoria, "2026-06-07", "12:00", 
                                c_lugar, c_estado, c_registrado_por, contacto_completo, imagen_final
                            )
                            
                            st.session_state.lista_objetos.agregar(nuevo)
                            st.session_state.tabla_hash.insertar(nuevo)
                            st.session_state.pila_historial.apilar(f"Se registró el objeto {codigo_automatico} por {st.session_state.usuario_actual}")
                            
                            st.session_state.form_abierto = False
                            st.session_state.expander_key += 1
                            
                            st.success(f"¡Objeto registrado con éxito ({codigo_automatico})!")
                            st.rerun()
                        else:
                            st.error("Por favor complete los campos obligatorios.")
            else:
                st.warning("🔒 Debe **iniciar sesión** en la barra lateral para desplegar y utilizar el formulario de publicación.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # --- SECCIÓN: ÚLTIMOS OBJETOS REGISTRADOS ---
    st.markdown("""
        <h3 style="color: #2E7D32; display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 15px;">
            <i class="fa-solid fa-cubes"></i> Últimos Objetos Ingresados
        </h3>
    """, unsafe_allow_html=True)
    objetos_guardados = st.session_state.lista_objetos.obtener_todos()

    if objetos_guardados:
        cols = st.columns(min(len(objetos_guardados), 3))
        for i, obj in enumerate(objetos_guardados[-3:]):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"<h4 style='margin-top: 0; color: #2E7D32;'>{obj.nombre}</h4>", unsafe_allow_html=True)
                    
                    col_datos, col_foto = st.columns([1.3, 1])
                    color_estado = "#E65100" if obj.estado == "PERDIDO" else ("#2E7D32" if obj.estado == "ENCONTRADO" else "#757575")
                    
                    contacto_texto = obj.contacto
                    observacion_texto = ""
                    if " | Obs: " in obj.contacto:
                        contacto_texto, observacion_texto = obj.contacto.split(" | Obs: ")

                    with col_datos:
                        html_datos = f"""
                            <p style="font-size: 13.5px; line-height: 1.4; margin-bottom: 5px;">
                            <b>Código:</b> {obj.codigo}<br>
                            <b>Estado:</b> <span style="color: {color_estado}; font-weight: bold;">{obj.estado}</span><br>
                            <b>Lugar:</b> {obj.lugar}<br>
                            <b><i class="fa-solid fa-user" style="color: #2E7D32;"></i>:</b> {obj.registrado_por}<br>
                            <b><i class="fa-solid fa-phone" style="color: #2E7D32;"></i>:</b> {contacto_texto}</p>
                        """
                        st.markdown(html_datos, unsafe_allow_html=True)
                    
                    with col_foto:
                        if obj.imagen:
                            st.image(obj.imagen, width=105)
                        else:
                            st.markdown("<div style='text-align: center; color: #999; padding: 20px 0; font-size: 12px; background: #f1f3f4; border-radius: 6px;'><i class='fa-solid fa-image-slash'></i> Sin foto</div>", unsafe_allow_html=True)
                    
                    if observacion_texto:
                        html_obs = f"""
                            <div style="background-color: #F1F8E9; padding: 8px; border-radius: 6px; margin-top: 10px; font-size: 12.5px; border-left: 3px solid #8BC34A;">
                            <b><i class="fa-solid fa-circle-info" style="color: #2E7D32;"></i> Detalle:</b> {observacion_texto}
                            </div>
                        """
                        st.markdown(html_obs, unsafe_allow_html=True)

                    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
                    
                    if obj.estado != "RECLAMADO":
                        if st.session_state.autenticado:
                            if st.button("Marcar Retirado", key=f"btn_retirar_{obj.codigo}_{i}", use_container_width=True):
                                obj.estado = "RECLAMADO"
                                st.session_state.pila_historial.apilar(f"El objeto {obj.codigo} fue cambiado a RECLAMADO")
                                st.success(f"¡Objeto {obj.codigo} actualizado!")
                                st.rerun()
                        else:
                            st.caption("🔒 Inicie sesión para retirar")
                    else:
                        st.markdown("<p style='color: #2E7D32; font-weight: bold; font-size: 13px; text-align: center;'><i class='fa-solid fa-circle-check'></i> Entregado / Retirado</p>", unsafe_allow_html=True)
    else:
        st.info("Aún no hay objetos registrados en el sistema.")

    st.markdown("---")

    # --- COLA Y PILA (ADMINISTRACIÓN) ---
    if st.session_state.autenticado:
        st.markdown("""
            <h3 style="color: #2E7D32; display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 15px;">
                <i class="fa-solid fa-gears"></i> Panel de Control de Datos
            </h3>
        """, unsafe_allow_html=True)
        col_cola, col_pila = st.columns(2, gap="medium")

        with col_cola:
            with st.container(border=True):
                st.markdown("""
                    <h4 style="color: #2E7D32; margin-top: 0;">
                        <i class="fa-solid fa-people-line"></i> Reclamos de objetos
                    </h4>
                """, unsafe_allow_html=True)
                persona_reclamo = st.text_input("Nombre del solicitante:", key="input_solicitante_cola")
                codigo_reclamo = st.text_input("Código del objeto reclamado:", key="input_codigo_reclamo")
                if st.button("Encolar Reclamo", use_container_width=True):
                    if persona_reclamo and codigo_reclamo:
                        st.session_state.cola_reclamos.encolar(f"{persona_reclamo} reclama {codigo_reclamo}")
                        st.success("Solicitud encolada correctamente.")
                        st.rerun()
                        
                st.write("**Fila actual de atención:**")
                reclamos_activos = st.session_state.cola_reclamos.obtener_todos()
                if reclamos_activos:
                    for r in reclamos_activos:
                        st.code(r)
                else:
                    st.caption("La cola está vacía.")
                    
                if st.button("Atender siguiente", use_container_width=True):
                    atendido = st.session_state.cola_reclamos.desencolar()
                    if atendido:
                        st.info(f"Atendido: {atendido}")
                        st.rerun()

        with col_pila:
            with st.container(border=True):
                st.markdown("""
                    <h4 style="color: #2E7D32; margin-top: 0;">
                        <i class="fa-solid fa-clock-rotate-left"></i> Historial de Auditoría
                    </h4>
                """, unsafe_allow_html=True)
                st.caption("Últimas acciones registradas en el sistema:")
                historial = st.session_state.pila_historial.obtener_todos()
                if historial:
                    for h in historial:
                        st.code(h)
                else:
                    st.caption("No hay registros en el historial.")
    else:
        st.info("💡 *Nota: El panel de gestión de colas de reclamos y auditoría de pila está restringido al personal autenticado.*")

# ==========================================
# VISTA 2: INVENTARIO COMPLETO
# ==========================================
elif menu == "📋 Ver Todos los Objetos (Inventario)":
    st.markdown("""
        <h2 style="color: #2E7D32; display: flex; align-items: center; gap: 10px;">
            <i class="fa-solid fa-boxes-stacked"></i> Ver Todos los Objetos (Inventario)
        </h2>
    """, unsafe_allow_html=True)
    st.write("Consulta general de todo el registro histórico de objetos perdidos y encontrados en la universidad.")
    
    todos_los_objetos = st.session_state.lista_objetos.obtener_todos()
    
    if todos_los_objetos:
        for i in range(0, len(todos_los_objetos), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(todos_los_objetos):
                    obj = todos_los_objetos[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='margin-top: 0; color: #2E7D32;'>{obj.nombre}</h4>", unsafe_allow_html=True)
                            
                            col_datos, col_foto = st.columns([1.3, 1])
                            color_estado = "#E65100" if obj.estado == "PERDIDO" else ("#2E7D32" if obj.estado == "ENCONTRADO" else "#757575")
                            
                            contacto_texto = obj.contacto
                            observacion_texto = ""
                            if " | Obs: " in obj.contacto:
                                contacto_texto, observacion_texto = obj.contacto.split(" | Obs: ")

                            with col_datos:
                                html_inv_datos = f"""
                                    <p style="font-size: 13.5px; line-height: 1.4; margin-bottom: 5px;">
                                    <b>Cat:</b> {obj.categoria}<br>
                                    <b>Código:</b> {obj.codigo}<br>
                                    <b>Estado:</b> <span style="color: {color_estado}; font-weight: bold;">{obj.estado}</span><br>
                                    <b>Lugar:</b> {obj.lugar}<br>
                                    <b><i class="fa-solid fa-user" style="color: #2E7D32;"></i>:</b> {obj.registrado_por}<br>
                                    <b><i class="fa-solid fa-phone" style="color: #2E7D32;"></i>:</b> {contacto_texto}</p>
                                """
                                st.markdown(html_inv_datos, unsafe_allow_html=True)
                            
                            with col_foto:
                                if obj.imagen:
                                    st.image(obj.imagen, width=105)
                                else:
                                    st.markdown("<div style='text-align: center; color: #999; padding: 20px 0; font-size: 12px; background: #f1f3f4; border-radius: 6px;'><i class='fa-solid fa-image-slash'></i> Sin foto</div>", unsafe_allow_html=True)
                            
                            if observacion_texto:
                                html_inv_obs = f"""
                                    <div style="background-color: #F1F8E9; padding: 8px; border-radius: 6px; margin-top: 10px; font-size: 12.5px; border-left: 3px solid #8BC34A;">
                                    <b><i class="fa-solid fa-circle-info" style="color: #2E7D32;"></i> Detalle:</b> {observacion_texto}
                                    </div>
                                """
                                st.markdown(html_inv_obs, unsafe_allow_html=True)

                            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
                            
                            if obj.estado != "RECLAMADO":
                                if st.session_state.autenticado:
                                    if st.button("Marcar Retirado", key=f"btn_retirar_inv_{obj.codigo}_{i}_{j}", use_container_width=True):
                                        obj.estado = "RECLAMADO"
                                        st.session_state.pila_historial.apilar(f"El objeto {obj.codigo} fue cambiado a RECLAMADO")
                                        st.success(f"¡Objeto {obj.codigo} actualizado!")
                                        st.rerun()
                                else:
                                    st.caption("🔒 Inicie sesión para retirar")
                            else:
                                st.markdown("<p style='color: #2E7D32; font-weight: bold; font-size: 13px; text-align: center;'><i class='fa-solid fa-circle-check'></i> Entregado / Retirado</p>", unsafe_allow_html=True)
    else:
        st.info("No hay objetos registrados en el sistema todavía.")