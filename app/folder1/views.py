import os

from OstrakovO_DBS_py39 import settings
from django.http import JsonResponse
from django.http import HttpResponse
import psycopg2

def homepage(request): return HttpResponse("This is a home page")

def health(request):

    conn = psycopg2.connect(
        database=os.environ.get('DBS_NAME'),
        user=os.environ.get('DBS_USERNAME'),
        host=os.environ.get('DBS_HOST'),
        password=os.environ.get('DBS_PASSWORD'),
        port=os.environ.get('DBS_PORT'),
    )
    """"
    conn = psycopg2.connect(
        database=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        host=settings.DATABASES['default']['HOST'],
        password=settings.DATABASES['default']['PASSWORD'],
        port=settings.DATABASES['default']['PORT'],
    )
    """

    cursor = conn.cursor()

    cursor.execute("SELECT VERSION();")

    result = cursor.fetchall()

    version = result[0][0]

    cursor.execute("SELECT pg_database_size('dota2') / 1024 / 1024 as dota2_db_size;")
    result = cursor.fetchall()

    db_size = result[0][0]

    dictionary = {"pgsql": {"version": str(version), "dota2_db_size": str(db_size)}}

    cursor.close()
    conn.close()

    return JsonResponse(dictionary)