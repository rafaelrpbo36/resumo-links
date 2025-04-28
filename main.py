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
                {"role": "system", "content": " Crie um post para o LinkedIn com até 1300 caracteres, com tom profissional, inspirador e voltado para profissionais de tecnologia, inovação ou gestão. O texto deve abordar de forma natural sem citar minha trajetória pessoal temas ligados a estas palavras-chave: Open Finance, API Management, integração de sistemas, liderança de times de TI, projetos ágeis, inovação digital, eficiência operacional, experiência do cliente, transformação tecnológica e estratégia de expansão de negócios. Desenvolva uma reflexão prática, um aprendizado, uma tendência ou uma dica de boas práticas nesses temas, como se estivesse compartilhando uma visão de mercado ou uma inspiração profissional. O post deve soar como um convite à reflexão e terminar com uma pergunta para incentivar a interação, por exemplo: Como você tem enfrentado esse desafio, Quais práticas têm funcionado melhor para você ou Que tendências você vê surgindo nesse contexto."},
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
