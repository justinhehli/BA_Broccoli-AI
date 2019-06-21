# Update der Datensätze in der Tabelle dbo.broccolivalues -> Erweiterung mit Erntedaten
import pyodbc
import pandas as pd
from shapely.geometry import Point

# CSV einlesen und Datensätze filtern, die in DB geschrieben werden sollen
filename = ''
cropValues = pd.read_csv(filename, delimiter=';')

# Azure-DB Verbindungsaufbau
server = 'deepbroccoliserver.database.windows.net'
database = 'DeepBroccoliDatabase'
username = 'ntb'
password = 'brokkoli_2019'
driver= '{SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

# Abfrage der Brokkoli-Daten aus dbo.broccoli
query = 'SELECT * FROM dbo.broccoli'
SQL_Query = pd.read_sql_query(query, conn)
broccoli_data = pd.DataFrame(SQL_Query)
broccoli_data['coord'] = Point(broccoli_data.lat, broccoli_data.long)

 # UPDATE
cursor = conn.cursor()
for index, row in cropValues.iterrows():    
    cursor.execute('''UPDATE dbo.broccoli
                        SET cropNoMeasure = ,
                            cropOverripe = ,
                            cropRudimentary = ,
                            cropRotten = ,
                            cropUnripe = ,
                            cropUnripe = ,
                            cropWeight = , 
                            cropNotice = ,
                        WHERE dbo.broccoli.id = ''' + str(row['id']) + ''';''')

conn.commit()

SQL_Query = pd.read_sql_query(''' select * from dbo.broccoliBlacklist''', conn)
sqlBlacklist = pd.DataFrame(SQL_Query)
sqlBlacklist