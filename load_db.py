# This file is not used at the moment
from mariadbconn import MariaDBConn
from tqdm import tqdm
import traceback
import datetime
import glob
import pandas as pd
from pathlib import Path
import tempfile
import os

from DafneDash.filedumps import read_xls

# This file is in case we want to load xls files into a MariaDB
# But it is not used at the moment as we load xls files directly into memory

DATA_PATH = '../DataExports/'
TMPLT_FILE = './load_db_tmpl.sql'
DB = 'cont_mngm'

def main(user):
    # Connect to MariaDB
    db = None 
    tmp_file = None   
    
    try:
        data = read_xls(DATA_PATH)
        
        with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as tmp_file:
            print(tmp_file.name)
            with open(TMPLT_FILE, 'r') as sql_tmpl:
                for line in sql_tmpl:
                    key = line.strip()
                    if not key in list(data.keys()):
                        tmp_file.writelines(line)
                    else:
                        data[key]['used'] = True
                        insert_data = data[key]['data'].to_numpy()
                        last_row = len(insert_data) - 1
                        for i,row in enumerate(insert_data):
                            if i == last_row:
                                frmt_row = "(\"" + "\",\"".join(row) + "\");\n"
                                # breakpoint()
                            else:
                                frmt_row = "(\"" + "\",\"".join(row) + "\"),\n"
                            tmp_file.writelines(frmt_row)
        
        # breakpoint()

        db = MariaDBConn(user=user, database=DB)

        db.load_data(tmp_file.name)
        # breakpoint()
        # db.connect(password=password)

        # breakpoint()
            

    except Exception as e:
        print(f"{''.join(traceback.format_exception(e))}")
        
    finally:
        if db != None:
            db.close_conn()
        if tmp_file != None:
            os.unlink(tmp_file.name)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-u', '--user',
        dest='user',
        action='store',
        required=True,
        help='specifies the username to connect with',
    )

    parser.add_argument(
        '-l','--level',
        dest='level',
        action='store',
        default=1,
        type = int,
        required=False,
        help='specifies the level of output',
    )


    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print(f'Unknown options {unknown}')
        parser.print_help()
        exit(-1)

    main(user=args.user)
