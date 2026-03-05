import os
import pyodbc 
from sqlalchemy import create_engine 
from sqlalchemy import exc
import pandas as pd
import re
from dotenv import load_dotenv
import logging


class Check():

    @staticmethod
    def drivers_odbc():
        driversODBC = [driver for driver in pyodbc.drivers() if 'ODBC Driver' in driver and re.search(r'\d+', driver) and 'SQL Server' in driver]
        driver = max(driversODBC, key=lambda d: int(re.search(r'\d+', d).group()), default=None)
        if not driver:
            raise RuntimeError('Driver ODBC não encontrado.')
        return driver
    
    @staticmethod
    def env():
        load_dotenv()
        envar = {
            'DB_SERVER' : None,
            'DB_NAME' : None,
            'DB_USER' : None,
            'DB_PASS': None,
            'QUERY_PATH' : None
        }
        for key in envar.keys():            
            if os.getenv(key) is None:
                raise EnvironmentError(f'Env Var {key} is None')
            else:
                envar[key] = os.getenv(key)
        if not os.path.isfile(envar['QUERY_PATH']):
            raise FileNotFoundError(f"Query path em .env {envar['QUERY_PATH']} não encontrada.")
        return envar

class Data():

    @staticmethod
    def get():
        driver = Check.drivers_odbc()
        envar = Check.env()
        query_path = envar['QUERY_PATH']
        try:
            with open(query_path, 'r', encoding='cp1252') as f:
                query = f.read()
        except Exception as e:
            raise RuntimeError(f'Falha ao ler a query {query_path} - {repr(e)}') from e
        try:
            def create_conn():
                conn = pyodbc.connect(
                    f"DRIVER={{{driver}}};"
                    f"SERVER={envar['DB_SERVER']};"
                    f"DATABASE={envar['DB_NAME']};"
                    f"UID={envar['DB_USER']};"
                    f"PWD={envar['DB_PASS']};"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"
                    "Connection Timeout=30;"
                )
                conn.timeout = 300
                return conn

            engine = create_engine("mssql+pyodbc://", creator=create_conn)
            df = pd.read_sql_query(query, engine)
            return df
        except exc.OperationalError as e:
            raise ConnectionError(f'Falha na conexão com o banco: {e.orig.args[1]}') from None
        except exc.ProgrammingError as e:
            raise ValueError(f'Falha ao rodar a query: {e.orig.args[1]}') from None
        except exc.DataError as e:
            raise ValueError(f'Problema nos dados retornados: {e.orig.args[1]}') from None
        except exc.DatabaseError as e:
            raise RuntimeError(f'Falha inesperada no banco: {e.orig.args[1]}') from None
    
    @staticmethod
    def to_json(df):
        json_path = 'data.json'
        df.to_json(
            json_path,
            orient='records',
            force_ascii=False,
            indent=4
        )



if __name__ == '__main__':

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('get_data.log'),
            logging.StreamHandler()
        ]
    )

    try:
        logging.info('Iniciando Coleta do SQL.')
        df = Data.get()
        logging.info('Transformando em JSON.')
        Data.to_json(df)
        logging.info('Conversão finalizada.')
    except (RuntimeError, FileNotFoundError, EnvironmentError, ValueError, ConnectionError) as e:
        logging.exception(f'Erro: {e}.')
    except Exception as e:
        logging.exception(f'Erro inesperado: {e}.')
    

