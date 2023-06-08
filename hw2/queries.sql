# 1
SELECT distinct emp.name, emp.surname, emp.employees_AM
FROM employees emp, travel_guide tg, guided_tour gt, tourist_attraction ta, destination d
WHERE emp.employees_AM = tg.travel_guide_employee_AM
	  AND gt.travel_guide_employee_AM = tg.travel_guide_employee_AM
	  AND ta.destination_destination_id = d.destination_id 
      	  AND ta.tourist_attraction_id = gt.tourist_attraction_id
	  AND d.country = 'Germany';


# 2
SELECT tg.travel_guide_employee_AM as travel_guide_id, count(tg.travel_guide_employee_AM) as number_of_guided_tours
FROM travel_guide tg, trip_package tpp, guided_tour gtt  
WHERE tg.travel_guide_employee_AM = gtt.travel_guide_employee_AM AND 
tpp.trip_package_id = gtt.trip_package_id AND 
datediff(tpp.trip_start, '2019-1-1') >= 0 AND  
datediff(tpp.trip_end, '2020-1-1') < 0 AND
( 
	SELECT count(*)
    FROM guided_tour gt, trip_package tp 
    WHERE (
		tg.travel_guide_employee_AM = gt.travel_guide_employee_AM AND 
        tp.trip_package_id = gt.trip_package_id AND 
        datediff(tp.trip_start, '2019-1-1') >= 0 AND  
        datediff(tp.trip_end, '2020-1-1') < 0
	)
) > 3 
GROUP BY tg.travel_guide_employee_AM;


# 3
SELECT tab.travel_agency_branch_id, count(distinct emp.employees_AM) AS 'number of employees'
FROM employees emp, travel_agency_branch tab
WHERE emp.travel_agency_branch_travel_agency_branch_id = tab.travel_agency_branch_id
GROUP BY tab.travel_agency_branch_id;


# 4
SELECT trip_package_id, count(distinct Reservation_id)  
FROM trip_package t, reservation r 
WHERE t.trip_package_id = r.offer_trip_package_id AND t.trip_start LIKE '2021%' AND t.trip_end LIKE '2021%'
      AND t.trip_package_id IN (
		SELECT hd.trip_package_trip_package_id
		FROM trip_package_has_destination hd, destination d  
		WHERE hd.destination_destination_id = d.destination_id AND d.name = 'Paris'
	)


# 5
SELECT e.name, e.surname
FROM travel_guide t, guided_tour g1, employees e
WHERE t.travel_guide_employee_AM = g1.travel_guide_employee_AM AND e.employees_AM = t.travel_guide_employee_AM
		AND NOT EXISTS (
			SELECT *
			FROM guided_tour g2
			WHERE g2.travel_guide_language_id != g1.travel_guide_language_id
			AND g2.travel_guide_employee_AM = g1.travel_guide_employee_AM
        )
GROUP BY e.name, e.surname


# 6
SELECT 'NO' AS Answer
WHERE NOT EXISTS ( SELECT o.offer_id 
	FROM offer o  WHERE NOT EXISTS(
		SELECT r.Reservation_id 
			FROM reservation r 
				WHERE r.offer_id = o.offer_id) AND 
	o.offer_start LIKE '2020%' 
    AND o.offer_end LIKE '2020%')
UNION
SELECT 'YES' AS Answer
WHERE EXISTS ( SELECT o.offer_id 
	FROM offer o  WHERE NOT EXISTS(
		SELECT r.Reservation_id 
			FROM reservation r 
				WHERE r.offer_id = o.offer_id) AND 
	o.offer_start LIKE '2020%' 
    AND o.offer_end LIKE '2020%')


# 7
SELECT tr.name
FROM traveler tr
WHERE tr.gender = 'male' AND tr.age > 2039 AND EXISTS (
	SELECT res.Customer_id
    FROM reservation res
    WHERE res.Customer_id = tr.traveler_id
    GROUP BY res.Customer_id
    HAVING count(*) > 3
);


# 8
SELECT e.employees_AM as travel_guide_id, e.name, e.surname, count(ta.tourist_attraction_id) as nubmer_of_attractions
FROM employees e, tourist_attraction ta, languages l
WHERE
	l.languages_id IN (
		SELECT la.languages_id
		FROM languages la
		WHERE la.name = 'English'
	)
    and e.employees_AM IN (
		SELECT tghl.travel_guide_employee_AM
		FROM travel_guide_has_languages tghl
		WHERE tghl.languages_id = l.languages_id
	)
    and ta.tourist_attraction_id IN (
		SELECT gt.tourist_attraction_id  
		FROM guided_tour gt, languages lg
		WHERE gt.travel_guide_employee_AM = e.employees_AM AND gt.travel_guide_language_id = l.languages_id
	) 
GROUP BY e.employees_AM, e.name, e.surname;


# 9
SELECT d.country
FROM destination d, trip_package_has_destination tphd
WHERE tphd.destination_destination_id = d.destination_id
GROUP BY d.country
HAVING count(DISTINCT tphd.trip_package_trip_package_id) >= ALL (
	SELECT count(DISTINCT  tphdd.trip_package_trip_package_id)
	FROM destination dd, trip_package_has_destination tphdd
	WHERE tphdd.destination_destination_id = dd.destination_id 
    GROUP BY dd.country
);


# 10
SELECT DISTINCT tp.trip_package_id
FROM trip_package tp
WHERE NOT EXISTS
(
	SELECT d.destination_id FROM destination d
	WHERE d.country = 'Ireland' AND NOT EXISTS
    (
		SELECT tphd.trip_package_trip_package_id
        FROM trip_package_has_destination tphd
        WHERE tphd.destination_destination_id = d.destination_id
			  AND tphd.trip_package_trip_package_id = tp.trip_package_id
    )
);


# 11
SELECT emp.name
FROM employees emp, travel_guide tg
WHERE emp.employees_AM = tg.travel_guide_employee_AM AND NOT EXISTS
(
	SELECT d.destination_id FROM destination d WHERE d.country = 'Germany'
    AND NOT EXISTS
    (
		SELECT tphd.trip_package_trip_package_id
        FROM trip_package_has_destination tphd, guided_tour gt
        WHERE tphd.destination_destination_id = d.destination_id
              AND gt.trip_package_id = tphd.trip_package_trip_package_id
              AND gt.travel_guide_employee_AM = emp.employees_AM
    )
);
