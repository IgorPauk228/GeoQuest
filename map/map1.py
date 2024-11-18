import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import osmnx as ox
from osmnx import distance
import overpy


def get_latlng(name):
    o = []
    with open(name, "r") as n:
        for line in n:
            o.append(line)
    with open(name, "w") as n:
        pass
    try:
        g = o[-1].split()
        latlng = (float(g[2][0:(len(g[2])-1)]), float(g[-1][0:(len(g[-1])-2)]))
        return latlng
    except:
        return "Недостаточно координат"


def get_latlng_markers(name):
    o = []
    with open(name, "r") as n:
        for line in n:
            o.append(line)
    with open(name, "w") as n:
        pass
    try:
        g = o[-1].split()
        end_latlng = (float(g[2][0:(len(g[2])-1)]), float(g[-1][0:(len(g[-1])-2)]))
        p = o[-2].split()
        start_latlng = (float(p[2][0:(len(p[2]) - 1)]), float(p[-1][0:(len(p[-1]) - 2)]))
        return start_latlng, end_latlng
    except:
        return "Недостаточно координат"

def get_latlng_location(name, location):
    o = []
    with open(name, "r") as n:
        for line in n:
            o.append(line)
    with open(name, "w") as n:
        pass
    try:
        g = o[-1].split()
        end_latlng = (float(g[2][0:(len(g[2]) - 1)]), float(g[-1][0:(len(g[-1]) - 2)]))
        start_latlng = (location["latitude"], location["longitude"])
        return start_latlng, end_latlng
    except:
        return "Недостаточно координат"


api = overpy.Overpass()
g = False
hh = False
p = False
o = []
y = []


m = folium.Map(
)

m.add_child(
    folium.ClickForMarker()
)

MODE = ["Выбрать местоположение на карте", "Мое местоположение"]
TRANSPORT = ["Пешком", "Велосипед", "Машина", "Всё"]
OPTIMIZE = ["Расстояние","Время"]
BASE = ["Построение маршрута", "Места вблизи"]
MODE_V2 = ["Выбрать местоположение на карте", "Написать в командную строку", "Мое местоположение"]
QUERIES = ["Сфера еды", "Развлечения", "Обучение", "Заправка для автомобилей", "Банковская сфера", "Медицина", "Государственные службы", "Магазины"]
with st.sidebar:
    st.title("Настройки карты")
    base = st.selectbox('Выбрать базовый режим:', BASE)
    if base == "Построение маршрута":
        mode = st.selectbox('Выбрать точку отправления', MODE)
        if mode == "Мое местоположение":
            st.write("Нажмите кнопку, чтобы отправить локацию")
            location = streamlit_geolocation()
        transport = st.selectbox('Выберите транспорт', TRANSPORT)
        optimize = st.selectbox('Оптимизировать по', OPTIMIZE)
        if st.button("Построить мартшрут", type="primary"):
            g = True
    elif base == "Места вблизи":
        mode_v2 = st.selectbox('Выбрать место', MODE_V2)
        if mode_v2 == "Выбрать местоположение на карте":
            pass
        elif mode_v2 == "Мое местоположение":
            st.write("Нажмите кнопку, чтобы отправить локацию")
            location = streamlit_geolocation()
        else:
            comand = st.text_input("Введите место:")
        QUERY = st.selectbox("Введите запрос", QUERIES)
        
        if QUERY == "Сфера еды":
            food = ["Фаст-фуд", "Кафе", "Ресторан", "Мороженое"]
            query_m = st.selectbox("Выберите тип", food)
        elif QUERY == "Развлечения":
            razvlecuha = ["Искусство", "Театр", "Кино"]
            query_m = st.selectbox("Выберите тип", razvlecuha)
        elif QUERY == "Обучение":
            education = ["Колледж", "Университет", "Библиотека", "Детский сад", "Школа"]
            query_m = st.selectbox("Выберите тип", education)
        elif QUERY == "Медицина":
            med = ["Клиника", "Стоматолог", "Врачи", "Больница", "Аптека", "Клиника для животных"]
            query_m = st.selectbox("Выберите тип", med)
        if st.button("Найти", type="primary"):
            hh = True



if g==True:
    try:
        if mode=="Выбрать местоположение на карте":
            start_latlng, end_latlng = get_latlng_markers("text")
        else:
            start_latlng, end_latlng = get_latlng_location("text", location)

        dist = ox.distance.euclidean(start_latlng[0], end_latlng[0], start_latlng[1], end_latlng[1])
        graph = ox.graph_from_point(((start_latlng[0] + end_latlng[0]) / 2, (start_latlng[1] + end_latlng[1]) / 2),
                                    dist * 50, retain_all=True, simplify=False, network_type="all")
        start_node = ox.nearest_nodes(graph, start_latlng[1], start_latlng[0])
        end_node = ox.nearest_nodes(graph, end_latlng[1], end_latlng[0])
        shortest_route = ox.shortest_path(graph, start_node, end_node, weight="length")
        nodes, streets = ox.graph_to_gdfs(graph)


        def generate_multindex(route_nodes):
            multiindex_list = []
            # append the index to list
            for u, v in zip(route_nodes[:-1], route_nodes[1:]):
                multiindex_list.append((u, v, 0))
            return multiindex_list


        gdf_nodes, gdf_edges = ox.graph_to_gdfs(graph)

        multiindex_list = generate_multindex(shortest_route)

        put_voina = gdf_edges[gdf_edges.index.isin(multiindex_list)]

        style = {'color': "#24ff17", 'weight': '3'}
        folium.GeoJson(put_voina, style_function=lambda x: style).add_to(m)
        folium.Marker(
            location = (start_latlng[0], start_latlng[1])
        ).add_to(m)
        folium.Marker(
            location=(end_latlng[0], end_latlng[1])
        ).add_to(m)
        with st.sidebar:
            st.write("Нажмите на карту, чтобы перезапустить")
    except:
        with st.sidebar:
            st.write("Произошла ошибка")



if hh == True:
    try:
        if mode_v2 == "Написать в командную строку":
            latt, lont = ox.geocode(comand)[0], ox.geocode(comand)[1]
        elif mode_v2 == "Мое местоположение":
            latt, lont = location["latitude"], location["longitude"]
        else:
            latt, lont = get_latlng("text")

        if QUERY=="Сфера еды":
            if query_m == "Фаст-фуд":
                query = """(node["amenity"="fast_food"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Кафе":
                query = """(node["amenity"="cafe"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Ресторан":
                query = """(node["amenity"="restaurant"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Мороженое":
                query = """(node["amenity"="ice_cream"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
        elif QUERY == "Развлечения":
            if query_m == "Искусство":
                query = """(node["amenity"="arts_centre"](around:15000,{lat},{lon});
                            node["amenity"="exhibition_centre"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Театр":
                query = """(node["amenity"="theatre"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Кино":
                query = """(node["amenity"="cinema"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue


        elif QUERY == "Обучение":
            if query_m == "Колледж":
                query = """(node["amenity"="college"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Университет":
                query = """(node["amenity"="university"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Библиотека":
                query = """(node["amenity"="library"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Детский сад":
                query = """(node["amenity"="kindergarten"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Школа":
                query = """(node["amenity"="school"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue


        elif QUERY == "Заправка для автомобилей":
            query = """(node["amenity"="fuel"](around:15000,{lat},{lon});
                    );out;
                    """.format(lat=latt, lon=lont)
            result = api.query(query)
            for x in result.nodes:
                data = x.tags
                try:
                    folium.Marker(
                        location=(x.lat, x.lon),
                        popup=folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                    ).add_to(m)
                except:
                    continue
        elif QUERY == "Банковская сфера":
            query = """(node["amenity"="atm"](around:15000,{lat},{lon});
                        node["amenity"="payment_terminal"](around:15000,{lat},{lon});
                        node["amenity"="bank"](around:15000,{lat},{lon});
                        node["amenity"="payment_centre"](around:15000,{lat},{lon});
                    );out;
                    """.format(lat=latt, lon=lont)
            result = api.query(query)
            for x in result.nodes:
                data = x.tags
                try:
                    folium.Marker(
                        location=(x.lat, x.lon),
                        popup=folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                    ).add_to(m)
                except:
                    continue
        elif QUERY == "Медицина":
            if query_m == "Клиника":
                query = """(node["amenity"="clinic"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Стоматолог":
                query = """(node["amenity"="dentist"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Врачи":
                query = """(node["amenity"="doctors"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Больница":
                query = """(node["amenity"="hospital"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Аптека":
                query = """(node["amenity"="pharmacy"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue
            elif query_m == "Клиника для животных":
                query = """(node["amenity"="veterinary"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
                result = api.query(query)
                for x in result.nodes:
                    print(x.tags)
                    data = x.tags
                    try:
                        folium.Marker(
                            location = (x.lat, x.lon),
                            popup = folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                        ).add_to(m)
                    except:
                        continue

        elif QUERY == "Государственные службы":
            query = """(node["amenity"="fire_station"](around:15000,{lat},{lon});
                        node["amenity"="courthouse"](around:15000,{lat},{lon});
                        node["amenity"="police"](around:15000,{lat},{lon});
                        node["amenity"="post_office"](around:15000,{lat},{lon});
                        node["amenity"="prison"](around:15000,{lat},{lon});
                        node["amenity"="ranger_station"](around:15000,{lat},{lon});
                        node["amenity"="townhall"](around:15000,{lat},{lon});
                        );out;
                        """.format(lat=latt, lon=lont)
            result = api.query(query)
            for x in result.nodes:
                data = x.tags
                try:
                    folium.Marker(
                        location=(x.lat, x.lon),
                        popup=folium.Popup(f"{data['name']}", max_width=100)
                    ).add_to(m)
                except:
                    continue
        elif QUERY == "Магазины":
            query = """(node["shop"](around:15000,{lat},{lon});
                                    );out;
                                    """.format(lat=latt, lon=lont)
            result = api.query(query)
            for x in result.nodes:
                print(x.tags)
                data = x.tags
                try:
                    folium.Marker(
                        location=(x.lat, x.lon),
                        popup=folium.Popup(f"{data['name']}", parse_html=True, max_width=100)
                    ).add_to(m)
                except:
                    continue

        with st.sidebar:
            st.write("Нажмите на карту, чтобы перезапустить")

    except:
        with st.sidebar:
            st.write("Произшла ошибка")



try:
    if base == "Построение маршрута":
        output = st_folium(m, center=start_latlng, zoom=12, width=800, height=500, returned_objects="last_clicked")
    elif base == "Места вблизи":
        output = st_folium(m, center=(latt, lont), zoom=11, width=800, height=500, returned_objects="last_clicked")
except:
    output = st_folium(m, width=800, height=500, returned_objects="last_clicked")


with open('text', 'a') as t:
    t.write(str(output) + '\n')
o.append(output)
print(o)
