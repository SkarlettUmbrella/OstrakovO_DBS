import os
from enum import unique

import psycopg2
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Abilities

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


def patches(request):
    conn = psycopg2.connect(
        database=os.environ.get('DBS_NAME'),
        user=os.environ.get('DBS_USERNAME'),
        host=os.environ.get('DBS_HOST'),
        password=os.environ.get('DBS_PASSWORD'),
        port=os.environ.get('DBS_PORT'),
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT p.patch_version, p.patch_start_date, p.patch_end_date, m.id AS match_id, m.duration AS match_duration FROM (SELECT p.name AS patch_version, cast (extract (epoch from p.release_date) as integer) AS patch_start_date, cast (extract (epoch from LEAD (p.release_date) over (order by id)) as integer) AS patch_end_date FROM patches p) p INNER JOIN matches m ON m.start_time BETWEEN p.patch_start_date AND p.patch_end_date OR TRUE IS NULL;")
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

    dictionary = {"patches": patches_dict}
    cursor.close()
    conn.close()

    return JsonResponse(dictionary)


def matches(request, id):
    conn = psycopg2.connect(
        database=os.environ.get('DBS_NAME'),
        user=os.environ.get('DBS_USERNAME'),
        host=os.environ.get('DBS_HOST'),
        password=os.environ.get('DBS_PASSWORD'),
        port=os.environ.get('DBS_PORT'),
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM (SELECT p.*, items.name, ROW_NUMBER() OVER (PARTITION BY localized_name ORDER BY p.count DESC) rn FROM (SELECT mpd.id, mpd.mpd_id, mpd.hero_id, pl.item_id, COUNT(pl.item_id) as count, heroes.localized_name from purchase_logs pl, heroes, (SELECT matches.id, mpd.id as mpd_id, mpd.hero_id FROM matches, (SELECT CASE WHEN matches.radiant_win = true THEN 5 ELSE 133 END AS max, CASE WHEN matches.radiant_win = true THEN 0 ELSE 128 END AS min FROM matches WHERE matches.id = " + str(
            id) + " ) AS range, matches_players_details as mpd WHERE mpd.match_id = matches.id AND player_slot >= range.min AND player_slot < range.max AND matches.id = " + str(
            id) + ") as mpd WHERE pl.match_player_detail_id = mpd.mpd_id AND heroes.id = mpd.hero_id GROUP BY mpd.mpd_id, mpd.hero_id, pl.item_id, heroes.localized_name, mpd.id ORDER BY hero_id, count DESC) as p, items WHERE items.id = p.item_id ORDER BY p.hero_id, p.count DESC, items.name DESC) as pp WHERE pp.rn <= 5")
    result_match = cursor.fetchall()

    dict = {"id": id}
    heroes = []
    for i in range(5):
        hero_id = result_match[i * 5][2]
        hero_name = result_match[i * 5][5]
        item_dict = []
        for j in range(5):
            item_dict.append({"id": result_match[i * 5 + j][3], "name": result_match[i * 5 + j][6],
                              "count": result_match[i * 5 + j][4]})
        heroes.append({"id": hero_id, "name": hero_name, "top_purchases": item_dict})

    dict["heroes"] = heroes

    cursor.close()
    conn.close()

    return JsonResponse(dict)


def towerkills(request):
    conn = psycopg2.connect(
        database=os.environ.get('DBS_NAME'),
        user=os.environ.get('DBS_USERNAME'),
        host=os.environ.get('DBS_HOST'),
        password=os.environ.get('DBS_PASSWORD'),
        port=os.environ.get('DBS_PORT'),
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT hero_id, localized_name, max(count) FROM (SELECT hero_id, localized_name, match_id, count(*) FROM (SELECT hero_id, localized_name, match_id, isstart, SUM (CASE WHEN isstart = 1 THEN 1 ELSE 0 END) OVER (ORDER BY sub3.RN) AS SeriaId FROM(SELECT *, CASE WHEN hero_id != prev_hero or prev_hero is null THEN 1 ELSE 0 END AS IsStart FROM (SELECT ROW_NUMBER () OVER (ORDER BY obj_id) AS RN, hero_id, localized_name, match_id, lag (hero_id) OVER (ORDER BY obj_id) prev_hero FROM (SELECT go.id obj_id, h.id hero_id, h.localized_name, mpd.id mpd_id, mpd.match_id, go.subtype FROM heroes h, matches_players_details mpd, game_objectives go WHERE h.id = mpd.hero_id and mpd.id = go.match_player_detail_id_1  and go.subtype = 'CHAT_MESSAGE_TOWER_KILL') sub ) sub2 ) sub3 ) sub4 GROUP BY hero_id, localized_name, match_id, sub4.seriaid) sub5 GROUP BY hero_id, localized_name ORDER BY max DESC")
    result_max_towers = cursor.fetchall()

    dictionary = {}

    heroes = []

    for i in result_max_towers:
        heroes.append({"id": i[0], "name": i[1], "tower_kills": i[2]})
    dictionary["heroes"] = heroes

    cursor.close()
    conn.close()

    return JsonResponse(dictionary)