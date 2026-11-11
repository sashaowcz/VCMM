import datetime as dt
import html
import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title='MTBLANC-VCMM | Météo alpine', page_icon='🏔️', layout='wide')

LOCATIONS = {
 'Verbier': (46.096, 7.228, 1500, '4 Vallées'),
 'Mont Fort': (46.081, 7.318, 3329, '4 Vallées'),
 'Les Attelas': (46.103, 7.270, 2727, '4 Vallées'),
 'La Tzoumaz': (46.145, 7.234, 1500, '4 Vallées'),
 'Nendaz': (46.183, 7.294, 1400, '4 Vallées'),
 'Veysonnaz': (46.196, 7.335, 1350, '4 Vallées'),
 'Thyon 2000': (46.178, 7.388, 2000, '4 Vallées'),
 'Bruson': (46.066, 7.216, 1100, '4 Vallées'),
 'Le Châble': (46.080, 7.216, 820, '4 Vallées'),
 'Martigny': (46.102, 7.073, 471, 'Corridor alpin'),
 'Trient': (46.056, 6.995, 1300, 'Corridor alpin'),
 'Vallorcine': (46.034, 6.933, 1260, 'Chamonix'),
 'Le Tour': (46.003, 6.946, 1460, 'Chamonix'),
 'Argentière': (45.982, 6.927, 1250, 'Chamonix'),
 'Grands Montets': (45.956, 6.961, 3275, 'Chamonix'),
 'Chamonix': (45.924, 6.869, 1035, 'Chamonix'),
 'Brévent': (45.933, 6.838, 2525, 'Chamonix'),
 'Aiguille du Midi': (45.879, 6.887, 3842, 'Chamonix'),
 'Les Houches': (45.890, 6.799, 1000, 'Chamonix'),
 'Saint-Gervais': (45.893, 6.712, 850, 'Megève'),
 'Megève': (45.857, 6.617, 1110, 'Megève'),
 'Mont d’Arbois': (45.865, 6.653, 1833, 'Megève'),
 'Rochebrune': (45.835, 6.643, 1754, 'Megève'),
 'Côte 2000': (45.829, 6.675, 2000, 'Megève'),
 'Combloux': (45.897, 6.644, 960, 'Megève'),
 'Les Contamines': (45.821, 6.728, 1164, 'Megève'),
 'Praz-sur-Arly': (45.837, 6.573, 1030, 'Megève'),
 'Courmayeur': (45.793, 6.969, 1224, 'Aoste'),
 'Aoste': (45.737, 7.321, 583, 'Aoste'),
 'Genève': (46.204, 6.143, 375, 'Léman'),
 'Évian-les-Bains': (46.401, 6.591, 372, 'Léman'),
 'Montreux': (46.431, 6.911, 390, 'Léman'),
}

st.markdown('''<style>
:root{--neon:#b4ff00;--red:#f04444}
.stApp{background:#090d0b;color:#f4f6f4}
[data-testid="stSidebar"]{background:#131a15}
[data-testid="stMetric"]{background:#171e19;border:1px solid #485448;padding:12px;border-radius:0}
div[data-testid="stVerticalBlockBorderWrapper"],div[data-testid="stExpander"],div[data-baseweb="select"],button,input{border-radius:0!important}
.stButton>button{background:#b4ff00;color:#0a0d0b;border:0;font-weight:800}
h1,h2,h3{letter-spacing:.03em}
a{color:#b4ff00!important}
.brand{border-left:5px solid #b4ff00;padding:10px 18px;background:#151c16;margin-bottom:15px}
.brand h1{margin:0;color:white;font-size:2.2rem}
.brand b{color:#b4ff00}
.kicker{font-size:.75rem;color:#b4ff00;font-weight:800;letter-spacing:.18em}
.warning{border-left:4px solid #f04444;padding:12px;background:#27191a}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="brand"><div class="kicker">ALPINE WEATHER / MOUNTAIN SAFETY</div><h1>MT<b>BLANC</b>-VCMM</h1><div>VERBIER · 4 VALLÉES · CHAMONIX · MEGÈVE · CORRIDOR ALPIN</div></div>', unsafe_allow_html=True)

@st.cache_data(ttl=600, show_spinner=False)
def forecast(lat, lon, elevation, model):
    params = {'latitude':lat,'longitude':lon,'elevation':elevation,
              'hourly':'temperature_2m,relative_humidity_2m,precipitation,snowfall,snow_depth,wind_speed_10m,wind_gusts_10m,wind_direction_10m,freezing_level_height,weather_code',
              'current':'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_gusts_10m,weather_code',
              'timezone':'Europe/Zurich','forecast_days':3}
    if model != 'Automatique': params['models']=model
    r=requests.get('https://api.open-meteo.com/v1/forecast',params=params,timeout=18)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=300, show_spinner=False)
def radar_frames():
    r=requests.get('https://api.rainviewer.com/public/weather-maps.json',timeout=10)
    r.raise_for_status()
    d=r.json()
    frames=d.get('radar',{}).get('past',[])
    return d.get('host','https://tilecache.rainviewer.com'),frames

with st.sidebar:
    st.header('PARAMÈTRES')
    region=st.selectbox('Secteur', ['4 Vallées','Corridor alpin','Chamonix','Megève','Aoste','Léman','Tous'])
    available=[k for k,v in LOCATIONS.items() if region=='Tous' or v[3]==region]
    place=st.selectbox('Point météo',available)
    lat,lon,natural,area=LOCATIONS[place]
    st.caption(f'Altitude indicative du lieu : {natural} m')
    use_natural=st.checkbox('Altitude du lieu (automatique)',value=True)
    altitude=st.slider('Altitude cible (m)',500,4000,max(500,min(4000,round(natural/50)*50)),50,disabled=use_natural)
    target=natural if use_natural else altitude
    model_label=st.selectbox('Modèle météo', ['Automatique','ICON Europe','AROME France'],help='La disponibilité dépend du fournisseur et de la zone.')
    model={'Automatique':'Automatique','ICON Europe':'icon_eu','AROME France':'meteofrance_arome_france'}[model_label]
    radar_on=st.checkbox('Radar des précipitations (RainViewer)',value=True)
    st.caption('Les coordonnées des points sont indicatives. Les données sont des prévisions de modèle, pas des mesures sur piste.')

st.markdown(f'### {place.upper()}  ·  {target:,} M'.replace(',', ' '))
try:
    data=forecast(lat,lon,target,model)
    current=data.get('current',{})
    cols=st.columns(4)
    for col,label,key,unit in zip(cols,['TEMPÉRATURE','VENT 10 M','RAFALES','PRÉCIPITATIONS'],['temperature_2m','wind_speed_10m','wind_gusts_10m','precipitation'],['°C','km/h','km/h','mm']):
        val=current.get(key)
        col.metric(label, f'{val} {unit}' if val is not None else '—')
    st.caption(f"Source : Open-Meteo · Modèle demandé : {model_label} · Altitude modèle renvoyée : {data.get('elevation','?')} m · Actualisation des données : {current.get('time','non disponible')} (heure locale)")
except Exception as e:
    data=None
    st.error(f'Prévisions indisponibles pour cette combinaison de paramètres : {e}. Essayez « Automatique ».')

tab_map,tab_hour,tab_webcams,tab_safety=st.tabs(['CARTE + RADAR','PRÉVISIONS 72 H','WEBCAMS','SÉCURITÉ MONTAGNE'])
with tab_map:
    m=folium.Map(location=[46.01,6.94],zoom_start=9,tiles='OpenTopoMap',control_scale=True)
    for name,(la,lo,el,zone) in LOCATIONS.items():
        if region!='Tous' and zone!=region:continue
        folium.CircleMarker([la,lo],radius=6 if name==place else 4,color='#b4ff00' if name==place else '#f04444',fill=True,fill_opacity=.95,
                            popup=folium.Popup(f'<b>{html.escape(name)}</b><br>{el} m · {html.escape(zone)}',max_width=240),tooltip=name).add_to(m)
    if radar_on:
        try:
            host,frames=radar_frames()
            if frames:
                frame=frames[-1]
                tile=f"{host}{frame['path']}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
                folium.TileLayer(tiles=tile,attr='RainViewer',name='Radar RainViewer (dernière image)',overlay=True,control=True,opacity=.7).add_to(m)
                st.caption('Radar : dernière image passée disponible, non une prévision. Couverture et latence variables.')
            else:st.info('Radar momentanément indisponible.')
        except Exception:st.warning('Impossible de charger la couche radar pour le moment.')
    folium.LayerControl().add_to(m)
    st_folium(m,height=570,use_container_width=True,returned_objects=[])
    st.caption('Cliquez sur les points pour identifier les secteurs. Sélectionnez un point dans le panneau latéral pour afficher ses prévisions.')
with tab_hour:
    if data and 'hourly' in data:
        h=pd.DataFrame(data['hourly'])
        h['time']=pd.to_datetime(h['time'])
        h=h.rename(columns={'time':'Heure','temperature_2m':'Température °C','precipitation':'Précipitations mm','snowfall':'Neige cm','snow_depth':'Hauteur neige m','wind_speed_10m':'Vent km/h','wind_gusts_10m':'Rafales km/h','freezing_level_height':'Isotherme 0 °C m','relative_humidity_2m':'Humidité %'})
        st.line_chart(h.set_index('Heure')[['Température °C']],height=230)
        st.line_chart(h.set_index('Heure')[['Vent km/h','Rafales km/h']],height=230)
        st.dataframe(h[['Heure','Température °C','Précipitations mm','Neige cm','Vent km/h','Rafales km/h','Isotherme 0 °C m','Humidité %']],hide_index=True,use_container_width=True)
        st.download_button('Télécharger les prévisions CSV',h.to_csv(index=False).encode('utf-8-sig'),file_name=f"mtblanc_vcmm_{place.lower().replace(' ','_')}.csv",mime='text/csv')
    else:st.info('Aucune donnée horaire chargée.')
with tab_webcams:
    st.info('Annuaire de liens externes vers des webcams : les images en direct ne sont pas intégrées ni vérifiées automatiquement.')
    for title,url in [
        ('Verbier / 4 Vallées','https://verbier4vallees.ch/'),
        ('Chamonix Mont-Blanc','https://www.chamonix.com/'),
        ('Megève','https://www.megeve-tourisme.fr/'),
        ('Évasion Mont-Blanc','https://www.evasionmontblanc.com/'),
        ('Courmayeur','https://www.courmayeurmontblanc.it/'),
        ('MétéoSuisse','https://www.meteosuisse.admin.ch/')]:
        st.markdown(f'**{title}** — [Site officiel / chercher « webcams »]({url})')
with tab_safety:
    st.markdown('<div class="warning"><b>IMPORTANT</b> — Outil de préparation, pas un dispositif d’alerte, de dispatch ou de décision de secours certifié. Vérifiez toujours les bulletins officiels et les observations terrain.</div>',unsafe_allow_html=True)
    st.markdown('**Bulletins officiels** : [SLF Suisse](https://www.slf.ch/fr/bulletin-davalanches-et-situation-nivologique/) · [Météo-France montagne](https://meteofrance.com/meteo-montagne) · [MétéoSuisse](https://www.meteosuisse.admin.ch/) · [Météo région Vallée d’Aoste](https://cf.regione.vda.it/)')
    st.markdown('**Briefing pisteurs / hors-piste**')
    for item in ['Dernier bulletin d’avalanche consulté','Vent et rafales observés sur les crêtes','Évolution de l’isotherme 0 °C','Neige récente et transport par le vent','Visibilité et couverture nuageuse','État des remontées et fermetures officielles','Communication et moyens de secours vérifiés']:
        st.checkbox(item,key='check_'+item)
    st.caption('En cas d’urgence, contactez les services de secours locaux. Ne prenez pas de décision de sécurité sur la seule base de cette application.')

st.divider()
st.caption('MTBLANC-VCMM · Version Streamlit V6 · Open-Meteo / OpenTopoMap / RainViewer. L’ajustement d’altitude par 50 m n’équivaut pas à une résolution réelle de 50 m. Les observations, modèles et radars peuvent diverger.')
