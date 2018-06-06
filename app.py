import argparse
from os import walk

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/grader')
def grader():
    if app.config["HEAD"] == len(app.config["MASK_FILES"]):
        return redirect(url_for('bye'))
    directory = app.config['MASK_DIR']
    mask = app.config["MASK_FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    not_end = not (app.config["HEAD"] == len(app.config["MASK_FILES"]) - 1)
    return render_template('grader.html', not_end=not_end, directory=directory, mask=mask, labels=labels,
                           head=app.config["HEAD"] + 1, len=len(app.config["MASK_FILES"]))


@app.route('/next')
def save_grade():
    label = request.args.get('label')
    print('label: {}'.format(label))

    mask = app.config["MASK_FILES"][app.config["HEAD"]]
    mask_id = mask.split('.')[0]
    print('id: {} label: {}'.format(mask_id, label))
    app.config["HEAD"] = app.config["HEAD"] + 1
    with open(app.config["CSV"], 'a') as f:
        pass
        # for label in app.config["LABELS"]:
        #     f.write(image + "," +
        #             label["id"] + "," +
        #             label["name"] + "," +
        #             str(round(float(label["xMin"]))) + "," +
        #             str(round(float(label["xMax"]))) + "," +
        #             str(round(float(label["yMin"]))) + "," +
        #             str(round(float(label["yMax"]))) + "\n")
    app.config["LABELS"] = []
    return redirect(url_for('grader'))


@app.route("/bye")
def bye():
    return send_file("taf.gif", mimetype='image/gif')


@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id": id, "name": "", "xMin": xMin, "xMax": xMax, "yMin": yMin, "yMax": yMax})
    return redirect(url_for('grader'))


@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('grader'))


@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('grader'))


# @app.route('/prev')
# def prev():
#     app.config["HEAD"] = app.config["HEAD"] - 1
#     return redirect(url_for('grader'))

@app.route('/mask/<f>')
def masks(f):
    mask_dir = app.config['MASK_DIR']
    return send_file(mask_dir + f)


@app.route('/image/<f>')
def images(f):
    image_dir = app.config['IMAGE_DIR']
    return send_file(image_dir + f)


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

    app.config["MASK_FILES"] = mask_files
    app.config["HEAD"] = 0
    app.run(debug="True")


if __name__ == "__main__":
    main()
