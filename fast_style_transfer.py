from flask import Flask, url_for, render_template, request, flash, redirect, jsonify #, session
from werkzeug.utils import secure_filename
import os

import threading
import subprocess
import uuid

# from flask_script import Manager
from fst import evaluate

app =Flask(__name__)

# UPLOAD_FOLDER = '/Users/joysword/Development/github/fast-style-transfer/static/content'
UPLOAD_FOLDER = os.path.join(app.static_folder, 'content')
STYLE_FOLDER = os.path.join(app.static_folder, 'style')
CHECKPOINT_FOLDER = os.path.join(app.static_folder, 'checkpoints')
RESULT_FOLDER = os.path.join(app.static_folder, 'results')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

FST_FOLDER = 'fst'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STYLE_FOLDER'] = STYLE_FOLDER

background_scripts = {}

def run_evaluation(id, style, filename):
    print 'in run_evaluation'
    ckpt = ''
    if style == 'chinese' or style == 'picasso':
        ckpt = os.path.join(CHECKPOINT_FOLDER, style)
    else:
        ckpt = os.path.join(CHECKPOINT_FOLDER, style+'.ckpt')
    print 'calling subprocess'
    print 'ckpt:', ckpt
    print 'in-path:', os.path.join(UPLOAD_FOLDER, filename),
    print 'out-path:', RESULT_FOLDER
    subprocess.call([FST_FOLDER+'/evaluate.py',
        '--checkpoint', ckpt,
        '--in-path', os.path.join(UPLOAD_FOLDER, filename),
        '--out-path', RESULT_FOLDER])
    # subprocess.call([FST_FOLDER+'/test.py',
    #     '--hello', 'true', '--good', 'false'])
    background_scripts[id] = True
    print 'out run_evaluation'

# manager = Manager(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_styles():
    imgs = []
    for img in os.listdir(app.config['STYLE_FOLDER']):
        imgs.append(img)
    return imgs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'style' not in request.form:
            flash('No style selected')
            return redirect(request.url)
        style = request.form['style'].split('.')[0]
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # TODO: what if the file name exist?
        print 'filename:', filename
        print 'style:', style
        return redirect(url_for('evaluate', filename=filename, style=style))
    else:
        return render_template('index.html', styles=get_styles())

@app.route('/evaluate/<style>/<filename>')
def evaluate(style, filename):
    print 'in evaluate'
    id = str(uuid.uuid4())
    background_scripts[id] = False
    threading.Thread(target=lambda: run_evaluation(id, style, filename)).start()
    print 'started thread'
    return render_template('processing.html', id=id, filename=filename, style=style)

@app.route('/get_result')
def get_result():
    id = request.args.get('id', None)
    if id not in background_scripts:
        abort(404)
    return jsonify(done=background_scripts[id])

@app.route('/show_result/<style>/<filename>')
def show_result(style, filename):
    new_name = filename.split('.')[0]+'_'+style+'.'+filename.split('.')[1]
    os.rename(os.path.join(RESULT_FOLDER, filename), os.path.join(RESULT_FOLDER, new_name))
    return '<img src="' + url_for('static', filename='results/'+new_name) + '" />'

if __name__ == '__main__':
    app.run()


