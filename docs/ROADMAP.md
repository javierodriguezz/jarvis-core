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

### Fase 6.5 — Conexión a IA en la nube (semana 17)
Fase agregada sobre la marcha, fuera del plan original. Hasta aquí, Jarvis solo sabía responder preguntas predefinidas o cálculos aritméticos: el LLM local (Fase 3) se usa para elegir herramienta, no para conversar. Se conecta la API de Gemini como una herramienta más del registro, de modo que las preguntas abiertas tengan una respuesta real en vez de un "no entendí". El resto del proyecto sigue siendo local; esta es la única pieza que sale a internet.

### Fase 7 — Palabra de activación (semanas 18-19)
openWakeWord para detectar "Jarvis" y activar la escucha, en vez de tener que ejecutar el programa manualmente cada vez.

### Fase 8 — Funciones extra (semanas 20-23)
Recordatorios y calendario, control de música, búsqueda de documentos más avanzada. Cada una se agrega como una nueva herramienta en el registro — el patrón ya está probado.

### Fase 9 — Estabilidad y arranque automático (semanas 24+)
Inicio automático con el sistema (Task Scheduler de Windows), manejo robusto de errores para que no se caiga tras horas corriendo, revisión de consumo de memoria/CPU en ejecución prolongada. Esta fase es abierta — "24 horas estable" es una meta de mejora continua, no un checkbox único.

**Estimado total hasta una versión "24 horas" razonablemente estable: ~6 meses a este ritmo.** Si el semestre se complica, lo normal y esperable es que esto se estire — la prioridad es que entiendas cada pieza, no la velocidad.

---

## 5. Próximo paso inmediato

Fase 0 a Fase 6.5 completas. Fase 7 en curso.

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

Fase 6: salida de voz con `piper-tts` (paquete de Python que envuelve Piper -- a diferencia de Whisper, esta vez el pip install trajo una rueda precompilada para Windows sin necesidad de compilar nada, ni siquiera en Python 3.14). Se agregó `jarvis/audio/sintetizador.py`, simétrico a `transcriptor.py`: `sintetizar(texto)` regresa `(audio, sample_rate)`, con la voz de Piper cacheada a nivel de módulo (`_voz`) para no releerla del disco en cada llamada. El `sample_rate` se regresa junto con el audio en vez de asumirlo fijo, porque es propio de cada voz (22050 Hz para la elegida) y distinto de `config.AUDIO_SAMPLE_RATE` (16000 Hz, el de *entrada* por micrófono) -- son dos frecuencias independientes.

La voz se eligió probando varias en voz alta con la misma frase de prueba: se descartó `es_MX-ald-medium` (sonaba artificial) a favor de `es_ES-davefx-medium`, con un tono más formal ("de mayordomo"). El nombre de la voz es configurable vía `config.PIPER_VOICE` (`.env`, por defecto `es_ES-davefx-medium`, mismo patrón que `WHISPER_MODEL`); sus archivos (`.onnx` y `.onnx.json`, ~63 MB) se descargan una sola vez a `data/voices/` con `python -m piper.download_voices` y no se suben a git (`data/voices/` en `.gitignore`, igual que `data/*.db`).

`main.py` agrega `hablar(texto)`: imprime la respuesta y además la reproduce con `sounddevice.play()` -- ya era dependencia del proyecto desde la Fase 5, así que no se agregó nada nuevo para la reproducción. Cada `print(respuesta)` que ya existía en el loop principal (incluyendo "no entendí" y los errores de conexión con Ollama) se reemplazó por `hablar(respuesta)`, sin duplicar la lógica de historial que ya seguía después.

De paso se encontró un problema, no arquitectónico sino de contenido: `decir_hora()` (Fase 1) devolvía la fecha como `"12/09/2026"`, que Piper leía literalmente ("doce barra cero nueve barra dos mil veintiséis") porque el sintetizador no sabe que esos números son una fecha. Se corrigió para que arme la fecha con el nombre del mes en español (`"12 de septiembre de 2026"`), usando una lista fija de nombres de mes (`_MESES`) en vez de depender del locale del sistema operativo, que no es confiable entre máquinas Windows. Se actualizó también `test_decir_hora_incluye_fecha_de_hoy` en `tests/test_basic_tools.py` para que compare contra el nuevo formato.

Pruebas (`tests/test_sintetizador.py`): mismo patrón que `test_transcriptor.py` -- se reemplaza `PiperVoice.load` por una voz falsa, nunca se toca el modelo real ni el hardware de audio.

Fase 6.5: conexión a una IA en la nube (Gemini) para preguntas abiertas. Nació de una pregunta de Javier -- un asistente que solo contesta lo predefinido sirve de poco -- y se resolvió sin tocar la arquitectura, porque el patrón de "lista blanca + ejecutor" ya estaba hecho para esto: la IA entra como una herramienta más, no como una excepción.

- `jarvis/core/gemini_client.py`: gemelo de `llm_client.py`, pero contra la API de Gemini. `generar(pregunta, instruccion_sistema)` hace el POST y deja propagar los errores de `requests`, igual que el de Ollama. La clave viaja en el header `x-goog-api-key` y no pegada a la URL, porque las URLs terminan escritas en los logs de cualquier servidor intermedio. `_extraer_texto()` valida la respuesta anidada en vez de confiar en que las llaves existan: Gemini puede contestar 200 y aun así no traer texto (por ejemplo cuando sus filtros de seguridad bloquean algo), y un `KeyError` ahí habría tumbado el loop de `main.py`.
- `jarvis/tools/ia_tools.py`: la herramienta `preguntar_ia`, en su propio módulo y no en `basic_tools.py`, porque depende de un servicio externo -- misma lógica por la que la voz tuvo su propio paquete en la Fase 5. Nunca lanza excepciones: `executor.execute()` llama a las herramientas sin `try/except`, así que cualquier excepción que se escapara tumbaría el programa en vez de dar un mensaje.
- `config.py`: `GEMINI_API_KEY` (vacía por defecto, cada quien pone la suya en `.env`) y `GEMINI_MODEL`.
- `main.py`: la rama de "No entendí esa instrucción" se sustituyó por un `ToolCall` a `preguntar_ia`, que cae al mismo camino de siempre (`executor.execute` → `hablar` → `historial`). Ese respaldo cubre los casos en que el modelo local responde `null`, inventa una herramienta o devuelve JSON inválido.
- `jarvis/core/interpreter.py`: tres ejemplos nuevos en `PROMPT_BASE`. Uno ancla `preguntar_ia` para conocimiento general, pero el importante es el de `responder_pregunta` con un cálculo: al meter dos herramientas casi gemelas (las dos "responden preguntas", las dos reciben un parámetro `pregunta`), había que anclar los dos lados y no solo el nuevo, o el modelo de 3B empezaría a mandar todo a la nube.

Tres cosas que solo aparecieron al probar con una clave real, y que valen como lección:

1. El alias `gemini-flash-latest` existe pero responde 503 seguido, por ser el que todos usan por defecto. `gemini-2.5-flash` ya devuelve 404 para cuentas nuevas (Google lo retiró). El default quedó en `gemini-3.6-flash`, que es justo el que recomienda el mensaje de error de Google.
2. El mensaje de error para un 503 decía "puede ser la clave de API o el nombre del modelo" -- falso y peor que inútil, porque manda a revisar lo que está bien. Ahora cada código HTTP tiene su propio mensaje (403 la clave, 404 el modelo, 429 la cuota, 503 saturación de Google), y hay una prueba que verifica que el de 503 no mencione la clave.
3. Gemini responde en Markdown y se extiende: negritas, listas, encabezados. Leído en voz alta por Piper, eso son asteriscos dictados y respuestas eternas. Se resolvió por los dos lados: una instrucción de sistema que pide texto plano y dos o tres frases, más `_quitar_markdown()` como red por si el modelo la ignora. Es el mismo problema que la fecha con diagonales de la Fase 6 -- conviene revisar con esa óptica cualquier texto nuevo que vaya a salir por voz.

Pruebas (`tests/test_gemini_client.py`, `tests/test_ia_tools.py`): ninguna sale a internet ni gasta cuota. El cliente se prueba simulando `requests.post`; la herramienta se prueba simulando `gemini_client.generar`, que es la capa inmediatamente inferior -- el mismo patrón por capas que ya usaban `test_llm_client.py` y `test_interpreter.py`.

Fase 7 (en curso, NO terminada): palabra de activación con openWakeWord. El código está escrito y probado, pero la detección todavía no funciona con la voz de Javier -- ver "Lo que falta" al final de esta sección.

La idea: un detector de palabra de activación es un modelo diminuto que solo contesta "¿está la frase X en este pedacito de audio?", muchas veces por segundo. Es el `if` barato que va antes de la función cara: Whisper (~140 MB, segundos por transcripción) no puede correr en bucle continuo, este modelo sí -- medido en esta máquina, procesa 4 segundos de audio en 0.078 s y carga en 0.12 s.

- `openwakeword` se instaló con pip sin problemas en Python 3.14. No trajo motor de inferencia como dependencia, pero `onnxruntime` ya estaba instalado desde la Fase 6 (lo arrastró `piper-tts`), así que no hubo nada que resolver ahí.
- El modelo no hubo que entrenarlo: openWakeWord trae modelos pre-entrenados y uno de ellos es `hey_jarvis`. Se descargan una sola vez con `openwakeword.utils.download_models(model_names=['hey_jarvis'])` y quedan dentro del paquete, igual que el modelo de Whisper queda en su cache -- no en `data/`.
- Detecta la frase completa "hey Jarvis", no "Jarvis" a secas. Una sola palabra corta da demasiados falsos positivos; por eso todos los asistentes comerciales usan frases de dos o tres sílabas ("Hey Siri", "OK Google").
- `jarvis/audio/detector.py`: `esperar_palabra_activacion()` bloquea hasta oír la frase. Abre el micrófono con `sd.InputStream` y lo lee en bloques de exactamente 1280 muestras (80 ms a 16000 Hz), que es el tamaño que exige el modelo; internamente él guarda el último ~1.5 s, por eso reconoce una frase completa aunque se le entregue en migajas. El modelo se cachea a nivel de módulo, mismo patrón que `transcriptor.py` y `sintetizador.py`.
- Trampa importante del formato: openWakeWord consume `int16` (enteros de 16 bits), mientras que `grabador.py` entrega `float32` entre -1.0 y 1.0 porque es lo que quiere Whisper. Es la misma señal en dos representaciones distintas. Si se le pasa la equivocada no truena: simplemente nunca detecta nada. Por eso el detector abre su propio stream en `int16` en vez de convertir, y hay una prueba (`test_abre_el_microfono_en_int16_y_no_en_float32`) que lo fija.
- `config.py`: `WAKEWORD_MODEL` (por defecto `hey_jarvis`) y `WAKEWORD_THRESHOLD` (por defecto 0.5), sobreescribibles en `.env` igual que `WHISPER_MODEL` y `PIPER_VOICE`.
- `grabador.py`: se le agregó el parámetro `cuenta_regresiva` (por defecto `True`, comportamiento de siempre). En el modo manos libres se apaga: la cuenta de 3 segundos existía porque el usuario escribía `voz` y necesitaba prepararse, pero después de decir "hey Jarvis" ya viene hablando y esos 3 segundos se comerían su pregunta.
- `main.py`: antes de agregar nada se extrajo la tubería (interpretar → ejecutar → responder → historial) del cuerpo del bucle a `procesar_texto(texto)`, para que el modo nuevo la reutilizara en vez de duplicarla. `modo_escucha()` es el bucle manos libres: espera la palabra, contesta "¿Sí?" en voz alta (hace de campanita, avisa que ya está grabando), graba sin cuenta regresiva, transcribe y llama a `procesar_texto()`. Se sale con Ctrl+C, que regresa al prompt de texto -- el modo escrito se conservó a propósito porque sigue siendo la forma cómoda de depurar.
- `main.py` imprime ahora "Transcribiendo...", "Pensando..." y "Respondiendo...". Sin eso la consola se queda muda unos 6 segundos (2.4 s de Ollama + 1.7 s de síntesis + 1.7 s de reproducción, medidos) y el programa parece colgado. De hecho se reportó como un bug ("se quedó, no me dio respuesta") y no lo era.
- Pruebas: `tests/test_detector.py` (7, con micrófono y modelo falsos) y `tests/test_main.py` (5, sobre el bucle de `modo_escucha` con todo simulado), más 2 nuevas en `test_grabador.py` para la cuenta regresiva. Suite completa: 126.

Lo que falta (por dónde retomar): el modelo no alcanza el umbral con la voz de Javier. Medido con un diagnóstico numérico sobre el micrófono real:

- Volumen máximo de entrada: 12441 de 32767 -- el micrófono está bien, no es problema de ganancia.
- Ruido de fondo y habla normal: puntajes de 0.02 a 0.09.
- Diciendo "hey Jarvis": máximo 0.2603, con intentos que se quedaron en 0.13.
- Umbral configurado: 0.5. Nunca lo cruza, por eso el modo escucha no reacciona.

Bajar el umbral a secas no es solución: habría que ponerlo cerca de 0.2, demasiado pegado al ruido de fondo, y aun así no atraparía todos los intentos. La hipótesis principal es la pronunciación -- el modelo fue entrenado con voces en inglés, donde la "J" suena /dʒ/ ("Yarvis"), muy distinta de la /x/ del español ("Járvis"). El plan para medirlo es grabar dos WAV (uno pronunciando a la inglesa, otro a la española) y comparar sus puntajes fuera de línea, en vez de repetir pruebas en vivo a ciegas. El script que hace esa grabación (16000 Hz, int16, el formato que consume el detector) quedó en una carpeta temporal fuera del repo, así que probablemente haya que rehacerlo: son unas 20 líneas con `sd.rec()` y el módulo `wave`.

Dos callejones sin salida ya descartados, para no repetirlos:

1. `Model.reset()` no es el culpable. Se sospechó porque era la única línea que el script de prueba manual no tenía, pero su código fuente deja los buffers exactamente igual que un modelo recién construido.
2. No sirve probar el detector con audio generado por Piper. Se intentó sintetizar "hey Jarvis" para tener una prueba reproducible sin micrófono, y el modelo dio 0.0002: estos modelos no reaccionan a voces sintéticas. Cualquier prueba de detección real necesita voz humana grabada.

Siguiente paso concreto: grabar los dos WAV de muestra, medir cuál pronunciación puntúa más alto, y con eso decidir entre calibrar el umbral, cambiar de frase de activación, o entrenar un modelo propio con la voz de Javier (openWakeWord lo permite).
