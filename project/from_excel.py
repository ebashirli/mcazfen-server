import pandas as pd
from datetime import datetime
now = datetime.now()



def migr():
  table_lists = {
    'lossh': {
      'function': lossh_dict,
      'list': None,
    },
    'asbuilt': {
      'function': asbuilt_dict,
      'list': None,
    },
    'transmittal': {
      'function': transmittal_dict,
      'list': None,
    },

  }
  table_names = list(table_lists.keys())
  for table_name in table_names:
    df = pd.read_excel(f'{table_name}.xlsx')
    list_data = []
    for i in range(df.shape[0]):
      data = table_lists[table_name]['function'](df, i)
      list_data.append(data)
    table_lists[table_name]['list'] = list_data
  return table_lists

def lossh_dict(dataframe, item):
  return dict(
    SubsystemID = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Subsystem']}",
    PackageID = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Package']}",
    Drawing = dataframe.iloc[item]['Drawing'],
    Revision = dataframe.iloc[item]['Revision'],
    MCRevision =  None if pd.isna(dataframe.iloc[item]['MCRevision']) else dataframe.iloc[item]['MCRevision'],
    CreatedBy = dataframe.iloc[item]['CreatedBy'],
    CreatingDateTime = str(dataframe.iloc[item]['CreatingDateTime'])
  )
def asbuilt_dict(dataframe, item):
  return dict(
    SubsystemID = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Subsystem']}",
    PackageID = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Package']}",
    Drawing = dataframe.iloc[item]['Drawing'],
    Revision = dataframe.iloc[item]['Revision'],
    MCRevision =  None if pd.isna(dataframe.iloc[item]['MCRevision']) else dataframe.iloc[item]['MCRevision'],
    StatusOfChange = dataframe.iloc[item]['StatusOfChange'] == 'Yes',
    DateOfChange = str(dataframe.iloc[item]['DateOfChange']),
    CreatedBy = dataframe.iloc[item]['CreatedBy'],
    CreatingDateTime = str(dataframe.iloc[item]['CreatingDateTime']),
    TransmittalNumbers =  None if pd.isna(dataframe.iloc[item]['TransmittalNumbers']) else dataframe.iloc[item]['TransmittalNumbers'],
    MOCNumber = None if pd.isna(dataframe.iloc[item]['MOCNumber']) else dataframe.iloc[item]['MOCNumber'],
    ReceivedFrom = None if pd.isna(dataframe.iloc[item]['ReceivedFrom']) else dataframe.iloc[item]['ReceivedFrom']
  )
def transmittal_dict(dataframe, item):
  asbuilt_df = pd.read_excel(f'asbuilt.xlsx')
  l = asbuilt_df.loc[asbuilt_df['TransmittalNumbers'].str.contains(f";{dataframe.iloc[item]['Number']};", na=False), "ID"].to_list()
  asbuiltIds = ';' if len(l)==0 else f";{';'.join(str(v) for v in l)};"
  return dict(
    Number = int(dataframe.iloc[item]['Number']),
    AsbuiltIds = asbuiltIds,
    CreatedBy = dataframe.iloc[item]['CreatedBy'],
    CreatingDateTime = str(dataframe.iloc[item]['CreatingDateTime']),
  )


# from werkzeug.security import generate_password_hash
    # 'subsystems': {
    #   'function': subsystem_dict,
    #   'list': None,
    # },
    # 'packages': {
    #   'function': package_dict,
    #   'list': None,
    # },
    # 'users': {
    #   'function': users_dict,
    #   'list': None,
    # },

# def subsystem_dict(dataframe, item):
#   return dict(
#     id = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Subsystem']}",
#     project = dataframe.iloc[item]['Project'],
#     subsystem = dataframe.iloc[item]['Subsystem'],
#   )
# def package_dict(dataframe, item):
#   return dict(
#     id = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Package']}",
#     project = dataframe.iloc[item]['Project'],
#     subsystemId = f"{dataframe.iloc[item]['Project']}|{dataframe.iloc[item]['Subsystem']}",
#     package = dataframe.iloc[item]['Package']
#   )
# def users_dict(dataframe, item):
#   return dict(
#     name = dataframe.iloc[item]['name'],
#     surname = dataframe.iloc[item]['surname'],
#     password = generate_password_hash(dataframe.iloc[item]['password'], method='sha256'),
#     position = dataframe.iloc[item]['position'],
#     email = dataframe.iloc[item]['email'],
#     createdBy = 'Admin',
#     creatingDateTime = str(now)
#   )