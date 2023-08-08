from datetime import datetime
fare_table = {
    ('1', '1'): {'peak': 30, 'off_peak': 25},
    ('1', '2'): {'peak': 35, 'off_peak': 30},
    ('2', '1'): {'peak': 35, 'off_peak': 30},
    ('2', '2'): {'peak': 25, 'off_peak': 20}
}
fare_capping = {
    ('1', '1'): {'daily': 100, 'weekly': 500},
    ('1', '2'): {'daily': 120, 'weekly': 600},
    ('2', '1'): {'daily': 120, 'weekly': 600},
    ('2', '2'): {'daily': 80, 'weekly': 400}
}


def calculate_fare(journeys):
    daily_fares = {}
    daily_max_zone = {}
    weekly_max_zone = {}
    journeys_by_week = {}
    weekly_fares = {}
    for journey in journeys:
        day = journey['Day']
        year, week_number, _ = journey['Day'].isocalendar()
        week_key = (year, week_number)
        if week_key in journeys_by_week:
            journeys_by_week[week_key].append(day)
        else:
            journeys_by_week[week_key] = [day]
        from_zone = journey['From Zone']
        to_zone = journey['To Zone']
        time = datetime.strptime(journey['Time'], '%H:%M')
        peak_hours = (7 <= time.hour + time.minute/60 <
                      10.5) or (17 <= time.hour + time.minute/60 < 20)
        off_peak_hours = not peak_hours

        fare = fare_table.get((from_zone, to_zone), {}).get(
            'peak' if peak_hours else 'off_peak', 0)
        if from_zone != '1' and to_zone == '1':
            if day.weekday() in [0, 1, 2, 3, 4] and 17 <= time.hour < 20:
                fare -= 5
            if day.weekday() in [5, 6] and 18 <= time.hour < 22:
                fare -= 5
        if day not in daily_fares:
            daily_fares[day] = fare
        else:
            daily_fares[day] += fare
        if day in daily_max_zone:
            if (from_zone == '1' and to_zone == '2') or (from_zone == '2' and to_zone == '1'):
                daily_max_zone[day] = [from_zone, to_zone]
            if daily_max_zone[day][0] == '2' and daily_max_zone[day][1] == '2':
                daily_max_zone[day] = [from_zone, to_zone]
        else:
            daily_max_zone[day] = [from_zone, to_zone]
    for day, fair in daily_fares.items():
        zone_pair = tuple(daily_max_zone[day])
        daily_value = fare_capping.get(zone_pair, {}).get('daily', None)
        dummy_value = min(daily_value, daily_fares[day])
        daily_fares[day] = dummy_value
    for week_key, days in journeys_by_week.items():
        for day in days:
            if week_key in weekly_max_zone:
                if (daily_max_zone[day][0] == '1' and daily_max_zone[day][1] == '2') or (daily_max_zone[day][0] == '2' and daily_max_zone[day][1] == '1'):
                    weekly_max_zone[week_key] = [
                        daily_max_zone[day][0], daily_max_zone[day][1]]
                if weekly_max_zone[week_key][0] == '2' and weekly_max_zone[week_key][1] == '2':
                    weekly_max_zone[week_key] = [
                        daily_max_zone[day][0], daily_max_zone[day][1]]
            else:
                weekly_max_zone[week_key] = [
                    daily_max_zone[day][0], daily_max_zone[day][1]]
    for key, date in journeys_by_week.items():
        dummy = 0
        for val in date:
            dummy += daily_fares[val]
        weekly_fares[key] = dummy
    for key in weekly_fares.items():
        zone_pair = tuple(weekly_max_zone[key])
        daily_value = fare_capping.get(zone_pair, {}).get('weekly', None)
        dummy_value = min(daily_value, weekly_fares[key])
        weekly_fares[key] = dummy_value
    print(daily_fares)
    print(weekly_fares)
