from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import openai
import os

app = Flask(__name__)

# Pega a API Key da variável de ambiente
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

    # 🔥 Limpeza opcional do texto extraído (antes de enviar para o GPT)
    page_text = page_text.replace('\n', ' ').replace('\r', ' ').strip()
    page_text = ' '.join(page_text.split())

    prompt = f"Resuma o texto a seguir de forma clara e objetiva: {page_text[:4000]}"

    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": " Create a LinkedIn post based on the provided text or theme that maintains a professional, inspiring, and natural tone while subtly integrating your experience with the topic at hand. Include elements from your professional background, when possible, such as leadership of IT teams and projects, delivery of innovation and digital transformation, application of agile methodologies, significant experiences at Sensedia (API Management) and TIM Brasil (major projects, cross-functional leadership, team and large budget management). You should also highlight skills such as Lean Six Sigma, education in international business and technology, Yellow Belt certification, and a national innovation award in processes. The purpose of the post is to share lessons learned and encourage networking by showcasing your ability to impact new challenges without explicitly mentioning you're looking for a job change. Connect smoothly with the theme, add value to the discussion, and demonstrate expertise on the subject. Write in post format suitable for LinkedIn, maintaining clarity and conciseness. Ensure the post connects to the theme fluidly, adds value to the discussion, and exhibits authority and professionalism throughout. Keep in mind to showcase your experience subtly in the post without explicitly stating a desire to change jobs, focusing on the impact and value you bring to discussions and projects.   "},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        resumo = gpt_response.choices[0].message.content

        # 🔥 Limpeza do texto retornado pelo GPT
        resumo = resumo.replace('\n', ' ').replace('\r', ' ').strip()
        resumo = ' '.join(resumo.split())

    except Exception as e:
        return jsonify({"error": f"Erro ao chamar o ChatGPT: {str(e)}"}), 500

    return jsonify({"resumo": resumo})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
