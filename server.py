from flask import Flask, jsonify, request
import os

import setting
import extract

app = Flask(__name__)

@app.route('/api/upload', methods=['POST'])
def upload():
  file = request.files['file']
  base = os.path.dirname(__file__)
  upload_path = os.path.join(base, setting.HOST_MOUNT, 'imgs', file.filename)
  file.save(upload_path)
  print('上传成功')

  config, html = extract.formExtract('imgs/' + file.filename)

  return jsonify({
    'config': config,
    'html': html,
    'msg': '上传成功'
  })

if __name__ == '__main__':
  app.run(debug=True, port=7777)
