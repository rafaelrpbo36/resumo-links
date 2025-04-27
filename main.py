from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import openai
import os

app = Flask(__name__)

openai_api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

@app.route('/', methods=['POST'])
def resumir_link():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "Parâmetro 'url' obrigatório."}), 400

    url = data['url']

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar a URL: {str(e)}"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text()

    prompt = f"Resumo do texto extraído: {page_text[:4000]}"

    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Faça um post para que eu poste no linkedin"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        resumo = gpt_response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": f"Erro ao chamar o ChatGPT: {str(e)}"}), 500

    return jsonify({"resumo": resumo})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
