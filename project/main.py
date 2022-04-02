from operator import and_, attrgetter
from flask import Blueprint, render_template, jsonify, request, session
from flask_login import login_required, current_user
from project.from_excel import migr
import sqlite3 as sq
import pandas as pd

from project.models import Asbuilt, Lossh, Package, Subsystem, Transmittal
from . import db

main = Blueprint('main', __name__)


models = {
    'lossh': Lossh,
    'asbuilt': Asbuilt,
    'transmittal': Transmittal,
    'subsystem': Subsystem,
    'package': Package
}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/home')
def home():
    return f'Mecanical Complition Activities Home Page'

@main.route('/<division>/<keyword>', methods=['GET', 'OPTIONS'])
def get_from_source(division, keyword):
    is_drawing = request.args.get("isDrawing") == '1'
    process_name = "lossh" if request.args.get("processName") == '0' else 'asbuilt'

    model = models[division]
    if division == 'subsystem':
        model = models['package']
    all_divs = model.query.filter(model.id.like(f'%{keyword}%')).all()
    if is_drawing:
        all_processes = models[process_name].query.filter(models[process_name].Drawing==keyword).all()
        process_ids = [p.SubsystemID if division == 'subsystem' else p.PackageID for p in all_processes]
        all_divs = model.query.filter(model.id.in_(process_ids)).all()
    ls = [div.to_dict() for div in all_divs]

    if division == 'subsystem':
        from itertools import groupby
        def key_f(k):
            return k['SubsystemID']
        ls = sorted(ls, key=key_f)
        ls = [list(v)[0] for _, v in groupby(ls, key_f)]
    return response_function(ls)

@main.route('/<process>/<division>/<division_id>', methods=['GET'])
def get_from_output(process, division, division_id):
    args = request.args
    is_transmittal = args.get("isTransmittal")=='true'
    if division == 'package':
        processes = models[process].query.filter(and_(
            models[process].PackageID==division_id,
            models[process].DeletingDateTime==None,
        ))
        if not is_transmittal:
            processes = processes.all()
        else:
            processes = processes.filter(models[process].StatusOfChange==1).all()
        processes = sorted(processes, key=attrgetter('CreatingDateTime'), reverse=True)
        processes = list(map(lambda x: x.to_dict(), processes))
        if process == 'asbuilt':
            received_from_list = list(filter(lambda x: x, [list(name)[0] for name in db.session.query(models[process].ReceivedFrom).distinct().all()]))
            received_from_list.sort()
            processes = {
                'processes': processes,
                'received_from_list': received_from_list
            }
    if division == 'subsystem':
        processes = models[process].query.filter(
            models[process].SubsystemID==division_id,
            models[process].DeletingDateTime==None,
        ).all()
        processes = sorted(processes, key=attrgetter('CreatingDateTime'))
        processes = group_by_drawing(processes, process == 'asbuilt')
        processes = sorted(processes, key=lambda i: i['CreatingDateTime'], reverse=True)
    return response_function(processes)

@main.route('/update/<process_name>', methods=['POST'])
def update_table_row(process_name):
    request_form = request.form.to_dict()
    isSubsystem = request.args.get("isSubsystem")=='true'
    if not isSubsystem:
        id = request_form['id']
        del request_form['id']
        if id == 'transmittal':
            tr_number = int(request_form['TransmittalNumbers'])
            asbuiltIds = request_form['AsbuiltIds'].split(';')[1:-1]
            add_transmittal_number_to_asbuilt(asbuiltIds, tr_number)
        else:
            process_row = models[process_name].query.filter_by(id=id).first()
            for key, value in list(request_form.items()):
                if key == 'StatusOfChange':
                    value = 1 if value == 'true' else 0
                setattr(process_row, key, value)
    else:
        subsystemID = request_form['id']
        drawing = request_form['Drawing']
        mCRevision = request_form['MCRevision']
        models[process_name].query.filter(
            and_(
                models[process_name].SubsystemID == subsystemID,
                models[process_name].Drawing == drawing
            )).update({models[process_name].MCRevision: mCRevision}, synchronize_session=False)
    db.session.commit()
    return response_function({'message': 'your request has been done'})

@main.route('/<process_name>', methods=['POST'])
def insert_process(process_name):
    request_form = request.form.to_dict()
    process = models[process_name].from_dict(request_form)
    db.session.add(process)
    db.session.flush()
    db.session.refresh(process)
    process_id = process.id
    if process_name == 'transmittal':
        process_id = process.Number
        asbuilt_ids = request_form['AsbuiltIds'].split(';')[1:-1]
        for asbuilt_id in asbuilt_ids:
            asbuilt = Asbuilt.query.filter_by(id=int(asbuilt_id)).first()
            asbuilt.TransmittalNumbers = f"{asbuilt.TransmittalNumbers}{process_id};"
    db.session.commit()
    return response_function(process_id)

@main.route('/transmittal/last-number', methods=['GET'])
def get_last_transmittal_number():
    last_number = models['transmittal'].query.order_by(models['transmittal'].id.desc()).first().Number
    return response_function(str(last_number))

@main.route('/transmittal', methods=['GET'])
def get_transmittal_by_query():
    number = request.args.get('number')
    return response_function(models['transmittal'].query.filter_by(Number=int(number))[0].to_dict())

@main.route('/migrate', methods=['GET', 'POST'])
def migrate():
    if request.method == 'GET':
        return render_template('migrate.html')
    else:
        isPackage = request.args.get('package')
        if isPackage:
            try:
                database = r'project\db.sqlite'
                df = pd.read_excel(request.files.get('file'))
                df.dropna(subset = ["Package"], inplace=True)
                df['id'] = df['Project'] + '|' + df['Package']
                df['subsystemId'] = df['Project'] + '|' + df['Subsystem']
                df = df.rename(columns={'Project': 'project', 'Package': 'package'})
                df = df[['id', 'project', 'subsystemId', 'package']]

                conn = sq.connect(database)
                cur = conn.cursor()
                cur.execute('''DROP TABLE IF EXISTS package''')
                df.to_sql('package', conn, if_exists='replace', index=False)
                conn.commit()
                conn.close()
                response = 'Done'
            except Exception as ex:
                response = f'Error: Uploaded file has no {ex.args[0]} column!'
            return response_function(response)
                
        tables = migr()
        for table_name in list(tables.keys()):
            db.session.bulk_insert_mappings(models[table_name], tables[table_name]['list'])
        # db.session.bulk_insert_mappings(ms[5], lds[0])
        db.session.commit()
        return "Migration Done"

def response_function(res):
    res = jsonify(res)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

def add_transmittal_number_to_asbuilt(asbuiltIds, transmittalNumber):
    transmittal = Transmittal.query.filter_by(Number=transmittalNumber).first()
    for asbuilt_id in asbuiltIds:
        transmittal.AsbuiltIds = transmittal.AsbuiltIds.replace(f";{asbuilt_id};", ";") if f';{asbuilt_id};' in transmittal.AsbuiltIds  else f"{transmittal.AsbuiltIds}{asbuilt_id};"
        asbuilt = Asbuilt.query.filter_by(id=int(asbuilt_id)).first()
        asbuilt.TransmittalNumbers = asbuilt.TransmittalNumbers.replace(f";{transmittalNumber};", ";") if f';{transmittalNumber};' in asbuilt.TransmittalNumbers else f"{asbuilt.TransmittalNumbers}{transmittalNumber};"

def group_by_drawing(processes, isAsbuilt=False):
    subsystem_processes = []
    statusOfChange = None
    dateOfChange = None
    for drawingNo in set([p.Drawing for p in processes]):
        processes_grouped_by_drawing = [r for r in processes if r.Drawing == drawingNo]
        
        if processes_grouped_by_drawing[0].MCRevision is None:
            revisionNo = max([r.Revision for r in processes_grouped_by_drawing])
        else:
            revisionNo = processes_grouped_by_drawing[0].MCRevision
        
        subsystemID = processes_grouped_by_drawing[0].SubsystemID
        packageID = processes_grouped_by_drawing[0].PackageID

        
        if isAsbuilt:
            if processes_grouped_by_drawing[0].MCRevision is None:
                statusOfChange = True if processes_grouped_by_drawing[-1].StatusOfChange == 1 else False
            else:
                statusOfChange = False    
            dateOfChange = processes_grouped_by_drawing[-1].DateOfChange
            subsystem_processes.append(
                {
                    'Drawing': drawingNo,
                    'MCRevision': revisionNo,
                    'StatusOfChange': statusOfChange,
                    'CreatingDateTime': dateOfChange,
                    'id': 1,
                    'SubsystemID': subsystemID,
                    'PackageID': packageID,
                    'Revision': '',
                    'TransmittalNumbers': [],
                    'DateOfChange': '',
                    'CreatedBy': '',
                    'DeletedBy': '',
                    'DeletingDateTime': '',
                    'UpdatedBy': '',
                    'UpdatingDateTime': '',
                }
            )
        else:
            subsystem_processes.append(
                {
                    'Drawing': drawingNo,
                    'MCRevision': revisionNo,
                    'CreatingDateTime': max([r.CreatingDateTime for r in processes_grouped_by_drawing]),
                    'id': 1,
                    'SubsystemID': subsystemID,
                    'PackageID': packageID,
                    'Revision': '',
                    'TransmittalNumbers': [],
                    'DateOfChange': '',
                    'CreatedBy': '',
                    'DeletedBy': '',
                    'DeletingDateTime': '',
                    'UpdatedBy': '',
                    'UpdatingDateTime': '',
                }
            )
    return subsystem_processes