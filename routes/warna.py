from flask import Blueprint, jsonify

warna_blueprint = Blueprint('warna', __name__)

@warna_blueprint.route('/api/json/warna/<warna>', methods=['GET'])
def get_warna(warna):
    if warna == 'Merah':
        palet = [
            {
                "warna": "Merah",
                "strWarna": "Kombinasi Warna Merah",
                "strWarnaThumb": "http://192.168.1.25:5000/img/merah.jpg",
                "strDesc": "Kombinasi warna merah dengan nuansa lain seperti oranye, hijau, ungu, dan merah muda dapat menciptakan berbagai suasana dan gaya. Kombinasi ini dapat digunakan dalam berbagai konteks, mulai dari dekorasi interior hingga mode pakaian, tergantung pada efek yang ingin dicapai. Dengan memilih kombinasi yang tepat, Anda dapat menciptakan desain yang menarik dan harmonis.",
            }
        ]
    elif warna == 'Hijau':
        palet = [
            {
                "warna": "Hijau",
                "strWarna": "Kombinasi Warna Hijau",
                "strWarnaThumb": "http://192.168.1.25:5000/img/hijau.jpg",
                "strDesc": "Kombinasi warna hijau dengan nuansa lain seperti biru, kuning, merah muda, dan ungu dapat menciptakan berbagai suasana dan gaya. Kombinasi ini dapat digunakan dalam berbagai konteks, mulai dari dekorasi interior hingga mode pakaian, tergantung pada efek yang ingin dicapai. Dengan memilih kombinasi yang tepat, Anda dapat menciptakan desain yang menarik dan harmonis.",
            }
        ]
    elif warna == 'Biru':
        palet = [
            {
                "warna": "Biru",
                "strWarna": "Kombinasi Warna Biru",
                "strWarnaThumb": "http://192.168.1.25:5000/img/biru.jpg",
                "strDesc": "Kombinasi warna biru dengan nuansa lain seperti hijau, abu-abu, oranye, dan ungu dapat menciptakan berbagai suasana dan gaya. Kombinasi ini dapat digunakan dalam berbagai konteks, mulai dari desain interior hingga mode pakaian, tergantung pada efek yang ingin dicapai. Dengan memilih kombinasi yang tepat, Anda dapat menciptakan desain yang menarik dan harmonis.",
            }
        ]
    else:
        return jsonify({"message": "Palet Warna not found"})

    return jsonify({"palet": palet})