from dotenv import load_dotenv
from geopy import distance
import folium
import json
import os
import requests


def fetch_coordinates(apikey, address):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = (
                    response.json()
                    ['response']
                    ['GeoObjectCollection']
                    ['featureMember']
                )

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lat, lon


def get_shop_distance(shop_info):
    return shop_info['distance']


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')
    address = input('Где вы находитесь? ')
    user_coordinates = fetch_coordinates(apikey, address)
    fetch_coordinates(apikey, address)
    with open("files/coffee.json", encoding='CP1251') as file:
        coffee_shops = json.load(file)
    shops = []
    for shop in coffee_shops:
        shop_info = {}
        shop_info['title'] = shop['Name']
        shop_info['longitude'] = shop['geoData']['coordinates'][0]
        shop_info['latitude'] = shop['geoData']['coordinates'][1]
        shop_info['distance'] = (
                            distance.distance(
                                user_coordinates,
                                (shop_info['latitude'], shop_info['longitude'])
                                ).km
                            )
        shops.append(shop_info)
    get_shop_distance(shop_info)
    sorted_shops = sorted(shops, key=get_shop_distance)
    closest_shops = sorted_shops[:5]
    m = folium.Map(location=user_coordinates, zoom_start=12)
    folium.Marker(
        location=user_coordinates,
        tooltip="Нажми меня!",
        popup="Вы здесь",
        icon=folium.Icon(icon="cloud"),
    ).add_to(m)
    for shop_info in closest_shops:
        folium.Marker(
            location=(shop_info['latitude'], shop_info['longitude']),
            tooltip="Нажми меня!",
            popup=shop_info['title'],
            icon=folium.Icon(color="green"),
        ).add_to(m)
    m.save("index.html")


if __name__ == '__main__':
    main()
