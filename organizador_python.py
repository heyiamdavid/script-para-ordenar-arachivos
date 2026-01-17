import os
import shutil
from pathlib import Path

class OrganizadorArchivos:
    def __init__(self, carpeta_origen, materias_con_palabras_clave, estructura_personalizada=None):
        """
        Inicializa el organizador de archivos.
        
        Args:
            carpeta_origen: Ruta de la carpeta donde están los archivos desordenados
            materias_con_palabras_clave: Diccionario {nombre_materia: [lista de palabras clave]}
            estructura_personalizada: Diccionario {nombre_materia: [lista de tipos de carpetas]}
                                     Si no se especifica, usa la estructura por defecto
        """
        self.carpeta_origen = Path(carpeta_origen)
        self.materias_palabras_clave = materias_con_palabras_clave
        self.estructura_personalizada = estructura_personalizada or {}
        
        # Extensiones por tipo de archivo
        self.tipos_archivos = {
            'pdf': ['.pdf'],
            'words': ['.doc', '.docx'],
            'powerpoint': ['.ppt', '.pptx'],
            'imagenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'diagramas': ['.vsd', '.vsdx', '.drawio', '.lnk', '.xml'],
            'comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'codigo': ['.py', '.java', '.c', '.cpp', '.js', '.html', '.css']
        }
        
        # Estructura por defecto (se usa si no se especifica una personalizada)
        self.estructura_default = ['pdf', 'words', 'powerpoint']
    
    def obtener_carpetas_para_materia(self, materia):
        """
        Obtiene la lista de carpetas que se deben crear para una materia.
        
        Args:
            materia: Nombre de la materia
            
        Returns:
            Lista de nombres de carpetas a crear
        """
        if materia in self.estructura_personalizada:
            return self.estructura_personalizada[materia]
        return self.estructura_default
    
    def crear_estructura_carpetas(self):
        """Crea la estructura de carpetas para cada materia"""
        print("Creando estructura de carpetas...")
        
        for materia in self.materias_palabras_clave.keys():
            carpeta_materia = self.carpeta_origen / materia
            carpeta_materia.mkdir(exist_ok=True)
            
            # Obtener carpetas específicas para esta materia
            carpetas_materia = self.obtener_carpetas_para_materia(materia)
            
            # Crear subcarpetas solo las especificadas
            for tipo in carpetas_materia:
                carpeta_tipo = carpeta_materia / tipo
                carpeta_tipo.mkdir(exist_ok=True)
                print(f"  ✓ Creada: {carpeta_materia.name}/{tipo}")
    
    def mover_archivos_de_subcarpetas(self):
        """
        Mueve todos los archivos de subcarpetas a la carpeta principal
        y elimina las carpetas vacías.
        """
        print("\nMoviendo archivos de subcarpetas a la carpeta principal...")
        archivos_movidos = 0
        carpetas_eliminadas = 0
        
        # Recorrer todas las subcarpetas
        for item in self.carpeta_origen.rglob('*'):
            # Solo procesar archivos que están dentro de subcarpetas
            if item.is_file() and item.parent != self.carpeta_origen:
                # Saltar archivos que ya están en carpetas de materias organizadas
                if any(materia in str(item.parent) for materia in self.materias_palabras_clave.keys()):
                    continue
                
                destino = self.carpeta_origen / item.name
                
                # Si ya existe un archivo con ese nombre, agregar sufijo
                if destino.exists():
                    base = destino.stem
                    ext = destino.suffix
                    contador = 1
                    while destino.exists():
                        destino = self.carpeta_origen / f"{base}_{contador}{ext}"
                        contador += 1
                
                try:
                    shutil.move(str(item), str(destino))
                    print(f"  ✓ Movido: {item.relative_to(self.carpeta_origen)} → {destino.name}")
                    archivos_movidos += 1
                except Exception as e:
                    print(f"  ✗ Error moviendo {item.name}: {e}")
        
        # Eliminar carpetas vacías (de abajo hacia arriba)
        print("\nEliminando carpetas vacías...")
        for carpeta in sorted(self.carpeta_origen.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if carpeta.is_dir() and carpeta != self.carpeta_origen:
                # No eliminar carpetas de materias
                if carpeta.name in self.materias_palabras_clave.keys():
                    continue
                
                # No eliminar carpetas de tipos (pdf, words, etc.) dentro de materias
                if any(materia in str(carpeta.parent) for materia in self.materias_palabras_clave.keys()):
                    continue
                
                try:
                    # Solo eliminar si está vacía
                    if not any(carpeta.iterdir()):
                        carpeta.rmdir()
                        print(f"  ✓ Eliminada: {carpeta.relative_to(self.carpeta_origen)}")
                        carpetas_eliminadas += 1
                except Exception as e:
                    print(f"  ⚠ No se pudo eliminar {carpeta.name}: {e}")
        
        print(f"\n  Archivos movidos: {archivos_movidos}")
        print(f"  Carpetas eliminadas: {carpetas_eliminadas}")
    
    def identificar_materia(self, nombre_archivo):
        """
        Identifica a qué materia pertenece un archivo basándose en palabras clave.
        
        Args:
            nombre_archivo: Nombre del archivo
            
        Returns:
            Nombre de la materia o None si no se identifica
        """
        nombre_lower = nombre_archivo.lower()
        
        # Buscar en cada materia si alguna palabra clave coincide
        for materia, palabras_clave in self.materias_palabras_clave.items():
            for palabra in palabras_clave:
                if palabra.lower() in nombre_lower:
                    return materia
        
        return None
    
    def obtener_tipo_archivo(self, extension):
        """
        Determina el tipo de archivo según su extensión.
        
        Args:
            extension: Extensión del archivo (ej: '.pdf')
            
        Returns:
            Tipo de archivo o None si no se reconoce
        """
        for tipo, extensiones in self.tipos_archivos.items():
            if extension.lower() in extensiones:
                return tipo
        return None
    
    def organizar_archivos(self, mover_de_subcarpetas=True, crear_estructura=True):
        """
        Organiza todos los archivos en sus carpetas correspondientes.
        
        Args:
            mover_de_subcarpetas: Si True, primero mueve archivos de subcarpetas
            crear_estructura: Si True, crea la estructura de carpetas primero
        """
        # Paso 1: Mover archivos de subcarpetas si se solicita
        if mover_de_subcarpetas:
            self.mover_archivos_de_subcarpetas()
        
        # Paso 2: Crear estructura de carpetas
        if crear_estructura:
            self.crear_estructura_carpetas()
        
        print("\nOrganizando archivos...")
        archivos_organizados = 0
        archivos_no_organizados = []
        
        # Recorrer todos los archivos en la carpeta origen (solo nivel superior)
        for archivo in self.carpeta_origen.iterdir():
            # Saltar si es una carpeta
            if archivo.is_dir():
                continue
            
            # Obtener información del archivo
            nombre_archivo = archivo.name
            extension = archivo.suffix
            
            # Identificar materia y tipo
            materia = self.identificar_materia(nombre_archivo)
            tipo = self.obtener_tipo_archivo(extension)
            
            if materia and tipo:
                # Verificar si esta materia debe tener este tipo de carpeta
                carpetas_materia = self.obtener_carpetas_para_materia(materia)
                
                if tipo in carpetas_materia:
                    # Construir ruta de destino
                    carpeta_destino = self.carpeta_origen / materia / tipo
                    ruta_destino = carpeta_destino / nombre_archivo
                    
                    # Mover archivo
                    try:
                        shutil.move(str(archivo), str(ruta_destino))
                        print(f"  ✓ {nombre_archivo} → {materia}/{tipo}/")
                        archivos_organizados += 1
                    except Exception as e:
                        print(f"  ✗ Error moviendo {nombre_archivo}: {e}")
                        archivos_no_organizados.append(nombre_archivo)
                else:
                    # La materia fue identificada pero no tiene carpeta para este tipo
                    archivos_no_organizados.append(nombre_archivo)
                    print(f"  ⚠ {nombre_archivo} no organizado ('{materia}' no tiene carpeta '{tipo}')")
            else:
                archivos_no_organizados.append(nombre_archivo)
                motivo = []
                if not materia:
                    motivo.append("materia no identificada")
                if not tipo:
                    motivo.append("tipo de archivo no reconocido")
                print(f"  ⚠ {nombre_archivo} no organizado ({', '.join(motivo)})")
        
        # Resumen
        print(f"\n{'='*60}")
        print(f"Resumen de organización:")
        print(f"  Archivos organizados: {archivos_organizados}")
        print(f"  Archivos sin organizar: {len(archivos_no_organizados)}")
        
        if archivos_no_organizados:
            print(f"\nArchivos que no se pudieron organizar:")
            for archivo in archivos_no_organizados:
                print(f"  - {archivo}")


def main():
    # ===== CONFIGURACIÓN =====
    # Cambia esta ruta a la carpeta donde tienes tus archivos
    CARPETA_ORIGEN = "."  # "." significa la carpeta actual
    
    # Define tus materias con palabras clave para identificarlas
    # Formato: "Nombre Materia": ["palabra1", "palabra2", "palabra3"]
    MATERIAS_PALABRAS_CLAVE = {
        "Base de Datos": [
            "base", "datos", "basedatos", "bd", "postgresql", 
            "postgres", "sql", "vistas", "auditoria", "modelo conceptual", 
            "modelo", "actividad_clase", "BD"
        ],
        "Estructura de Datos": [
            "tad", "pila", "cola", "colas", "arboles", "caratula", "ej", "EJ", "ver", "veterinaria"
        ],
        "Modelado Orientado a Objetos": [
            "modelado", "objetos", "moo", "uml", "diagrama",
            "secuencia", "clases", "argouml", "refactorizacion", 
            "ejercicio", "escuela", "scar", "addons"
        ],
        "Perspectiva de la Inteligencia Artificial": [
            "ia", "inteligencia", "artificial", "perspectiva",
            "robotica", "vision", "sesgos", "discriminacion",
            "etica", "responsabilidad", "logica difusa", "tendencias",
            "trabajo-autonomo", "difusa", "ia", "Uleam"
        ],
        "Programacion Estructurada": [
            "programacion", "estructurada", "funciones",
            "ciclos", "diccionarios", "numpy", "archivos", "manipulacion", 
            "actividad_en_clase", "actv", "hay q hacer", "ejercicio", "numeros", "multiplos", "escoger", "retorno",
            "precios", "planificacion", "vector", "validar", "empleados", "promedio", "cedu","programacion"
        ],
        "Redes de la computadora": [
            "redes", "red", "wan", "vpn", "ethernet", "fibra",
            "optica", "packet tracer", "subnectic", "acls", "ieee","packet", "MAC"
        ]
    }
    
    # Define qué carpetas crear para cada materia
    # Si no especificas una materia, usará la estructura por defecto: pdf, words, powerpoint
    ESTRUCTURA_PERSONALIZADA = {
        "Modelado Orientado a Objetos": [
            "pdf", "words", "powerpoint", "imagenes", "diagramas"
        ],
        "Perspectiva de la Inteligencia Artificial": [
            "pdf", "words", "powerpoint", "imagenes", "comprimidos"
        ],
        "Programacion Estructurada": [
            "pdf", "words", "powerpoint","comprimidos", "codigo"
        ],
        "Estructura de Datos": [
            "pdf", "words", "powerpoint", "codigos"
        ],
        "Redes de la computadora": [
            "pdf", "words", "powerpoint"
        ],
        "Base de Datos": [
            "pdf", "words", "powerpoint", "comprimidos"
        ]
        # Las demás materias usarán la estructura por defecto
    }
    # =========================
    
    print("="*60)
    print("ORGANIZADOR DE ARCHIVOS ACADÉMICOS v2.0")
    print("="*60)
    print(f"\nCarpeta de trabajo: {os.path.abspath(CARPETA_ORIGEN)}")
    print(f"Materias configuradas: {len(MATERIAS_PALABRAS_CLAVE)}")
    
    print("\nEstructura personalizada:")
    for materia, carpetas in ESTRUCTURA_PERSONALIZADA.items():
        print(f"  • {materia}: {', '.join(carpetas)}")
    print("  • Otras materias: pdf, words, powerpoint (por defecto)")
    
    print("\nCaracterísticas:")
    print("  ✓ Mueve archivos de subcarpetas a la carpeta principal")
    print("  ✓ Elimina carpetas vacías automáticamente")
    print("  ✓ Organiza por palabras clave")
    print("  ✓ Estructura personalizada por materia")
    
    respuesta = input("\n¿Deseas continuar? (s/n): ").lower()
    if respuesta != 's':
        print("Operación cancelada.")
        return
    
    # Crear organizador
    organizador = OrganizadorArchivos(
        CARPETA_ORIGEN, 
        MATERIAS_PALABRAS_CLAVE,
        ESTRUCTURA_PERSONALIZADA
    )
    
    # Organizar archivos (mover de subcarpetas y organizar)
    organizador.organizar_archivos(mover_de_subcarpetas=True, crear_estructura=True)
    
    print("\n¡Organización completada!")


if __name__ == "__main__":
    main()