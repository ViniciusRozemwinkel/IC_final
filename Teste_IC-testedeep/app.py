from flask import Flask, render_template, request, jsonify, send_file
from Solver.bottom_left_packing import bottom_left_packing, Furnace  , Piece
from Solver.generate_pdf import generate_pdf
import os

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("Workstation.html")

@app.route('/alocar-pecas', methods=['POST'])
def alocar_pecas():
    data = request.json

    # Verifica se os dados foram recebidos corretamente
    if not data or 'forno' not in data or 'pecas' not in data:
        return jsonify({'success': False, 'message': 'Dados inválidos ou ausentes.'}), 400

    forno_data = data['forno']
    pecas_data = data['pecas']

    # Cria o objeto Furnace com os dados recebidos
    furnace = Furnace(forno_data['comprimento'], forno_data['largura'], forno_data['altura'], forno_data['prateleiras'])

    # Cria os objetos Piece com os dados recebidos
    pieces = [Piece(p['type'], p['length'], p['width'], p['height'], p['quantity']) for p in pecas_data]

    # Tenta alocar as peças no forno
    result = bottom_left_packing(furnace, pieces)

    if isinstance(result, str):
        # Se o resultado for uma string, significa que houve um erro
        return jsonify({'success': False, 'message': result}), 400
    else:
        # Se a alocação foi bem-sucedida, gera um PDF com a disposição das peças
        pdf_filename = "output.pdf"
        generate_pdf(result, pdf_filename)
        # Retorna a URL para download do PDF
        return jsonify({'success': True, 'pdf_url': f"/download-pdf/{pdf_filename}"})

@app.route('/download-pdf/<filename>')
def download_pdf(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)