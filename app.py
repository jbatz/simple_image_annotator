import argparse
from os import walk
import csv

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def grader():
    if app.config["HEAD"] == len(app.config["MASK_FILES"]):
        return redirect(url_for('bye'))
    mask = app.config["MASK_FILES"][app.config["HEAD"]]
    not_end = not (app.config["HEAD"] == len(app.config["MASK_FILES"]) - 1)
    return render_template('grader.html', not_end=not_end, filename=mask,
                           head=app.config["HEAD"] + 1, len=len(app.config["MASK_FILES"]))


@app.route('/next')
def save_grade():
    label = request.args.get('label')
    print('label: {}'.format(label))

    mask = app.config["MASK_FILES"][app.config["HEAD"]]
    mask_id = mask.split('.')[0]
    print('id: {} label: {}'.format(mask_id, label))
    app.config["HEAD"] = app.config["HEAD"] + 1
    with open(app.config["CSV"], 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow([mask_id, label])
    return redirect(url_for('grader'))


@app.route("/bye")
def bye():
    return send_file("taf.gif", mimetype='image/gif')


@app.route('/mask/<f>')
def masks(f):
    mask_dir = app.config['MASK_DIR']
    return send_file(mask_dir + f)


@app.route('/image/<f>')
def images(f):
    image_dir = app.config['IMAGE_DIR']
    return send_file(image_dir + f)


def init_csv():
    with open(app.config["CSV"], 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['id', 'label'])


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--image_dir', dest='image_dir', required=True)
    arg_parser.add_argument('--mask_dir', dest='mask_dir', required=True)
    arg_parser.add_argument("--csv", dest='csv', required=True)
    args = arg_parser.parse_args()

    app.config["IMAGE_DIR"] = args.image_dir
    app.config["MASK_DIR"] = args.mask_dir
    app.config["CSV"] = args.csv
    app.config["LABELS"] = ['good', 'bad']

    mask_files = []
    for (dirpath, dirnames, filenames) in walk(args.mask_dir):
        mask_files.extend(filenames)
        break

    init_csv()

    app.config["MASK_FILES"] = mask_files
    app.config["HEAD"] = 0
    app.run(debug="True")


if __name__ == "__main__":
    main()
