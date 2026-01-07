import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

import numpy as np

image_size = 150

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-key-for-dev')

# app.secret_key = "your_secret_key_here"
# submitボタンを押した際にエラーが出た場合上の行のコメントアウトを削除し、your_secret_key_hereに任意の文字列(例:aidemy)を指定し、再度アプリケーションを実行してください。

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

model = load_model('./my_model.keras') #学習済みモデルをロード

@app.route('/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            img = image.load_img(filepath, color_mode='rgb', target_size=(image_size,image_size))
            img_x = image.img_to_array(img)
            img_x = np.expand_dims(img_x, axis=0)
            img_x = img_x / 255.0

            prediction = model.predict(img_x)
            prediction_value = float(np.ravel(prediction)[0])

            if prediction_value < 0.5:
                res = "これはピザです"
                # 0に近いほど確信度が高いので、逆転させて表示
                conf = "ピザ度：" + str(round((1 - prediction_value) * 100, 4)) + "%"
            else:
                res = "これはピザではありません"
                conf = "ピザ度：" +  str(round((1 - prediction_value) * 100, 4)) + "%"

            return render_template("index.html", answer=res, confidence=conf)
    
    return render_template("index.html", answer="", confidence="")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0', port = port)