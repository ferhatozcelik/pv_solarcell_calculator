from flask import Flask, render_template, request, session, flash
import pandas as pd
import os
import calculate

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'txt'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'This is your secret key to utilize session in Flask'


@app.route('/', methods=("POST", "GET"))
def index():
    data = []
    light_source = 1000
    delimiter = ';'
    if request.method == 'POST':
        uploaded_file = request.files.get('filename')
        light_source = request.form['light_source']
        delimiter = request.form['delimiter']
        try:
            uploaded_df_value = pd.read_csv(uploaded_file, header=None, delimiter=delimiter).values
            data = [list(uploaded_df_value[:, 0]), list(uploaded_df_value[:, 1])]

            cal_value = calculate.calculate(uploaded_df_value, float(light_source))

            picker_data = cal_value[7]
            four_area_data = [list(picker_data[:, 0]), list(picker_data[:, 1])]

            return render_template('index.html', data=data, picker_data=four_area_data, delimiter=delimiter, light_source=light_source,
                                   Rs=float(cal_value[0]),
                                   Rsh=float(cal_value[1]), Voc=float(cal_value[2]),
                                   Jsc=float(cal_value[3]), FF=float(cal_value[4]), PCE=float(cal_value[5]), image_data=cal_value[6])
        except Exception as e:
            flash("Error: " + str(e))

    return render_template('index.html', data=None, delimiter=delimiter, light_source=light_source,
                                   Rs=None, Rsh=None, Voc=None, Jsc=None, FF=None, PCE=None, image_data=None)


if __name__ == '__main__':
    app.run(debug=True)
