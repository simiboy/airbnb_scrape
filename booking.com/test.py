import urllib.parse
from datetime import date, timedelta

def get_weekend_dates_two_months_ahead():
    """Return (checkin, checkout) for a 1-night weekend stay two months ahead."""
    today = date.today()
    target_month = (today.month + 2 - 1) % 12 + 1
    target_year = today.year + ((today.month + 2 - 1) // 12)

    first_day = date(target_year, target_month, 1)
    days_until_friday = (4 - first_day.weekday()) % 7
    checkin = first_day + timedelta(days=days_until_friday)
    checkout = checkin + timedelta(days=1)
    return checkin.isoformat(), checkout.isoformat()

def booking_district_url(district_number, checkin, checkout):
    """Generate Booking.com URL matching the 'I'm flexible' weekend format."""
    districts = {
        1: ("Budavár", 1244),
        2: ("Rózsadomb", 1245),
        3: ("Óbuda", 1246),
        4: ("Újpest", 1247),
        5: ("Belváros - Lipótváros", 1248),
        6: ("Terézváros", 1249),
        7: ("Erzsébetváros", 1250),
        8: ("Józsefváros", 1251),
        9: ("Ferencváros", 1252),
        10: ("Kőbánya", 1253),
        11: ("Újbuda", 1254),
        12: ("Hegyvidék", 1255),
        13: ("Angyalföld", 1256),
        14: ("Zugló", 1257),
        15: ("Rákospalota", 1258),
        16: ("Mátyásföld", 1259),
        17: ("Rákosmente", 1260),
        18: ("Pestszentlőrinc", 1261),
        19: ("Kispest", 1262),
        20: ("Pesterzsébet", 1263),
        21: ("Csepel", 1264),
        22: ("Budafok", 1265),
        23: ("Soroksár", 1266)
    }

    if district_number not in districts:
        raise ValueError(f"District {district_number} not found.")

    district_name, dest_id = districts[district_number]
    ss = f"{district_number:02d}. {district_name}"
    encoded_ss = urllib.parse.quote(ss)

    url = (
        "https://www.booking.com/searchresults.html?"
        f"ss={encoded_ss}"
        f"&ssne={encoded_ss}"
        f"&ssne_untouched={encoded_ss}"
        "&efdco=1"
        "&label=gen173nr-10CAQoggJCDWRpc3RyaWN0XzEyNDlIMVgEaGeIAQGYATO4ARfIAQzYAQPoAQH4AQGIAgGoAgG4AprIt8gGwAIB0gIkMTZkOTMwY2ItMzg5MS00ZmM0LTgyYjQtOTEyMjdkMGQzNjlk2AIB4AIB"
        "&aid=304142"
        "&lang=en-us"
        "&sb=1"
        "&src_elem=sb"
        "&src=searchresults"
        f"&dest_id={dest_id}&dest_type=district"
        f"&checkin={checkin}&checkout={checkout}"
        "&ltfd=5%3A1%3A1-2026%3A1%3A"
        "&group_adults=2&no_rooms=1&group_children=0"
    )

    return url

if __name__ == "__main__":
    checkin, checkout = get_weekend_dates_two_months_ahead()

    print(booking_district_url(22, checkin, checkout))
