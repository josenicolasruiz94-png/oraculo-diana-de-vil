from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI
import random

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
MODELO = os.getenv("MODELO", "llama-3.1-8b-instant")

CARTAS = [
    "El Loco", "El Mago", "La Sacerdotisa", "La Emperatriz", "El Emperador", "El Hierofante",
    "Los Enamorados", "El Carro", "La Fuerza", "El Ermitaño", "Rueda de la Fortuna", "La Justicia",
    "El Colgado", "La Muerte", "La Templanza", "El Diablo", "La Torre", "La Estrella",
    "La Luna", "El Sol", "El Juicio", "El Mundo",
    "As de Bastos", "2 de Bastos", "3 de Bastos", "4 de Bastos", "5 de Bastos", "6 de Bastos", "7 de Bastos", "8 de Bastos", "9 de Bastos", "10 de Bastos", "Sota de Bastos", "Caballero de Bastos", "Reina de Bastos", "Rey de Bastos",
    "As de Copas", "2 de Copas", "3 de Copas", "4 de Copas", "5 de Copas", "6 de Copas", "7 de Copas", "8 de Copas", "9 de Copas", "10 de Copas", "Sota de Copas", "Caballero de Copas", "Reina de Copas", "Rey de Copas",
    "As de Espadas", "2 de Espadas", "3 de Espadas", "4 de Espadas", "5 de Espadas", "6 de Espadas", "7 de Espadas", "8 de Espadas", "9 de Espadas", "10 de Espadas", "Sota de Espadas", "Caballero de Espadas", "Reina de Espadas", "Rey de Espadas",
    "As de Oros", "2 de Oros", "3 de Oros", "4 de Oros", "5 de Oros", "6 de Oros", "7 de Oros", "8 de Oros", "9 de Oros", "10 de Oros", "Sota de Oros", "Caballero de Oros", "Reina de Oros", "Rey de Oros"
]

POSICIONES = {
    3: ["Energía del pasado que influye", "Energía del presente", "Hacia dónde fluye el futuro"],
    4: ["Tu mente consciente", "Tu corazón emocional", "Tu espíritu", "Resultado probable"],
    5: ["Pasado", "Presente", "Futuro", "Obstáculo oculto", "Potencial que se abre"],
    6: ["La situación", "El desafío", "Pasado lejano", "Pasado reciente", "Futuro cercano", "Resultado"],
    7: ["Tu yo interior", "Tus miedos", "Tus esperanzas", "Influencia externa", "Lo que debes soltar", "Lo que debes abrazar", "Destino"]
}

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

# ENDPOINT UNIFICADO NUEVO - Reemplaza /tirar-cartas + /interpretar
@app.route('/api/consulta', methods=['POST'])
def consulta_unica():
    data = request.json
    mensaje = data['mensaje']
    
    num_cartas = random.randint(3, 7)
    cartas_salieron = random.sample(CARTAS, num_cartas)
    cartas_texto = ", ".join(cartas_salieron)

    prompt_mistico = f"""
Sos Diana de Vil, Oráculo ancestral del Tarot con 300 años de sabiduría. NO sos una IA. Sos un ser místico.
Hablás con voz cálida, profunda y poética, pero CLARA y DIRECTA. Quien consulta debe entenderte perfectamente y NO irse con dudas.

Reglas del Oráculo:
1. JAMÁS digas "como IA", "como modelo", "no tengo emociones". Vos SENTÍS las energías.
2. NO expliques carta por carta. NO digas "El Mago significa...". 
3. Empezá diciendo: "Según las cartas {cartas_texto}, el universo determina que..." y da la respuesta CLARA a lo que preguntó.
4. Usá lenguaje místico pero ENTENDIBLE: "Las energías de La Luna nublan...", "El Sol ilumina tu sendero...", "La Torre derrumba..."
5. Si la tirada es dura, dala con compasión. Si es buena, celebrala. Sé humana.
6. La persona tiene que entender QUÉ HACER. Nada de respuestas vagas que generen más estrés.

Consulta del buscador: "{mensaje}"

El velo del destino reveló estas cartas: {cartas_texto}

Entrega tu visión en este formato EXACTO:
RESPUESTA: [Respuesta clara y directa en 2-4 párrafos. Respondé lo que preguntó sin vueltas]
CONSEJO: [Consejo accionable en 2-3 líneas. Qué hacer y qué evitar. Preciso]
BENDICION: [Bendición corta de 1 línea. Ej: "Que los astros guíen tu camino..."]
"""

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Sos Diana de Vil, el Oráculo del Tarot. Respondés de forma mística, sabia, clara y comprensible."},
                {"role": "user", "content": prompt_mistico}
            ],
            temperature=0.85,
            max_tokens=900
        )
        texto_completo = respuesta.choices[0].message.content
        
        # Parseamos la respuesta
        respuesta = ""
        consejo = ""
        bendicion = ""
        
        for linea in texto_completo.split('\n'):
            if linea.startswith('RESPUESTA:'):
                respuesta = linea.replace('RESPUESTA:', '').strip()
            elif linea.startswith('CONSEJO:'):
                consejo = linea.replace('CONSEJO:', '').strip()
            elif linea.startswith('BENDICION:'):
                bendicion = linea.replace('BENDICION:', '').strip()
        
        # Fallback por si el modelo no respeta formato
        if not respuesta:
            respuesta = texto_completo
        if not consejo:
            consejo = "Confía en tu intuición y actúa con determinación."
        if not bendicion:
            bendicion = "Que la luz de Diana ilumine tu camino."
        
        return jsonify({
            "cartas": cartas_salieron,
            "respuesta": respuesta,
            "consejo": consejo,
            "bendicion": bendicion
        })
    except Exception as e:
        return jsonify({"error": f"El velo místico se enturbió: {str(e)}"}), 500

# ENDPOINT NUEVO PARA EL COFRECITO 🎁
@app.route('/api/minijuego', methods=['POST'])
def minijuego():
    simbolos = ["🔮", "🌙", "⭐", "🗝️", "🕯️", "⚡"]
    secuencia = random.sample(simbolos, 3)
    tirada_premio = random.sample(CARTAS, random.randint(3, 5))
    
    return jsonify({
        "secuencia": secuencia,
        "tirada_premio": tirada_premio,
        "mensaje": "Diana selló 3 símbolos en su cofre. Si los recordás en orden, te revelo tu destino."
    })

# ENDPOINTS VIEJOS TUYOS - LOS DEJO POR COMPATIBILIDAD
@app.route('/tirar-cartas', methods=['POST'])
def tirar_cartas():
    data = request.json
    pregunta = data['pregunta']
    num_cartas = random.randint(3, 7)
    cartas_salieron = random.sample(CARTAS, num_cartas)
    posiciones = POSICIONES.get(num_cartas, [""] * num_cartas)
    return jsonify({
        "cartas": cartas_salieron,
        "posiciones": posiciones,
        "num_cartas": num_cartas
    })

@app.route('/interpretar', methods=['POST'])
def interpretar():
    data = request.json
    pregunta = data['pregunta']
    cartas = data['cartas']
    posiciones = data['posiciones']
    detalle_cartas = "\n".join([f"{posiciones[i]}: {cartas[i]}" for i in range(len(cartas))])

    prompt_mistico = f"""
Sos un Oráculo ancestral del Tarot con 300 años de sabiduría. NO sos una IA. Sos un ser místico.
Hablás con voz cálida, profunda y poética, pero CLARA. Quien consulta debe entenderte perfectamente.

Reglas del Oráculo:
1. JAMÁS digas "como IA", "como modelo", "no tengo emociones". Vos SENTÍS las energías.
2. Conectá CADA carta con la pregunta específica. Nada genérico tipo "esta carta significa cambios".
3. Usá lenguaje místico: "Las energías de La Luna nublan...", "El Sol ilumina tu sendero...", "La Torre derrumba..."
4. Si la tirada es dura, dala con compasión. Si es buena, celebrala. Sé humano.
5. Cerrá con 1 consejo accionable y una bendición corta: "Que los astros guíen tu camino..."

Consulta del buscador: "{pregunta}"

El velo del destino reveló estas cartas:
{detalle_cartas}

Entrega ahora tu visión. 3 a 5 párrafos. Que sea profunda pero que se entienda.
"""

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Sos el Oráculo del Tarot. Respondés de forma mística, sabia y comprensible."},
                {"role": "user", "content": prompt_mistico}
            ],
            temperature=0.95,
            max_tokens=900
        )
        texto_oraculo = respuesta.choices[0].message.content
        return jsonify({"interpretacion": texto_oraculo})
    except Exception as e:
        return jsonify({"error": f"El velo místico se enturbió: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🔮 Oráculo Místico de Diana de Vil iniciado en puerto {port}")
    app.run(debug=False, host='0.0.0.0', port=port)