from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    surname = db.Column(db.String(1000))
    password = db.Column(db.String(1000))
    position = db.Column(db.String(1000))
    email = db.Column(db.String(1000), unique=True)
    createdBy = db.Column(db.String(1000))
    creatingDateTime = db.Column(db.String(1000))
    deletedBy = db.Column(db.String(1000))
    deletingDateTime = db.Column(db.String(1000))
    updatedBy = db.Column(db.String(1000))
    updatingDateTime = db.Column(db.String(1000))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'password': self.password,
            'position': self.position,
            'email': self.email,
            'createdBy': self.createdBy,
            'creatingDateTime': self.creatingDateTime,
            'deletedBy': self.deletedBy,
            'deletingDateTime': self.deletingDateTime,
            'updatedBy': self.updatedBy,
            'updatingDateTime': self.updatingDateTime
        }

    def to_str(self):
        return f"'name': {self.name}, 'surname': {self.surname}, 'position': {self.position}"

    def from_dict(dic):
        return User(
            name = dic['name'],
            surname = dic['surname'],
            password = dic['password'],
            position = dic['position'],
            email = dic['email'],
            createdBy = dic['createdBy'],
            creatingDateTime = dic['creatingDateTime'],
            DeletedBy = dic['DeletedBy'] if "DeletedBy" in dic else None,
            DeletingDateTime = dic['DeletingDateTime'] if 'DeletingDateTime' in dic else None,
            UpdatedBy = dic['UpdatedBy'] if 'UpdatedBy' in dic else None,
            UpdatingDateTime = dic['UpdatingDateTime'] if 'UpdatingDateTime' in dic else None
        )

class Lossh(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    SubsystemID = db.Column(db.String(100), nullable=False)
    PackageID = db.Column(db.String(100), nullable=False)
    Drawing = db.Column(db.String(100), nullable=False)
    Revision = db.Column(db.String(100), nullable=False)
    MCRevision = db.Column(db.String(100))
    CreatedBy = db.Column(db.String(100))
    CreatingDateTime = db.Column(db.String(100))
    DeletedBy = db.Column(db.String(100))
    DeletingDateTime = db.Column(db.String(100))
    UpdatedBy = db.Column(db.String(100))
    UpdatingDateTime = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'SubsystemID': self.SubsystemID,
            'PackageID': self.PackageID,
            'Drawing': self.Drawing,
            'Revision': self.Revision,
            'MCRevision': self.MCRevision,
            'CreatedBy': self.CreatedBy.replace('.',' '),
            'CreatingDateTime': self.CreatingDateTime,
            'DeletedBy': self.DeletedBy,
            'DeletingDateTime': self.DeletingDateTime,
            'UpdatedBy': self.UpdatedBy,
            'UpdatingDateTime': self.UpdatingDateTime
        }
    def from_dict(dic):
        return Lossh(
            SubsystemID = dic['SubsystemID'],
            PackageID = dic['PackageID'],
            Drawing = dic['Drawing'],
            Revision = dic['Revision'],
            MCRevision = dic['MCRevision'] if "MCRevision" in dic else None,
            CreatedBy = dic['CreatedBy'],
            CreatingDateTime = dic['CreatingDateTime'],
            DeletedBy = dic['DeletedBy'] if "DeletedBy" in dic else None,
            DeletingDateTime = dic['DeletingDateTime'] if 'DeletingDateTime' in dic else None,
            UpdatedBy = dic['UpdatedBy'] if 'UpdatedBy' in dic else None,
            UpdatingDateTime = dic['UpdatingDateTime'] if 'UpdatingDateTime' in dic else None
        )

class Asbuilt(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    SubsystemID = db.Column(db.String(100), nullable=False)
    PackageID = db.Column(db.String(100), nullable=False)
    Drawing = db.Column(db.String(100), nullable=False)
    Revision = db.Column(db.String(100), nullable=False)
    MCRevision = db.Column(db.String(100))
    TransmittalNumbers = db.Column(db.String(1000))
    MOCNumber = db.Column(db.String(1000))
    ReceivedFrom = db.Column(db.String(1000))
    StatusOfChange = db.Column(db.Integer, nullable=False)
    DateOfChange = db.Column(db.String(100), nullable=False)
    CreatedBy = db.Column(db.String(100))
    CreatingDateTime = db.Column(db.String(100))
    DeletedBy = db.Column(db.String(100))
    DeletingDateTime = db.Column(db.String(100))
    UpdatedBy = db.Column(db.String(100))
    UpdatingDateTime = db.Column(db.String(100))

    def to_dict(self):
        transmittalNumbers = list(map(lambda x: x, self.TransmittalNumbers.split(";")[1:-1]))
        return {
            'id': self.id,
            'SubsystemID': self.SubsystemID,
            'PackageID': self.PackageID,
            'Drawing': self.Drawing,
            'Revision': self.Revision,
            'MCRevision': self.MCRevision,
            'TransmittalNumbers': transmittalNumbers,
            'MOCNumber': self.MOCNumber,
            'ReceivedFrom': self.ReceivedFrom,
            'StatusOfChange': self.StatusOfChange == 1,
            'DateOfChange': self.DateOfChange,
            'CreatedBy': self.CreatedBy.replace('.',' '),
            'CreatingDateTime': self.CreatingDateTime,
            'DeletedBy': self.DeletedBy,
            'DeletingDateTime': self.DeletingDateTime,
            'UpdatedBy': self.UpdatedBy,
            'UpdatingDateTime': self.UpdatingDateTime
        }
    def from_dict(dic):
        transmittalNumbers = ';'
        if "TransmittalNumbers" in dic:
            if len(dic['TransmittalNumbers'])>0:
                transmittalNumbers = f";{';'.join(dic['TransmittalNumbers'])};"
        else:
            transmittalNumbers = None
            
        return Asbuilt(
            SubsystemID = dic['SubsystemID'],
            PackageID = dic['PackageID'],
            Drawing = dic['Drawing'],
            Revision = dic['Revision'],
            MCRevision = dic['MCRevision'] if dic['MCRevision'] else None,
            TransmittalNumbers = transmittalNumbers,
            MOCNumber = dic['MOCNumber'] if dic['MOCNumber'] else None,
            ReceivedFrom = dic['ReceivedFrom'] if dic['ReceivedFrom'] else None,
            StatusOfChange = int(dic['StatusOfChange'] == 'true'),
            DateOfChange = dic['DateOfChange'],
            CreatedBy = dic['CreatedBy'],
            CreatingDateTime = dic['CreatingDateTime'],
            DeletedBy = dic['DeletedBy'] if dic['DeletedBy'] else None,
            DeletingDateTime = dic['DeletingDateTime'] if dic['DeletingDateTime'] else None,
            UpdatedBy = dic['UpdatedBy'] if dic['UpdatedBy'] else None,
            UpdatingDateTime = dic['UpdatingDateTime'] if dic['UpdatingDateTime'] else None
        )

class Transmittal(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    Number = db.Column(db.Integer, unique=True)
    AsbuiltIds = db.Column(db.String(1000))
    CreatedBy = db.Column(db.String(100))
    CreatingDateTime = db.Column(db.String(100))
    DeletedBy = db.Column(db.String(100))
    DeletingDateTime = db.Column(db.String(100))
    UpdatedBy = db.Column(db.String(100))
    UpdatingDateTime = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'Number': self.Number,
            'AsbuiltIds': self.AsbuiltIds, # asbuiltIdList,
            'CreatedBy': self.CreatedBy.replace('.',' '),
            'CreatingDateTime': self.CreatingDateTime,
            'DeletedBy': self.DeletedBy,
            'DeletingDateTime': self.DeletingDateTime,
            'UpdatedBy': self.UpdatedBy,
            'UpdatingDateTime': self.UpdatingDateTime
        }
    def from_dict(dic):
        return Transmittal(
            Number = Transmittal.query.order_by(Transmittal.id.desc()).first().Number + 1,
            AsbuiltIds = dic['AsbuiltIds'],
            CreatedBy = dic['CreatedBy'],
            CreatingDateTime = dic['CreatingDateTime'],
            DeletedBy = dic['DeletedBy'] if "DeletedBy" in dic else None,
            DeletingDateTime = dic['DeletingDateTime'] if 'DeletingDateTime' in dic else None,
            UpdatedBy = dic['UpdatedBy'] if 'UpdatedBy' in dic else None,
            UpdatingDateTime = dic['UpdatingDateTime'] if 'UpdatingDateTime' in dic else None
        )

class Package(db.Model):
    id = db.Column(db.String(100), primary_key=True, unique=True)
    project = db.Column(db.String(100), nullable=False)
    subsystemId = db.Column(db.String(100), nullable=False)
    package = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'PackageID': self.id,
            'Project': self.project,
            'SubsystemID': self.subsystemId,
            'Package': self.package,
            'Subsystem': self.subsystemId.split('|')[1]
        }
    def from_dict(dic):
        return Package(
            id = dic['PackageID'],
            project = dic['Project'],
            subsystemId = dic['SubsystemID'],
            package = dic['Package']
        )
