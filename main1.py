import psycopg2
from psycopg2 import Error
import json
import sys

if __name__ == '__main__':
    try:
        # Connect to an existing database
        connection = False
        connection = psycopg2.connect(user="postgres",
                                      password="Lubimpalacinky",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")

    except(Exception, Error) as error:
        if (connection):
            connection.close()
            print("PostgreSQL connection is closed")
        print("Error while connecting to PostgreSQL", error)
        sys.exit(1)

    cursor = connection.cursor()
    # Opening json file
    with open('configClear_v2.json') as f:
        data1 = json.load(f)

    interfaces = ["Port-channel", "TenGigabitEthernet", "GigabitEthernet"]
    data_dict = data1['frinx-uniconfig-topology:configuration']['Cisco-IOS-XE-native:native']['interface']

    # Doping frinx_table if already exists.
    cursor.execute("DROP TABLE IF EXISTS frinx_table")

    # Creating new table
    sql = '''CREATE TABLE frinx_table(  
            id SERIAL PRIMARY KEY,
            connection INT,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            config json,
            type VARCHAR(50),
            infra_type VARCHAR(50),
            port_channel_id INT,
            max_frame_size INT
        )'''
    cursor.execute(sql)
    connection.commit()

    # Inserting data into new table
    for word in interfaces:
        for conf in data_dict[word]:
            name = conf['name']
            desc = conf.get('description', 'NULL')
            max_fr = conf.get('mtu', 'NULL')
            if (word == "TenGigabitEthernet" or word == "GigabitEthernet") and conf.get(
                    'Cisco-IOS-XE-ethernet:channel-group', False):
                sql = "SELECT id FROM frinx_table WHERE name = '{}'".format(
                    conf['Cisco-IOS-XE-ethernet:channel-group']['number'])
                cursor.execute(sql)
                port_ch_id = cursor.fetchall()[0][0]
            else:
                port_ch_id = 'NULL'

            sql = '''INSERT INTO frinx_table(name, description, config, port_channel_id, max_frame_size) 
            VALUES ('{0}', '{1}', '{2}', {3}, {4})'''.format(name, desc, json.dumps(conf), port_ch_id, max_fr)
            print(sql)
            cursor.execute(sql)
            connection.commit()
            print('Record inserted')

    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")
