""" Routes of Flask Web Application """
import os
import csv
import threading
import shelve
from pathlib import Path
from flask import render_template, request, jsonify
from lie_to_me import app, video, basedir
from lie_to_me.process import process_video, process_audio


@app.route('/', methods=['GET', 'POST'])
def upload():
    """ Home Page Route
        Upload and Analyze Video
    :return: home.html template
    """
    if request.method == 'POST' and 'file' in request.files:
        # Video has been uploaded
        filename = video.save(request.files['file'])

        # Process video on a new thread
        threading.Thread(target=process_video, args=[os.path.join('uploads', filename)]).start()
        threading.Thread(target=process_audio, args=[os.path.join('uploads', filename)]).start()

        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    elif request.method == 'GET':
        return render_template('home.html')


@app.route('/analysis', methods=['GET'])
def analysis():
    """ Analysis Route
        View Final Analysis of Uploaded Video
    :return:
    """
    json_path = os.path.join(basedir, 'static', 'data', 'tmp_json')

    audio_file = Path(os.path.join(json_path, 'audio_data.shlf'))
    video_file = Path(os.path.join(json_path, 'facial_data.shlf'))
    # csv_path = os.path.join(basedir, 'static', 'data', 'csv')
    # txt_file = Path(os.path.join(basedir, 'static', 'data', 'first_soc.txt'))

    # if not os.path.exists(csv_path):
    #     os.mkdir(csv_path)

    # Files exists
    if audio_file.is_file() and video_file.is_file():
        with shelve.open(os.path.join(json_path, 'facial_data.shlf')) as shelf:
            emotion_data = shelf['emotion_data']
            microexpression_data = shelf['micro_expression_data']
            blink_data = shelf['blink_data']

        with shelve.open(os.path.join(json_path, 'audio_data.shlf')) as shelf:
            mean_energy = shelf['mean_energy']
            max_pitch_amp = shelf['max_pitch_amp']
            vowel_duration = shelf['vowel_duration']
            pitch_contour = shelf['pitch_contour']

    else:
        emotion_data = None
        microexpression_data = None
        blink_data = None
        mean_energy = None
        max_pitch_amp = None
        vowel_duration = None
        pitch_contour = None

    # traindata = []
    #
    # for i in range(len(blink_data)):
    #     traindata.append(0)
    # trainfile = open(txt_file)
    # for line in trainfile:
    #     index1 = int((int(line[4]) * 600) + ((int(line[5]) * 60) + (int(line[7]) * 10) + int(line[8])) / 2)
    #     index2 = int((int(line[10]) * 600) + ((int(line[11]) * 60) + (int(line[13]) * 10) + int(line[14])) / 2)
    #     if line[0] == 'F':
    #         traindata[index1] = 1
    #         traindata[index2] = 1

    # All output values should be available here:

    # with open(Path(os.path.join(csv_path, 'train.csv')), 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(['Time Interval', 'Emotion Data', 'Micro-expressions', 'Blinks',
    #                      'Mean Energy', 'Max Pitch Amplitude', 'Vowel Duration', 'Fundamental Frequency',
    #                      'False/True'])
    #     for index in range(len(mean_energy)):
    #         writer.writerow([index, emotion_data[index], microexpression_data[index], blink_data[index],
    #                          mean_energy[index], max_pitch_amp[index], vowel_duration[index], pitch_contour[index],
    #                          traindata[index]])

    return render_template('analysis.html', mean_energy=mean_energy, max_pitch_amp=max_pitch_amp,
                           vowel_duration=vowel_duration, pitch_contour=pitch_contour, blink_data=blink_data,
                           microexpression_data=microexpression_data, emotion_data=emotion_data)


@app.route('/results', methods=['GET'])
def results():
    """ Results Route
        View Final Lie Detection results of Uploaded Video
    :return:
    """
    return render_template('results.html')
