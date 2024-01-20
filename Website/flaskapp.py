from flask import Flask, render_template, Response, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
import cv2

from YOLO_Video import video_detection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kd'
app.config['UPLOAD_FOLDER'] = 'static/files'


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Run")


def reduce_frame_rate(video_path, output_path, target_fps):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Wybierz odpowiedni kodek
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

    frame_counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_counter % int(fps / target_fps) == 0:
            out.write(frame)

        frame_counter += 1

    cap.release()
    out.release()


def generate_frames(path_x=''):
    reduced_video_path = 'reduced_video.mp4'
    target_fps = 15
    reduce_frame_rate(path_x, reduced_video_path, target_fps)

    yolo_output = video_detection(reduced_video_path)

    for detection_ in yolo_output:
        ref, buffer = cv2.imencode('.jpg', detection_)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    session.clear()
    return redirect(url_for('front'))


@app.route('/front', methods=['GET', 'POST'])
def front():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))

    return render_template('videoprojectnew.html', form=form)


@app.route('/video')
def video():
    return Response(generate_frames(path_x=session.get('video_path', None)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
