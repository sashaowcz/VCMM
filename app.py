"""MTBLANC-VCMM V9 — interface mobile météo alpine (Streamlit Cloud)."""
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="MTBLANC-VCMM | Météo alpine", page_icon="🏔️", layout="wide", initial_sidebar_state="collapsed")
TZ = ZoneInfo("Europe/Zurich")
POINTS = {
    "Verbier": (46.096, 7.228, 1500, "4 Vallées"),
    "Mont Fort": (46.081, 7.318, 3329, "4 Vallées"),
    "Les Attelas": (46.103, 7.270, 2727, "4 Vallées"),
    "La Tzoumaz": (46.145, 7.234, 1500, "4 Vallées"),
    "Nendaz": (46.183, 7.294, 1400, "4 Vallées"),
    "Veysonnaz": (46.196, 7.335, 1350, "4 Vallées"),
    "Thyon 2000": (46.178, 7.388, 2000, "4 Vallées"),
    "Bruson": (46.066, 7.216, 1100, "4 Vallées"),
    "Le Châble": (46.080, 7.216, 820, "4 Vallées"),
    "Martigny": (46.102, 7.073, 471, "Corridor"),
    "Trient": (46.056, 6.995, 1300, "Corridor"),
    "Vallorcine": (46.034, 6.933, 1260, "Chamonix"),
    "Le Tour": (46.003, 6.946, 1460, "Chamonix"),
    "Argentière": (45.982, 6.927, 1250, "Chamonix"),
    "Grands Montets": (45.956, 6.961, 3275, "Chamonix"),
    "Chamonix": (45.924, 6.869, 1035, "Chamonix"),
    "Brévent": (45.933, 6.838, 2525, "Chamonix"),
    "Aiguille du Midi": (45.879, 6.887, 3842, "Chamonix"),
    "Les Houches": (45.890, 6.799, 1000, "Chamonix"),
    "Saint-Gervais": (45.893, 6.712, 850, "Megève"),
    "Megève": (45.857, 6.617, 1110, "Megève"),
    "Mont d’Arbois": (45.865, 6.653, 1833, "Megève"),
    "Rochebrune": (45.835, 6.643, 1754, "Megève"),
    "Côte 2000": (45.829, 6.675, 2000, "Megève"),
    "Combloux": (45.897, 6.644, 960, "Megève"),
    "Les Contamines": (45.821, 6.728, 1164, "Megève"),
    "Praz-sur-Arly": (45.837, 6.573, 1030, "Megève"),
    "Courmayeur": (45.793, 6.969, 1224, "Aoste"),
    "Aoste": (45.737, 7.321, 583, "Aoste"),
    "Genève": (46.204, 6.143, 375, "Léman"),
    "Évian-les-Bains": (46.401, 6.591, 372, "Léman"),
    "Montreux": (46.431, 6.911, 390, "Léman"),
}

st.markdown("""<style>
:root{--bg:#080b09;--panel:#171d19;--edge:#526359;--lime:#c0ff45;--red:#ff5b64}
html,body,[data-testid="stAppViewContainer"],.stApp{background:var(--bg)!important;color:#f7faf7!important}
[data-testid="stHeader"]{background:var(--bg)!important}
.block-container{padding-top:1.3rem!important;max-width:1120px!important;padding-left:1rem!important;padding-right:1rem!important}
[data-testid="stSidebar"]{background:#171d19!important}
.stApp p,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp li,.stApp small{color:#f7faf7!important}
[data-testid="stCaptionContainer"] p{color:#d1dcd4!important}
[data-testid="stMarkdownContainer"] a{color:var(--lime)!important}
[data-testid="stMetric"]{border:1px solid #65756a!important;background:var(--panel)!important;padding:13px!important;border-radius:0!important}
[data-testid="stMetricLabel"] *,[data-testid="stMetricValue"] *,[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{color:white!important;-webkit-text-fill-color:white!important;opacity:1!important}
[data-testid="stMetricValue"]{font-size:clamp(1.5rem,5vw,2.1rem)!important}
button,[data-baseweb="select"],input,textarea,[data-testid="stAlert"],div[data-testid="stExpander"],div[data-testid="stDataFrame"],div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:0!important}
[data-testid="stAlert"] p,[data-testid="stAlert"] div{color:#142018!important}
[data-testid="stAlert"]{background:#e6f0e8!important}
[data-testid="stButton"] button[kind="primary"]{background:var(--lime)!important;color:#0b120c!important;font-weight:800!important;border:0!important}
[data-testid="stButton"] button[kind="secondary"]{background:#202b23!important;color:white!important;border:1px solid #738476!important}
[data-baseweb="select"]>div{background:#f7f9f7!important;color:#111!important}
[data-baseweb="select"] span,[data-baseweb="select"] input{color:#111!important}
[data-testid="stSlider"] p{color:white!important}
[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{color:white!important}
.brand{border-left:6px solid var(--lime);background:#172019;padding:14px 17px;margin-bottom:12px}
.brand .small{font-size:.72rem;letter-spacing:.12em;font-weight:800;color:var(--lime)}
.brand .name{font-size:clamp(1.6rem,6vw,2.6rem);font-weight:900;line-height:1.2;color:white;margin:7px 0}
.brand .name span{color:var(--lime)}
.brand .sub{font-size:.82rem;color:#e4ece5}
.section{border-left:4px solid var(--lime);padding-left:10px;margin:16px 0 8px;font-size:1.13rem;font-weight:850;color:white}
.place{background:#171d19;border:1px solid #647668;padding:13px 15px;margin-bottom:10px;min-height:130px}
.place .place-title{font-weight:850;font-size:1.05rem;color:#fff}
.place .place-temp{font-weight:900;font-size:2rem;color:var(--lime);line-height:1.4}
.place .place-info{font-size:.82rem;color:#e0e8e0}
.place .place-time{font-size:.7rem;color:#cbd9cf}
.info-panel{background:#18221a;border-left:4px solid var(--lime);padding:12px 14px;color:#f6fff6;margin:10px 0}
.warn-panel{background:#30191c;border-left:4px solid var(--red);padding:12px 14px;color:white;margin:10px 0}
[data-testid="stTabs"] button{color:#f7fff7!important;font-weight:700!important}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--lime)!important}
@media(max-width:650px){.block-container{padding-left:.75rem!important;padding-right:.75rem!important}.brand{padding:12px}.place{min-height:0}.stApp h1{font-size:1.5rem}}
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=60, show_spinner=False)
def weather(name, altitude=None):
    lat,lon,natural,_ = POINTS[name]
    params={"latitude":lat,"longitude":lon,"elevation":natural if altitude is None else altitude,
            "current":"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_gusts_10m,weather_code",
            "hourly":"temperature_2m,precipitation,snowfall,wind_speed_10m,wind_gusts_10m,freezing_level_height",
            "forecast_days":3,"timezone":"Europe/Zurich"}
    resp=requests.get("https://api.open-meteo.com/v1/forecast",params=params,timeout=12)
    resp.raise_for_status()
    return resp.json()

@st.cache_data(ttl=60, show_spinner=False)
def radar():
    resp=requests.get("https://api.rainviewer.com/public/weather-maps.json",timeout=9)
    resp.raise_for_status()
    data=resp.json()
    return data.get("host","https://tilecache.rainviewer.com"), data.get("radar",{}).get("past",[])

def fmt(value, unit="", decimals=0):
    if value is None:return "—"
    try:return f"{float(value):.{decimals}f}{unit}"
    except (TypeError,ValueError):return "—"

def time_label(s):
    if not s:return "Heure inconnue"
    try:return dt.datetime.fromisoformat(s).strftime("%d/%m %H:%M")
    except ValueError:return str(s)

def point_card(name, d):
    if not d:
        return f'<div class="place"><div class="place-title">{name}</div><div class="place-info">Données indisponibles</div></div>'
    c=d.get("current",{})
    return (f'<div class="place"><div class="place-title">{name.upper()}</div>'
            f'<div class="place-temp">{fmt(c.get("temperature_2m")," °C",1)}</div>'
            f'<div class="place-info">Vent {fmt(c.get("wind_speed_10m")," km/h")} · Rafales {fmt(c.get("wind_gusts_10m")," km/h")}</div>'
            f'<div class="place-time">Prévision modèle · {time_label(c.get("time"))}</div></div>')

st.markdown('<div class="brand"><div class="small">MÉTÉO ALPINE / TERRAIN / SÉCURITÉ</div><div class="name">MT<span>BLANC</span>-VCMM</div><div class="sub">VERBIER · 4 VALLÉES · CHAMONIX · MEGÈVE</div></div>',unsafe_allow_html=True)

page=st.radio("Navigation",["Accueil","Carte & radar","Détail météo","Terrain & secours","Webcams"],horizontal=True,label_visibility="collapsed")

@st.fragment(run_every="60s")
def overview():
    st.markdown('<div class="section">LES 3 SECTEURS — DERNIÈRE PRÉVISION DISPONIBLE</div>',unsafe_allow_html=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={name:pool.submit(weather,name) for name in ["Verbier","Chamonix","Megève"]}
        results={}
        for name,f in futures.items():
            try:results[name]=f.result()
            except Exception:results[name]=None
    cols=st.columns(3)
    for col,name in zip(cols,["Verbier","Chamonix","Megève"]):
        with col:st.markdown(point_card(name,results[name]),unsafe_allow_html=True)
    st.caption("Contrôle automatique toutes les 60 s. Les heures affichées sont celles des prévisions du fournisseur, pas des mesures sur piste.")

@st.fragment(run_every="60s")
def details(name, altitude):
    try:d=weather(name,altitude)
    except Exception as exc:
        st.error(f"Données indisponibles : {exc}")
        return
    c=d.get("current",{})
    st.markdown(f'<div class="section">{name.upper()} · {altitude} M</div>',unsafe_allow_html=True)
    cols=st.columns(2)
    for col,label,key,unit in [(cols[0],"Température","temperature_2m"," °C"),(cols[1],"Rafales","wind_gusts_10m"," km/h")]:
        col.metric(label,fmt(c.get(key),unit,1))
    cols2=st.columns(2)
    cols2[0].metric("Vent à 10 m",fmt(c.get("wind_speed_10m")," km/h",1))
    cols2[1].metric("Précipitations actuelles (modèle)",fmt(c.get("precipitation")," mm",1))
    st.caption(f"Source : Open-Meteo · Heure de validité : {time_label(c.get('time'))} · Altitude modèle : {d.get('elevation','—')} m")
    st.markdown('<div class="section">PROCHAINES 12 HEURES</div>',unsafe_allow_html=True)
    h=pd.DataFrame(d.get("hourly",{}))
    if not h.empty:
        h["time"]=pd.to_datetime(h["time"])
        now=pd.Timestamp.now(tz=TZ).tz_localize(None)
        h=h[h["time"]>=now.floor("h")].head(12)
        cols={"time":"Heure","temperature_2m":"Temp. °C","precipitation":"Précip. mm","snowfall":"Neige cm","wind_gusts_10m":"Rafales km/h","freezing_level_height":"Iso 0 °C m"}
        st.dataframe(h[list(cols)].rename(columns=cols).assign(Heure=lambda x:x.Heure.dt.strftime("%d/%m %Hh")),hide_index=True,use_container_width=True,height=320)
    st.caption("Les altitudes par pas de 50 m sont des ajustements de modèle, pas des observations tous les 50 m.")

if page=="Accueil":
    overview()
    st.markdown('<div class="section">ACCÈS RAPIDE</div>',unsafe_allow_html=True)
    st.markdown('<div class="info-panel">Choisis « Détail météo » pour consulter une piste ou un sommet et régler son altitude. « Carte & radar » affiche les précipitations observées sur la région.</div>',unsafe_allow_html=True)
    st.markdown('<div class="section">SECTEURS COUVERTS</div>',unsafe_allow_html=True)
    st.write("4 Vallées · Chamonix · Megève · corridor Martigny–Trient–Vallorcine · Aoste · Genève et Léman")
    st.markdown('<div class="warn-panel">Pour les décisions de sécurité en montagne, consulte toujours les observations de terrain et les bulletins officiels. Cette application n’est pas un outil de dispatch ou d’alerte certifié.</div>',unsafe_allow_html=True)

elif page=="Détail météo":
    groups=["4 Vallées","Chamonix","Megève","Corridor","Aoste","Léman"]
    group=st.selectbox("Secteur",groups)
    names=[n for n,p in POINTS.items() if p[3]==group]
    place=st.selectbox("Station / sommet / village",names)
    natural=POINTS[place][2]
    natural_mode=st.toggle("Utiliser l'altitude du lieu",value=True)
    altitude=natural if natural_mode else st.slider("Altitude demandée (pas de 50 m)",500,4000,min(4000,max(500,round(natural/50)*50)),50)
    details(place,altitude)

elif page=="Carte & radar":
    st.markdown('<div class="section">CARTE INTERACTIVE</div>',unsafe_allow_html=True)
    st.markdown('<div class="info-panel">Déplace la carte avec le doigt et zoome avec deux doigts. Le radar peut être activé ou désactivé. La chronologie concerne les observations radar disponibles, pas des prévisions futures.</div>',unsafe_allow_html=True)
    area=st.selectbox("Centrer la carte sur",["Tout le corridor","Verbier / 4 Vallées","Chamonix","Megève","Léman"])
    centers={"Tout le corridor":([46.01,6.95],9),"Verbier / 4 Vallées":([46.13,7.26],11),"Chamonix":([45.94,6.87],11),"Megève":([45.86,6.65],11),"Léman":([46.29,6.47],9)}
    radar_on=st.toggle("Afficher le radar des précipitations",value=True)
    host,frames=None,[]
    if radar_on:
        try:host,frames=radar()
        except Exception:st.warning("Radar temporairement indisponible. La carte reste utilisable.")
    frame=None
    if frames:
        idx=st.slider("Historique radar disponible",0,len(frames)-1,len(frames)-1)
        frame=frames[idx]
        stamp=dt.datetime.fromtimestamp(frame["time"],TZ)
        st.caption(f"Image radar : {stamp:%d/%m/%Y %H:%M} · {len(frames)} images accessibles. Historique de 48 h non garanti.")
    elif radar_on:st.caption("Aucune image radar actuellement disponible.")
    loc,zoom=centers[area]
    m=folium.Map(location=loc,zoom_start=zoom,tiles="OpenStreetMap",control_scale=True,zoom_control=True)
    for name,(lat,lon,elev,sector) in POINTS.items():
        folium.CircleMarker([lat,lon],radius=5,color="#121b12",weight=2,fill=True,fill_color="#baff35",fill_opacity=1,tooltip=f"{name} · {elev} m",popup=f"{name} · {elev} m").add_to(m)
    if frame:
        # Native radar resolution is limited; Leaflet can upscale tiles on zoom.
        tiles=f"{host}{frame['path']}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
        folium.TileLayer(tiles=tiles,attr="RainViewer",name="Radar",overlay=True,control=False,opacity=.65,max_zoom=19,max_native_zoom=7).add_to(m)
    st_folium(m,height=480,use_container_width=True,key=f"map_{area}",returned_objects=[])
    st.caption("Source radar : RainViewer. Les images sont mises à disposition avec un décalage possible ; les tuiles ne deviennent pas plus précises en zoomant.")
    st.markdown("**Prévisions de pluie et neige :** consulte « Détail météo » pour le point choisi. Les prévisions ne sont pas des images radar.")

elif page=="Terrain & secours":
    st.markdown('<div class="section">BRIEFING TERRAIN — COMMENT L’UTILISER</div>',unsafe_allow_html=True)
    st.markdown('<div class="warn-panel">Outil de préparation uniquement. Il ne déclenche aucune intervention et ne remplace ni les bulletins officiels, ni les décisions des responsables de secours.</div>',unsafe_allow_html=True)
    st.write("**1.** Consulte le bulletin d’avalanche du secteur. **2.** Vérifie les observations de vent, neige et visibilité. **3.** Contrôle les remontées, les accès et les moyens de communication. **4.** Valide la décision avec ton organisation.")
    for label,url in [
        ("Avalanches Suisse — SLF","https://www.slf.ch/fr/bulletin-davalanches-et-situation-nivologique/"),
        ("Météo-France — Montagne","https://meteofrance.com/meteo-montagne"),
        ("MétéoSuisse","https://www.meteosuisse.admin.ch/"),
        ("Bulletins Val d'Aoste","https://cf.regione.vda.it/")]:
        st.link_button(label,url,use_container_width=True)
    st.markdown('<div class="section">CHECKLIST DE BRIEFING (LOCALE À CETTE SESSION)</div>',unsafe_allow_html=True)
    for x in ["Bulletin officiel lu et daté","Observations terrain comparées aux modèles","Vent en crête et transport de neige vérifiés","Visibilité et météo à l’altitude prévue vérifiées","Accès, communications et protocole de secours confirmés"]:
        st.checkbox(x,key="brief_"+x)
    st.caption("Ces cases ne sont ni transmises à un centre de secours ni enregistrées comme compte rendu officiel.")

elif page=="Webcams":
    st.markdown('<div class="section">WEBCAMS — SOURCES OFFICIELLES</div>',unsafe_allow_html=True)
    st.write("Accès aux pages des stations. La disponibilité et l'heure des images dépendent de leurs exploitants.")
    links=[("Verbier 4 Vallées","https://verbier4vallees.ch/"),("Chamonix","https://www.chamonix.com/"),("Megève","https://www.megeve-tourisme.fr/"),("Les Houches","https://www.chamonix.com/"),("Nendaz","https://www.nendaz.ch/"),("Saint-Gervais","https://www.saintgervais.com/")]
    for label,url in links:st.link_button(f"Webcams / site officiel — {label}",url,use_container_width=True)
    st.caption("Ces liens mènent aux sites des destinations ; certaines webcams nécessitent une navigation supplémentaire.")

st.divider()
st.caption("MTBLANC-VCMM V9 · Vérification automatique des données toutes les 60 s sur l’accueil et le détail météo. Aucune garantie de publication minute par minute des sources. Pour les secours, privilégier les organismes officiels.")
