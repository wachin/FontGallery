# ROADMAP

## Vision

- [ ] Crear una aplicacion en `PyQt6` para GNU/Linux orientada a **Diseño Grafico**.
- [ ] Ayudar a personas nuevas en Linux a descubrir visualmente las fuentes disponibles en los repositorios.
- [ ] Tomar como base la coleccion de fuentes reunida por Ubuntu Studio y otras fuentes descargadas desde repositorios.
- [ ] Separar claramente las fuentes utiles para diseño grafico general de las fuentes tecnicas o matematicas.

## Principio central

- [ ] Usar `album-fuentes` como **coleccion maestra**.
- [ ] Extraer primero todas las fuentes desde `paquetes-deb` hacia `album-fuentes/fuentes-extraidas`.
- [ ] Analizar esa coleccion maestra una sola vez.
- [ ] Derivar desde esa coleccion maestra otros albumes tematicos sin volver a extraer los `.deb`.

## Estructura de carpetas

### Carpetas base

- [ ] Crear `/paquetes-deb` si no existe.
- [ ] Crear `/album-fuentes` si no existe.
- [ ] Crear `/album-fuentes-espanol` si no existe.
- [ ] Crear `/album-fuentes-tecnicas` si no existe.

### Subcarpetas de fuentes extraidas

- [ ] Crear `/album-fuentes/fuentes-extraidas` si no existe.
- [ ] Crear `/album-fuentes-espanol/fuentes-extraidas` si no existe.
- [ ] Crear `/album-fuentes-tecnicas/fuentes-extraidas` si no existe.

### Subcarpetas de tarjetas

- [ ] Crear `/album-fuentes/tarjetas-fuentes` si no existe.
- [ ] Crear `/album-fuentes-espanol/tarjetas-fuentes-espanol` si no existe.
- [ ] Crear `/album-fuentes-tecnicas/tarjetas-fuentes-tecnicas` si no existe.

## Flujo principal deseado

### Paso 1. Preparar estructura

- [ ] Boton para preparar la estructura de carpetas.
- [ ] Verificar permisos de escritura.
- [ ] Mostrar mensajes claros si alguna carpeta no puede crearse.

### Paso 2. Extraer todas las fuentes a la coleccion maestra

- [ ] Leer paquetes `.deb` desde `paquetes-deb`.
- [ ] Detectar cuales paquetes contienen fuentes.
- [ ] Extraer fuentes unicas hacia `album-fuentes/fuentes-extraidas`.
- [ ] Evitar duplicados por hash.
- [ ] Registrar fuentes que no puedan abrirse o copiarse.

### Paso 3. Analizar la coleccion maestra

- [ ] Leer metadata de todas las fuentes extraidas.
- [ ] Obtener familia, estilo, nombre completo y nombre de archivo.
- [ ] Detectar cobertura Unicode.
- [ ] Detectar si la fuente soporta correctamente español.
- [ ] Detectar si la fuente es tecnica o matematica.
- [ ] Detectar otras categorias utiles para diseñadores.

### Paso 4. Derivar subalbumes desde `album-fuentes`

- [ ] Crear `album-fuentes-espanol` a partir de `album-fuentes`.
- [ ] Crear `album-fuentes-tecnicas` a partir de `album-fuentes`.
- [ ] Crear reportes de exclusiones y clasificacion.

### Paso 5. Generar indices HTML

- [ ] Crear `album-fuentes/album-fuentes.html`.
- [ ] Crear `album-fuentes-espanol/album-fuentes-espanol.html`.
- [ ] Crear `album-fuentes-tecnicas/album-fuentes-tecnicas.html`.

### Paso 6. Generar tarjetas

- [ ] Generar tarjetas PNG para `album-fuentes`.
- [ ] Generar tarjetas PNG para `album-fuentes-espanol`.
- [ ] Generar tarjetas PNG para `album-fuentes-tecnicas`.

### Paso 7. Generar PDFs

- [ ] Generar PDF para `album-fuentes`.
- [ ] Generar PDF para `album-fuentes-espanol`.
- [ ] Generar PDF para `album-fuentes-tecnicas`.

## Albumes base del proyecto

### Album principal

- [ ] Mantener `album-fuentes` como catalogo principal de diseño grafico general.
- [ ] Excluir de ese album las fuentes tecnicas o matematicas.
- [ ] Incluir todas las fuentes visualmente utiles para composicion comun.

### Album en español

- [ ] Mantener `album-fuentes-espanol` como subconjunto con soporte correcto para `áéíóúüñÁÉÍÓÚÜÑ`.
- [ ] Excluir tambien de ese album las fuentes tecnicas.

### Album tecnico

- [ ] Mantener `album-fuentes-tecnicas` como album separado para fuentes matematicas, simbolicas o de composicion tecnica.
- [ ] Incluir fuentes de `jsMath`, `LyX`, `LaTeX`, `TeX` y similares cuando corresponda.

## Filtros utiles para diseñadores

### Filtros prioritarios

- [ ] Fuentes con soporte para español.
- [ ] Fuentes tecnicas o matematicas.
- [ ] Fuentes monoespaciadas.
- [ ] Fuentes serif.
- [ ] Fuentes sans serif.
- [ ] Fuentes script o caligraficas.
- [ ] Fuentes display o decorativas.
- [ ] Fuentes manuscritas.
- [ ] Fuentes con muchas variantes.
- [ ] Fuentes adecuadas para texto largo.
- [ ] Fuentes adecuadas para titulos.

### Filtros tecnicos posibles

- [ ] Filtrar por familia.
- [ ] Filtrar por estilo.
- [ ] Filtrar por cobertura Unicode.
- [ ] Filtrar por cantidad de glifos.
- [ ] Filtrar por ancho fijo o proporcional.
- [ ] Filtrar por presencia de negrita real.
- [ ] Filtrar por presencia de italica real.
- [ ] Filtrar por small caps si la metadata lo permite.
- [ ] Filtrar por OpenType features si se logra detectar.
- [ ] Filtrar por variable font si se logra detectar.

### Filtros graficos recomendables para el futuro

- [ ] `album-fuentes-monoespaciadas`
- [ ] `album-fuentes-serif`
- [ ] `album-fuentes-sans`
- [ ] `album-fuentes-display`
- [ ] `album-fuentes-script`
- [ ] `album-fuentes-con-muchas-variantes`
- [ ] `album-fuentes-latino-basicas`
- [ ] `album-fuentes-unicode-amplias`

## Criterios de clasificacion ya definidos

### Fuentes de diseño grafico general

- [ ] Mantener en el album principal las fuentes utiles para carteles, branding, publicaciones, maquetacion y composicion visual general.

### Fuentes en español

- [ ] Mantener en el album español solo fuentes que realmente cubran los caracteres necesarios para usuarios hispanohablantes.

### Fuentes tecnicas

- [ ] Mantener fuera del album principal las fuentes tecnicas o matematicas.
- [ ] Documentar por qué se excluyen del album principal.
- [ ] Explicar que sirven mejor en otros programas especializados.

## Programas y ecosistemas tecnicos a documentar

- [ ] Explicar el uso de fuentes de `jsMath`.
- [ ] Explicar el uso de fuentes de `LyX`.
- [ ] Explicar el uso de fuentes de `LaTeX`.
- [ ] Explicar el uso de fuentes de `TeX`.
- [ ] Explicar que algunas dependen de metricas o convenciones de composicion especiales y no se ven bien en HTML comun.

## Dependencias y aclaraciones del sistema

- [ ] Documentar que en `paquetes-deb` pueden venir tambien dependencias y no solo fuentes.
- [ ] Explicar que algunas dependencias sirven para renderizado, otras para composicion tipografica y otras para programas especializados.
- [ ] No asumir que todas las dependencias mejoran la visualizacion en navegador web normal.

## Interfaz PyQt6

### Ventana principal

- [ ] Mostrar carpeta base de trabajo.
- [ ] Mostrar cantidad de paquetes `.deb` detectados.
- [ ] Mostrar estado de carpetas.
- [ ] Mostrar progreso de extraccion.
- [ ] Mostrar progreso de analisis.
- [ ] Mostrar progreso de generacion de HTML.
- [ ] Mostrar progreso de generacion de tarjetas.
- [ ] Mostrar progreso de generacion de PDFs.

### Botones minimos

- [ ] Boton `Preparar estructura`.
- [ ] Boton `Extraer todas las fuentes a album-fuentes`.
- [ ] Boton `Analizar y clasificar coleccion maestra`.
- [ ] Boton `Generar album-fuentes-espanol`.
- [ ] Boton `Generar album-fuentes-tecnicas`.
- [ ] Boton `Generar indices HTML`.
- [ ] Boton `Generar tarjetas`.
- [ ] Boton `Generar PDFs`.

### Mejoras futuras de interfaz

- [ ] Consola de salida integrada.
- [ ] Panel de reportes.
- [ ] Vista previa de fuentes.
- [ ] Selector de carpeta base.
- [ ] Configuracion persistente.

## Arquitectura recomendada

### Modulo de filesystem

- [ ] Crear y validar carpetas.
- [ ] Comprobar permisos.
- [ ] Limpiar o reutilizar salidas.

### Modulo de paquetes `.deb`

- [ ] Detectar paquetes.
- [ ] Extraer con `dpkg-deb -x`.
- [ ] Determinar si contienen fuentes.

### Modulo de analisis tipografico

- [ ] Leer metadata de las fuentes.
- [ ] Detectar cobertura para español.
- [ ] Detectar fuentes tecnicas.
- [ ] Detectar filtros utiles para diseñadores.

### Modulo de generacion HTML

- [ ] Generar albumes HTML reutilizando la logica existente.

### Modulo de tarjetas

- [ ] Generar tarjetas PNG con Pillow.

### Modulo de PDF

- [ ] Generar PDF desde tarjetas o desde composicion directa.

### Modulo GUI

- [ ] Orquestar todo desde `PyQt6`.
- [ ] No reimplementar la logica de negocio dentro de la GUI.

## Reutilizacion del trabajo ya hecho

- [ ] Reutilizar `generar_album_fuentes.py`.
- [ ] Reutilizar `generar_album_fuentes_espanol.py`.
- [ ] Reutilizar `generar_album_fuentes_tecnicas.py`.
- [ ] Reutilizar `generar_album_fuentes_espanol_imagenes.py` donde convenga.
- [ ] Extraer la logica comun a funciones o modulos reutilizables.

## Fases sugeridas

### Fase 1

- [ ] Crear esqueleto del proyecto PyQt6.
- [ ] Crear ventana principal minima.
- [ ] Implementar `Preparar estructura`.

### Fase 2

- [ ] Implementar extraccion total hacia `album-fuentes`.
- [ ] Implementar registro de errores y duplicados.

### Fase 3

- [ ] Implementar analisis de la coleccion maestra.
- [ ] Implementar derivacion a español y tecnicas.

### Fase 4

- [ ] Implementar generacion de HTML desde la GUI.
- [ ] Implementar generacion de tarjetas desde la GUI.

### Fase 5

- [ ] Implementar generacion de PDFs.
- [ ] Optimizar rendimiento.
- [ ] Evitar congelamiento de interfaz.

### Fase 6

- [ ] Implementar nuevos filtros utiles para diseñadores.
- [ ] Generar albumes derivados adicionales.

## Riesgos y puntos a revisar

- [ ] Paquetes `.deb` dañados o incompletos.
- [ ] Fuentes duplicadas.
- [ ] Fuentes que fallan al cargar con Pillow.
- [ ] Dificultad para distinguir automaticamente algunas familias tecnicas.
- [ ] Tiempos largos de renderizado.
- [ ] Necesidad de hilos o procesos para no congelar la GUI.
- [ ] Diferencias entre lo que renderiza Pillow y lo que renderiza el navegador.
- [ ] Diferencias entre fuentes buenas para diseño y fuentes que solo parecen utiles a simple vista.

## Resultado final esperado

- [ ] El usuario prepara la estructura con un boton.
- [ ] El usuario coloca manualmente los `.deb` en `paquetes-deb`.
- [ ] La aplicacion extrae todo primero a `album-fuentes`.
- [ ] La aplicacion analiza esa coleccion maestra.
- [ ] La aplicacion crea albumes derivados como español y tecnicas.
- [ ] La aplicacion genera HTML, tarjetas y PDFs.
- [ ] El sistema queda listo para crecer con nuevos filtros utiles para diseñadores.
