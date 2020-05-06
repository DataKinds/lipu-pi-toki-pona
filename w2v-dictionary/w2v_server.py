from flask import Flask, Response
import json
from w2v_dict import load_words, load_tp_words, get_string_vector

api = Flask(__name__)

words, DIMS = load_words()

tp_words = load_tp_words(words)

@api.route('/dict/<string>', methods=['GET'])
def dict(string):
    print(f"Querying {string}")
    vec = get_string_vector(words, string, verbose=True)

    if vec is None:
        return "Word not found!"

    angles = [(word, word.angle_to(vec)) for word in tp_words]
    goods = sorted(angles, key=lambda pair: pair[1])

    res = json.dumps([{"word": word.get_subword(), "ext": word.get_ext(), "angle": angle} for word, angle in goods])

    return Response(res, mimetype='text/xml')

if __name__ == '__main__':
    api.run(port=58008)
