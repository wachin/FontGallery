# Álbum de Fuentes Extraídas de Paquetes .deb de UbuntuStudio Fonts

<div align="center">

**Por:** Washington Indacochea Delgado  
✉️ linuxfrontier@proton.me  
📅 2026

</div>

## Introducción

Este documento es un catálogo visual de 488 páginas que muestra una extensa colección de tipografías generadas a partir de los paquetes `.deb` oficiales de los repositorios de Ubuntu. 

La colección ha sido extraída específicamente utilizando la lista de dependencias del metapaquete **[UbuntuStudio Fonts 26.04](https://packages.ubuntu.com/ubuntustudio-fonts)**. El propósito principal de este álbum es servir como un directorio de exploración y referencia para diseñadores gráficos, tipógrafos y usuarios en general, permitiendo apreciar la variedad de fuentes de código abierto disponibles en el ecosistema UbuntuStudio.

### Contenido del catálogo

Cada una de las 488 páginas de este PDF está dedicada a mostrar una familia o variante de fuente específica. Para cada tipografía se incluye la siguiente información técnica:
* **Nombre completo** (Full name)
* **Estilo** (Style: Regular, Bold, Italic, etc.)
* **Paquete de origen** (Package)
* **Archivo** (File)

Además, se presenta una muestra de texto que incluye el abecedario en minúsculas y mayúsculas, caracteres numéricos, símbolos especiales con acentuación propia del idioma español, y un pasaje de texto continuo (Proverbios 3:3-4) para evaluar la legibilidad y el flujo de la fuente en un bloque de párrafo. 

*Nota: Las fuentes de orientación técnica y matemática han sido excluidas de este álbum principal para centrarse en las tipografías de uso general para diseño gráfico.*

### Comando de descarga e instalación

Si deseas replicar este entorno, descargar los paquetes originales o instalar estas fuentes en tu propio sistema, a continuación se proporciona el script en bash utilizado para obtener la lista de paquetes y descargarlos desde los repositorios:

```bash
for pkg in $(apt-rdepends \
cm-super-x11 fonts-adf-accanthis fonts-aenigma fonts-agave \
fonts-alee fonts-atarismall fonts-bpg-georgian fonts-breip \
fonts-dejavu-extra fonts-dkg-handwriting fonts-dustin \
fonts-ecolier-court fonts-ecolier-lignes-court fonts-f500 \
fonts-fanwood fonts-freefont-ttf fonts-georgewilliams \
fonts-goudybookletter fonts-inconsolata fonts-inter \
fonts-isabella fonts-jsmath fonts-junicode fonts-jura \
fonts-larabie-deco fonts-larabie-straight fonts-larabie-uncommon \
fonts-league-spartan fonts-lindenhill fonts-linex \
fonts-linuxlibertine fonts-lyx fonts-manchufont \
fonts-noto-hinted fonts-noto-mono fonts-ocr-a fonts-ocr-b \
fonts-oflb-euterpe fonts-okolaks fonts-opensymbol \
fonts-osifont fonts-radisnoir fonts-sil-andika \
fonts-sil-charis fonts-sil-doulos fonts-sil-gentium \
fonts-sil-gentium-basic fonts-tomsontalks fonts-tuffy \
fonts-ubuntu-title fonts-unifont gsfonts gsfonts-other \
lmodern t1-cyrillic t1-teams t1-xfree86-nonfree \
ttf-bitstream-vera ttf-xfree86-nonfree \
ttf-xfree86-nonfree-syriac xfonts-scalable 2>/dev/null \
| grep -v '^ ' \
| sort -u); do
    apt download "$pkg"
done
```

*(Para instalar las fuentes descargadas en tu sistema, simplemente debes extraer los archivos `.ttf` u `.otf` de los paquetes `.deb` descargados y copiarlos a tu directorio de fuentes de usuario `~/.local/share/fonts/` o del sistema `/usr/share/fonts/`) o en `~/.fonts/`*

---
*Generado con FontGallery a partir de paquetes .deb extraídos localmente.*