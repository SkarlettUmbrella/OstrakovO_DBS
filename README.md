# OstrakovO_DBS
 
 task 1 avaliable at: https://fiit-dbs-xostrakov-app.azurewebsites.net/v1/health
 
 task 2.1 avaliable at: https://fiit-dbs-xostrakov-app.azurewebsites.net/v2/patches/
 
  task 3.1 avaliable at: https://fiit-dbs-xostrakov-app.azurewebsites.net.v3/matches/{id}/top_purchases
  
  query: 
 SELECT * FROM
(SELECT p.*, items.name, ROW_NUMBER() OVER (PARTITION BY localized_name ORDER BY p.count DESC) rn FROM
(SELECT mpd.id, mpd.mpd_id, mpd.hero_id, pl.item_id, COUNT(pl.item_id) as count, heroes.localized_name from purchase_logs pl, heroes, 
(SELECT matches.id, mpd.id as mpd_id, mpd.hero_id FROM matches,
(SELECT
	CASE WHEN matches.radiant_win = true THEN 5
         ELSE 132 END AS max,
 	CASE WHEN matches.radiant_win = true THEN 0
         ELSE 128 END AS min
FROM matches
WHERE matches.id = 0 ) AS range,
matches_players_details as mpd
WHERE mpd.match_id = matches.id AND player_slot >= range.min AND player_slot < range.max AND matches.id = 0) as mpd
WHERE pl.match_player_detail_id = mpd.mpd_id AND heroes.id = mpd.hero_id
GROUP BY mpd.mpd_id, mpd.hero_id, pl.item_id, heroes.localized_name, mpd.id
ORDER BY mpd.mpd_id, count DESC) as p, items
WHERE items.id = p.item_id
ORDER BY p.hero_id, p.count DESC, items.name DESC) as pp WHERE pp.rn <= 5
  
   task 3.3 avaliable at: https://fiit-dbs-xostrakov-app.azurewebsites.net/v3/statistics/tower_kills/
   
   query:
SELECT 
	hero_id, localized_name, max(count)
	FROM
		(SELECT hero_id, localized_name, match_id, count(*)
		FROM
			(SELECT
			hero_id, localized_name, match_id, isstart,
			SUM (CASE WHEN isstart = 1 THEN 1 ELSE 0 END) OVER (ORDER BY sub3.RN) AS SeriaId
			FROM
				(SELECT 
				*,
				CASE WHEN hero_id != prev_hero or prev_hero is null THEN 1 ELSE 0 END AS IsStart
				FROM
					(SELECT
					  ROW_NUMBER () OVER (ORDER BY obj_id) AS RN,
					  hero_id, localized_name, match_id, 
					  lag (hero_id) OVER (ORDER BY obj_id) prev_hero
					FROM
					 (SELECT go.id obj_id, h.id hero_id, h.localized_name, mpd.id mpd_id, mpd.match_id, go.subtype 
						FROM heroes h, matches_players_details mpd, game_objectives go
						WHERE h.id = mpd.hero_id and mpd.id = go.match_player_detail_id_1 
							and go.subtype = 'CHAT_MESSAGE_TOWER_KILL') sub
						) sub2 
				) sub3 
			) sub4
		GROUP BY hero_id, localized_name, match_id, sub4.seriaid) sub5
	GROUP BY hero_id, localized_name
	ORDER BY max DESC
