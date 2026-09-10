# Proyecto Jarvis — Plan de trabajo

Documento vivo. Lo iremos ajustando conforme avancemos; no es una promesa de fechas exactas, es un mapa realista para no perdernos.

**Perfil de partida:** estudiante de 4to semestre de Ingeniería (CUCEI), base sólida en C/C++, Python en aprendizaje. Objetivo secundario del proyecto: aprender programación, IA, bases de datos, APIs, seguridad y manejo del sistema operativo — no solo "tener un asistente que funcione".

**Tiempo disponible:** 6-10 horas/semana. **Sistema operativo:** Windows.

**Forma de trabajar juntos:** avanzamos en partes pequeñas. Cada módulo se explica antes de escribirlo, se escribe, se prueba, y no seguimos al siguiente hasta que lo entiendas y funcione. Yo actúo como mentor, no como generador de código terminado.

---

## 1. Principios de arquitectura (desde el día uno)

Estos principios no son "para después", se aplican desde la v0.1 porque cambiarlos más adelante es mucho más caro que empezar bien:

- **Módulos separados y desacoplados.** Entrada (texto/voz), interpretación, herramientas, memoria, salida (texto/voz) y activación son piezas independientes que se comunican por interfaces simples (funciones/clases con contratos claros), no un solo script gigante.
- **Registro de herramientas con lista blanca (allowlist).** El asistente nunca ejecuta comandos arbitrarios de CMD/PowerShell. Cada acción posible es una función de Python registrada explícitamente, con un nombre, una descripción y un nivel de permiso.
- **Niveles de permiso por herramienta.** Por ejemplo: `SAFE` (leer la hora, listar notas — se ejecuta sin preguntar), `CONFIRM` (borrar una nota, enviar algo, modificar configuración — pide confirmación explícita antes de ejecutar). Esto se decide ahora en el diseño del registro de herramientas, aunque al inicio casi todo sea `SAFE`.
- **El intérprete nunca ejecuta directamente.** El modelo de lenguaje (o el parser simple inicial) solo decide *qué herramienta* llamar y con qué parámetros; una capa intermedia valida que esa herramienta exista, esté permitida, y pide confirmación si aplica. El LLM no tiene la llave de la casa, solo puede tocar el timbre.
- **Todo queda registrado (logging).** Cada acción que ejecuta el asistente se guarda en un log local. Es barato de hacer ahora y esencial para depurar cuando el sistema crezca.

---

## 2. Estructura del proyecto

```
ProyectoJarvis/
├── README.md                  # Qué es, cómo instalarlo, cómo correrlo
├── requirements.txt           # Dependencias de Python
├── .gitignore
├── .env.example                # Variables de entorno de ejemplo (sin secretos reales)
├── config.py                  # Carga de configuración (rutas, flags, claves)
├── main.py                    # Punto de entrada: arranca el loop de la consola
├── jarvis/
│   ├── core/
│   │   ├── interpreter.py     # Traduce texto del usuario -> (herramienta, parámetros)
│   │   └── executor.py        # Valida permisos, pide confirmación, ejecuta la herramienta
│   ├── tools/
│   │   ├── registry.py        # Lista blanca de herramientas disponibles
│   │   └── basic_tools.py     # Las ~5 herramientas iniciales
│   ├── memory/
│   │   └── notes_store.py     # Guardar/leer notas (JSON al inicio, SQLite después)
│   └── utils/
│       └── logger.py          # Logging simple a archivo
├── data/                      # Notas, base de datos, logs (no se sube a git)
├── tests/
│   └── test_basic_tools.py    # Pruebas de cada herramienta
└── docs/
    └── ROADMAP.md              # Este documento
```

**Por qué así:** `core` decide *qué hacer*, `tools` sabe *cómo hacerlo*, `memory` sabe *qué recordar*. Cuando en la Fase 2 conectemos un LLM, solo se reemplaza la lógica interna de `interpreter.py` — el resto del sistema no se entera del cambio. Ese es el punto de tener módulos desacoplados: se puede mejorar una pieza sin romper las demás.

---

## 3. Requisitos iniciales (Windows)

Para la v0.1 (solo consola, sin voz todavía) necesitas:

- **Python 3.11 o 3.12** (evita instalar más de una versión sin usar entornos virtuales — causa muchos dolores de cabeza).
- **Git para Windows** + una cuenta de GitHub (ya la tienes contemplada).
- **VS Code** con la extensión de Python (si no lo usas ya).
- **Entorno virtual** (`venv`) por proyecto — te lo explico y lo montamos juntos en la primera sesión de código; es una de esas cosas que hay que entender bien una vez y ya.

Para fases posteriores (no instalar todavía, se agregan cuando lleguemos ahí):

- **Ollama para Windows** (Fase 3 — modelo de lenguaje local).
- **Visual C++ Build Tools** (necesario para compilar algunas dependencias de audio en Windows, como whisper.cpp o ciertas ruedas de Python).
- **ffmpeg** (Fase 5 — manejo de audio).
- **git-lfs** opcional si terminamos versionando modelos pesados (normalmente NO se versionan, se descargan aparte — lo veremos cuando llegue el momento).

---

## 4. Roadmap por fases

Fases pensadas para 6-10 h/semana. Los rangos de semanas son una guía, no una fecha límite — si una fase se alarga porque el semestre aprieta, ajustamos el resto sin culpa.

### Fase 0 — Arranque (semana 1)
Entorno de desarrollo, Git/GitHub conectados, entorno virtual funcionando, esqueleto del repo corriendo (`main.py` que abre un loop que solo hace *echo* de lo que escribes). Meta: tener el "hola mundo" del proyecto, con control de versiones desde el primer commit.

### Fase 1 — v0.1: asistente de consola con reglas simples (semanas 2-5)
Antes de tocar un LLM, el intérprete es un parser simple basado en palabras clave / expresiones regulares. Esto es intencional: entender bien un intérprete simple hace mucho más fácil entender uno basado en LLM después. Se implementan las ~5 herramientas iniciales:

1. Decir la hora y la fecha.
2. Abrir programas o páginas web (con lista blanca de programas/URLs permitidos).
3. Crear y consultar notas (guardadas en un archivo JSON).
4. Buscar archivos en el sistema (en carpetas permitidas, no en todo el disco).
5. Responder preguntas sencillas (respuestas predefinidas o cálculos simples).

Aquí también se construye el patrón de "registro de herramientas + ejecutor con niveles de permiso" descrito arriba, aunque casi todo sea `SAFE` por ahora.

### Fase 2 — Arquitectura de permisos y confirmaciones (semana 6)
Se formaliza el sistema de confirmación antes de acciones delicadas (borrar, modificar, enviar). Es una fase corta pero importante: mejor consolidar seguridad antes de que el sistema tenga más piezas móviles.

### Fase 3 — Modelo de lenguaje local (semanas 7-9)
Se instala Ollama y se conecta un modelo pequeño (por ejemplo Llama 3.2 3B o Phi-3 mini, según lo que tu equipo aguante). `interpreter.py` cambia de reglas fijas a usar el LLM para decidir qué herramienta llamar — pero el ejecutor sigue validando todo igual que antes. Aquí se aprende sobre prompting, function calling / tool use, y por qué nunca hay que confiar ciegamente en la salida de un modelo.

### Fase 4 — Memoria persistente con SQLite (semanas 10-12)
Se reemplaza el JSON de notas por una base de datos SQLite: notas, preferencias del usuario, historial de conversación. Se diseña el esquema de tablas juntos — es una buena introducción práctica a bases de datos relacionales.

### Fase 5 — Entrada de voz (semanas 13-15)
Reconocimiento de voz con whisper.cpp (o `faster-whisper` como alternativa más simple de instalar en Windows si whisper.cpp da problemas de compilación). El resultado transcrito entra al mismo `interpreter.py` de siempre — otra ventaja de tener módulos desacoplados.

### Fase 6 — Salida de voz (semanas 16-17)
Síntesis de voz con Piper. El asistente empieza a "hablar" sus respuestas en vez de solo imprimirlas.

### Fase 7 — Palabra de activación (semanas 18-19)
openWakeWord para detectar "Jarvis" y activar la escucha, en vez de tener que ejecutar el programa manualmente cada vez.

### Fase 8 — Funciones extra (semanas 20-23)
Recordatorios y calendario, control de música, búsqueda de documentos más avanzada. Cada una se agrega como una nueva herramienta en el registro — el patrón ya está probado.

### Fase 9 — Estabilidad y arranque automático (semanas 24+)
Inicio automático con el sistema (Task Scheduler de Windows), manejo robusto de errores para que no se caiga tras horas corriendo, revisión de consumo de memoria/CPU en ejecución prolongada. Esta fase es abierta — "24 horas estable" es una meta de mejora continua, no un checkbox único.

**Estimado total hasta una versión "24 horas" razonablemente estable: ~6 meses a este ritmo.** Si el semestre se complica, lo normal y esperable es que esto se estire — la prioridad es que entiendas cada pieza, no la velocidad.

---

## 5. Próximo paso inmediato

Fase 0 a Fase 5 completas.

Fase 1: las 5 herramientas iniciales (hora y fecha, abrir programa o web, crear/consultar notas, buscar archivos, responder preguntas sencillas) están implementadas, registradas en `jarvis/tools/registry.py`, y cada una tiene al menos una prueba en `tests/`.

Fase 2: el sistema de confirmación de `jarvis/core/executor.py` (permiso `CONFIRM`, pide s/n antes de ejecutar) se ejercita con dos acciones destructivas reales -- `borrar_nota` y `sobrescribir_nota` -- además de pruebas de punta a punta que confirman el flujo completo.

Fase 3: Ollama instalado localmente con el modelo `llama3.2` (3B). `jarvis/core/interpreter.py` ya no usa palabras clave -- `interpret()` arma un prompt con la lista de herramientas (sacada directo de `registry.py` con `inspect.signature`, nunca escrita a mano) vía `jarvis/core/llm_client.py`, y valida la respuesta del modelo antes de convertirla en `ToolCall`: si el JSON viene mal formado, si inventa una herramienta que no existe, o si los parámetros no coinciden con los que la herramienta espera, se trata igual que "no entendí" -- nunca se ejecuta nada a ciegas. `executor.py` no cambió: sigue validando contra el registro y pidiendo confirmación exactamente igual que antes. `main.py` distingue "Ollama no responde" (error de conexión) de "no entendí la instrucción" (el modelo respondió pero no encontró herramienta aplicable).

Fase 4: se creó `jarvis/memory/db.py` (conexión a `data/jarvis.db` vía `sqlite3`, incluido en la librería estándar). `notes_store.py` se migró del JSON a la tabla `notas` (columnas `id`, `texto`, `creada`, `editada`), manteniendo la misma interfaz pública y la misma numeración visible (1, 2, 3...) que ya usaban `basic_tools.py` y el usuario -- por dentro, cada nota ahora tiene un `id` propio que nunca cambia aunque se borren otras. Se agregó también `jarvis/memory/historial_store.py` con la tabla `historial` (`texto_usuario`, `respuesta`, `fecha`): a diferencia de `jarvis/utils/logger.py` (que solo registra ejecuciones de herramientas para depuración), aquí queda toda la interacción -- incluyendo "no entendí" o un error de conexión con Ollama -- conectado directo en el loop de `main.py`. Todas las consultas SQL que incluyen datos del usuario usan placeholders (`?`), nunca los meten en el texto de la consulta, para evitar inyección SQL.

La tabla de preferencias del usuario, contemplada originalmente en esta fase, se dejó pendiente a propósito: todavía no existe ninguna herramienta que necesite leer o guardar una preferencia, y se decidió no diseñar ese esquema hasta que haya una razón concreta que lo pida.

Fase 5: entrada de voz con `faster-whisper` (se eligió sobre whisper.cpp para no depender de compilar nada en Windows -- se instala con `pip install` y ya, vía ruedas precompiladas). Se agregó `jarvis/audio/`:

- `grabador.py`: `grabar_audio()` captura del micrófono por defecto con `sounddevice`, con una cuenta regresiva de 3 segundos impresa antes de empezar (sin eso, se perdía el inicio de lo que decía el usuario -- se detectó probando a mano). Regresa un arreglo de una dimensión en punto flotante a `config.AUDIO_SAMPLE_RATE` (16000 Hz, lo que espera Whisper).
- `transcriptor.py`: `transcribir()` envuelve `faster_whisper.WhisperModel`, cacheando el modelo cargado en una variable de módulo (`_modelo`) para no releerlo del disco en cada llamada -- cargarlo tarda unos segundos. El tamaño de modelo es configurable vía `config.WHISPER_MODEL` (`.env`, por defecto `"base"`: mejor precisión que `"tiny"` corriendo en CPU, sin llegar a ser lento).

`main.py` reconoce el comando `voz`: graba, transcribe, e inyecta el texto resultante al mismo `interpreter.interpret()` de siempre -- no se duplicó ninguna lógica de interpretación/ejecución/historial, solo se agregó una fuente de entrada alternativa a `input()`.

De paso se encontró y corrigió un bug de la Fase 3, no relacionado con la voz en sí: `config.OLLAMA_MODEL` tenía por defecto `"llama3.2:3b"`, un tag que no coincidía con el modelo realmente descargado (`llama3.2:latest`), así que cualquier instrucción devolvía un 404 de Ollama. `main.py` además atrapaba cualquier `requests.RequestException` bajo el mismo mensaje "No pude conectar con Ollama", escondiendo que en realidad sí había conexión pero el modelo no existía. Se corrigió el default a `"llama3.2"` y se separaron los mensajes: error de conexión real (`ConnectionError`) vs. respuesta de error HTTP (`HTTPError`, ej. modelo no encontrado) vs. cualquier otro error de la petición.

Pruebas (`tests/test_grabador.py`, `tests/test_transcriptor.py`): igual que con Ollama, nunca se toca hardware ni modelo real -- se reemplazan `sounddevice.rec`/`wait` y `WhisperModel` por versiones falsas.

Siguiente paso: Fase 6, salida de voz con Piper.
