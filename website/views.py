import shutil
from flask import Blueprint, flash, request, redirect, render_template, url_for
from werkzeug.utils import secure_filename
import os
from .cbir import cbir
from .yoloDeepSort import yoloDeepSort
from .ocr import ocr
from collections import defaultdict

views = Blueprint('views', __name__)
videos = []
queryImage = []

@views.route('/')
def index():
    videos = [f for f in os.listdir('videos') if f.endswith(('.mp4', '.mkv', '.MP4', '.MKV', '.avi', '.AVI', '.mov', '.MOV', '.wmv', '.WMV', '.flv', '.FLV', '.webm', '.WEBM'))]
    queryImage = [f for f in os.listdir('website/static/queryImage') if f.endswith(('.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG'))]
    print(videos)
    print(queryImage)
    return render_template('index.html', videos=videos, queryImage=queryImage)

@views.route('/run', methods=['POST'])
def run():
    if request.method == 'POST':
        result_paths = defaultdict(list)
        queries = request.form.getlist('queryImage')
        if(len(queries) == 0):
            flash("No query image selected")
            return redirect(url_for('views.index'))
        print(queryImage)
        video = request.form['video']
        # delete if directory exists
        if(not os.path.isdir('videos/outputs/crops/{}'.format(video.split('.')[0]))):
            os.mkdir('videos/outputs/crops/{}'.format(video.split('.')[0]))
            yoloDeepSort(video)
        result_paths = cbir(video.split('.')[0], queries)
        if(request.form.get('plate') != ''):
            if(not os.path.isdir('videos/outputs/ocr/{}'.format(video.split('.')[0]))):
                os.mkdir('videos/outputs/ocr/{}'.format(video.split('.')[0]))
            ocr(video.split('.')[0])
        print(result_paths)
        print(request.form.get('plate'))
        return render_template('run.html', result_paths=result_paths)
    
@views.route('/saveMatches', methods=['POST'])
def saveMatches():
    if request.method == 'POST':
        for i in request.form.getlist('matches'):
            shutil.copy(i, 'website/static/queryImage/')
        return redirect(url_for('views.index'))
    
@views.route('addQueryImage', methods=['POST'])
def addQueryImage():
    if request.method == 'POST':
        if 'queryImage' not in request.files:
            flash('No file part')
            print("No file part")
            return redirect(url_for('views.index'))
        file = request.files['queryImage']
        if file.filename == '':
            flash('No selected file')
            print("No selected file")
            return redirect(url_for('views.index'))
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('website/static/queryImage', filename))
    return redirect(url_for('views.index'))

@views.route('/startFresh', methods=['POST'])
def startFresh():
    if request.method == 'POST':
        if(os.path.isdir('videos/outputs/crops/')):
            shutil.rmtree('videos/outputs/crops/')
        if(os.path.isdir('website/static/queryImage')):
            shutil.rmtree('website/static/queryImage')
        if(os.path.isdir('website/static/resultImage')):
            shutil.rmtree('website/static/resultImage')
        if(os.path.isdir('videos/outputs/ocr/')):
            shutil.rmtree('videos/outputs/ocr/')
        os.mkdir('videos/outputs/ocr/')
        os.mkdir('videos/outputs/crops/')
        os.mkdir('website/static/queryImage')
        os.mkdir('website/static/resultImage')
        return redirect(url_for('views.index'))