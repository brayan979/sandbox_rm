from datetime import datetime, timedelta,timezone
from airflow.providers.standard.operators.empty import EmptyOperator

from airflow.sdk import DAG, BaseOperator


class TimeDiff(BaseOperator):
    
    def __init__(self, diff_date, **kwargs):
        super().__init__(**kwargs)
        self.diff_date = diff_date

    def execute(self, context):
        diff_date = self.diff_date.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - diff_date
        self.log.info("Fecha actual: %s | diff_date: %s | Diferencia: %s", now, diff_date, diff)
        return str(diff)



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(1900, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

N = 5

with DAG(
    dag_id="test",
    default_args=default_args,
    schedule="0 3 * * *", 
    catchup=False,  
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")
    odd_tasks = []
    even_tasks = []

    for n in range(1, N + 1):
        task = EmptyOperator(task_id=f"task_{n}")
        if n % 2 != 0:
            odd_tasks.append(task)
        else:
            even_tasks.append(task)

    for odd in odd_tasks:
        start >> odd

    for odd in odd_tasks:
        for even in even_tasks:
            odd >> even

    for even in even_tasks:
        even >> end

    time_diff = TimeDiff(task_id="time_diff", diff_date=datetime(2024, 1, 1))
    start >> time_diff >> end

# ¿Qué es un Hook? ¿En qué se diferencia de una conexión?

# - Una conexión  solo guarda los datos para acceder a un sistema
#   externo: host, puerto, usuario, contraseña, esquema y extras. 
#
# - Un Hook es una clase de Python que usa esa conexión para
#   abrir el cliente o la sesión con el sistema externo y ofrece métodos de alto
#   nivel para trabajar.

# La diferencia, es que la conexión dice dónde y con qué credenciales conectarse, mientras que el hook define cómo conectarse y qué operaciones realizar.