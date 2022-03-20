import os
from enum import unique

import psycopg2
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone

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

def patches (request):

    conn = psycopg2.connect(
        database=os.environ.get('DBS_NAME'),
        user=os.environ.get('DBS_USERNAME'),
        host=os.environ.get('DBS_HOST'),
        password=os.environ.get('DBS_PASSWORD'),
        port=os.environ.get('DBS_PORT'),
    )

    cursor = conn.cursor()

    cursor.execute("SELECT p.patch_version, p.patch_start_date, p.patch_end_date, m.id AS match_id, m.duration AS match_duration FROM (SELECT p.name AS patch_version, cast (extract (epoch from p.release_date) as integer) AS patch_start_date, cast (extract (epoch from LEAD (p.release_date) over (order by id)) as integer) AS patch_end_date FROM patches p) p INNER JOIN matches m ON m.start_time BETWEEN p.patch_start_date AND p.patch_end_date OR TRUE IS NULL;")
    result = cursor.fetchall()

    patches = []
    for x in result:
            patches.append(x[0:3])

    versions = []
    uniq_patches = []
    for item in patches:
        if item[0] not in versions:
            versions.append(item[0])
            uniq_patches.append(item)
        else:
            pass
    patches_dict = []
    for item in uniq_patches:
        patch_matches = []
        for match in result:
            if match[0] == item[0]:
                tmp = {"match_id": match[3], "duration": round(match[4] / 60, 2)}
                patch_matches.append(tmp)
        dict = {"patch_version": item[0], "patch_start_date": item[1], "patch_end_date": item[2],
                "matches": patch_matches}
        patches_dict.append(dict)

    dictionary = {"patches":patches_dict}
    cursor.close()
    conn.close()

    return JsonResponse(dictionary)

