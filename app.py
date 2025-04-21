from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime, timedelta
import csv
import json

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if not os.path.exists('strain_data.json'):
    with open('strain_data.json', 'w') as f:
        json.dump([], f)

model_data = {
    'eps-1': ['MAS#65', 'MAS#35'],
    'eps-2': ['MAS#65'],
    'eps-3': ['TMA PPK', 'AY PPK', 'BEV PPK'],
    'ebs-1': ['ESC', 'ABS', '2W ABS', 'PBB'],
    'ebs-2': ['PBB'],
    'tas-1': ['RTAS', 'TASGen2.0'],
    'tas-2': ['TASGen2.0'],
    'avas-1': ['PSA', 'FCA', 'LUCID'],
    'fcm-1': ['FCM#30', 'FCM#50'],
    'radar-1': ['MRR', 'SRR'],
}

station_data = {
    ('eps-1', 'MAS#65'): ['Router', 'Screwing', 'ICT'],
    ('eps-1', 'MAS#35'): ['Screwing', 'ICT'],
    ('eps-2', 'MAS#65'): ['Screwing', 'ICT'],
    ('eps-3', 'TMA PPK'): ['Router', 'ICT'],
    ('eps-3', 'AY PPK'): ['ICT'],
    ('eps-3', 'BEV PPK'): ['ICT'],
    ('ebs-1', 'ESC'): ['soldering', 'ICT'],
    ('ebs-1', 'ABS'): ['Screwing'],
    ('ebs-1', '2W ABS'): ['HFT', 'Screwing'],
    ('ebs-2', 'PBB'): ['HFT', 'Screwing'],
    ('tas-1', 'RTAS'): ['ICT'],
    ('tas-2', 'TASGen2.0'): ['Press fit'],
    ('radar-1', 'MRR'): ['Press fit'],
    ('radar-1', 'SRR'): ['Press fit'],
    ('fcm-1', 'FCM#30'): ['Press fit'],
    ('fcm-1', 'FCM#50'): ['Press fit'],
    ('avas-1', 'PSA'): ['Press fit'],
    ('avas-1', 'FCA'): ['Press fit'],
    ('avas-1', 'LUCID'): ['Press fit'],
}

@app.route('/')
def home():
    return redirect(url_for('strain'))

@app.route('/strain', methods=['GET', 'POST'])
def strain():
    source = request.args.get('source')
    model = request.args.get('model')
    selected_station = request.args.get('station')
    success = False

    if request.method == 'POST':
        retention = request.form['retention']
        measured_date = request.form['measured_date']
        measured_by = request.form['measured_by']
        approved_by = request.form['approved_by']
        remarks = request.form['remarks']

        months = int(retention.split()[0])
        date_obj = datetime.strptime(measured_date, '%Y-%m-%d')
        expiry_date = (date_obj + timedelta(days=90 if months == 3 else 180)).strftime('%Y-%m-%d')

        file = request.files['document']
        filename = ''
        if file and file.filename:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        entry = {
            'source': source,
            'model': model,
            'selected_station': selected_station,
            'retention': retention,
            'measured_date': measured_date,
            'expiry_date': expiry_date,
            'measured_by': measured_by,
            'approved_by': approved_by,
            'document_filename': filename,
            'remarks': remarks
        }

        with open('strain_data.json', 'r+') as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4)

        with open('strain_data.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=entry.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(entry)

        success = True

    return render_template('strain.html',
                           source=source,
                           model=model,
                           selected_station=selected_station,
                           success=success)

@app.route('/strain/project')
def project():
    project_map = {
        'eps': 'EPS',
        'tas': 'TAS',
        'ebs': 'EBS',
        'avas': 'AVAS',
        'radar': 'RADAR',
        'fcm': 'FCM'
    }
    return render_template('project.html', project_map=project_map)

@app.route('/strain/line')
def line():
    section = request.args.get('section')
    return render_template('line.html', section=section)

@app.route('/strain/model')
def strain_model():
    source = request.args.get('source', '').lower()
    models = model_data.get(source, [])
    return render_template('model.html', source=source, models=models)

@app.route('/strain/station', methods=['GET', 'POST'])
def station():
    source = request.args.get('source')
    model = request.args.get('model')
    selected_station = request.args.get('station')
    success = False

    stations = station_data.get((source, model), [])

    if request.method == 'POST':
        measured_date = request.form['measured_date']
        retention = request.form['retention']
        measured_by = request.form['measured_by']
        approved_by = request.form['approved_by']
        remarks = request.form['remarks']

        months = int(retention.split()[0])
        expiry_date = (datetime.strptime(measured_date, '%Y-%m-%d') + timedelta(days=90 if months == 3 else 180)).strftime('%Y-%m-%d')

        file = request.files['document']
        document_filename = None
        if file and file.filename != '':
            document_filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))

        strain_entry = {
            'source': source,
            'model': model,
            'selected_station': selected_station,
            'measured_date': measured_date,
            'retention': retention,
            'expiry_date': expiry_date,
            'measured_by': measured_by,
            'approved_by': approved_by,
            'document_filename': document_filename,
            'remarks': remarks
        }

        with open('strain_data.json', 'r+') as f:
            data = json.load(f)
            data.append(strain_entry)
            f.seek(0)
            json.dump(data, f, indent=2)

        with open('strain_data.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=strain_entry.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(strain_entry)

        success = True

    return render_template(
        'station.html',
        source=source,
        model=model,
        stations=stations,
        selected_station=selected_station,
        success=success
    )

@app.route('/strain/view')
def strain_view():
    with open('strain_data.json', 'r') as f:
        data = json.load(f)

    sort_by = request.args.get('sort_by', 'expiry_date')
    order = request.args.get('order', 'desc')
    reverse = order == 'desc'

    try:
        if sort_by in ['measured_date', 'expiry_date']:
            data.sort(key=lambda x: datetime.strptime(x[sort_by], '%Y-%m-%d'), reverse=reverse)
        else:
            data.sort(key=lambda x: x.get(sort_by, '').lower(), reverse=reverse)
    except Exception as e:
        print(f"Sort error: {e}")

    return render_template(
        'view.html',
        strain_entries=data,
        current_sort=sort_by,
        current_order=order
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
