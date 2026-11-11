import datetime as dt
from zoneinfo import ZoneInfo
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

st.markdown("""<style>
:root{--neon:#baff35;--red:#ff565e;--ink:#080b09;--panel:#171d19}
.stApp,.main{background:#080b09!important;color:#fff!important}
[data-testid="stSidebar"]{background:#151b17!important}
[data-testid="stMetric"]{background:#171d19!important;border:2px solid #647266!important;padding:16px!important;border-radius:0!important}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *, [data-testid="stMetricValue"], [data-testid="stMetricValue"] *{color:#ffffff!important;opacity:1!important;-webkit-text-fill-color:#ffffff!important}
[data-testid="stMetricLabel"]{font-weight:750!important}
[data-testid="stMetricValue"]{font-weight:850!important}
[data-testid="stMetricDelta"] *{color:#baff35!important}
[data-testid="stMarkdownContainer"],.stApp p,.stApp label,.stApp h1,.stApp h2,.stApp h3{color:#f5f8f5}
[data-testid="stCaptionContainer"] p{color:#cbd8cd!important}
[data-testid="stVerticalBlockBorderWrapper"],div[data-testid="stExpander"],div[data-baseweb="select"],button,input,[data-testid="stTabs"] button{border-radius:0!important}
.stButton>button{background:#baff35!important;color:#070907!important;border:0!important;font-weight:800!important}
[data-baseweb="tab"]{color:#e8f1e8!important}
[data-baseweb="tab"][aria-selected="true"]{color:#baff35!important}
h1,h2,h3{letter-spacing:.025em}
a{color:#baff35!important}
.brand{border-left:6px solid #baff35;padding:15px 20px;background:#171d19;margin-bottom:15px}
.brand h1{margin:0;color:white;font-size:clamp(1.6rem,5vw,2.5rem)}
.brand b{color:#baff35}
.kicker{font-size:.78rem;color:#baff35;font-weight:800;letter-spacing:.13em}
.warning{border-left:5px solid #ff565e;padding:14px;background:#2c171a;color:white}
.radar-note{border-left:4px solid #baff35;background:#172019;padding:12px;color:white}
</style>""",unsafe_allow_html=True)
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


# Chaque source est interrogée séparément : aucun chiffre n'est inventé en cas d'échec.
MODELS_COMPARE = {
    'MétéoSuisse ICON-CH1 (~1 km)': 'meteoswiss_icon_ch1',
    'MétéoSuisse ICON-CH2 (~2 km)': 'meteoswiss_icon_ch2',
    'Météo-France AROME HD (~1,3 km)': 'meteofrance_arome_france_hd',
    'ECMWF IFS (~9 km)': 'ecmwf_ifs025',
}

@st.cache_data(ttl=900, show_spinner=False)
def model_comparison(lat, lon, altitude):
    import concurrent.futures
    def fetch(item):
        label, model_id = item
        params = {
            'latitude': lat, 'longitude': lon, 'elevation': altitude,
            'models': model_id, 'timezone': 'Europe/Zurich', 'forecast_days': 2,
            'hourly': 'temperature_2m,precipitation,wind_speed_10m,wind_gusts_10m',
        }
        try:
            r = requests.get('https://api.open-meteo.com/v1/forecast', params=params, timeout=16)
            r.raise_for_status()
            d = r.json()
            h = pd.DataFrame(d['hourly'])
            if h.empty or 'time' not in h:
                raise ValueError('Réponse horaire vide')
            h['time'] = pd.to_datetime(h['time'])
            h = h.set_index('time')
            return label, h, None
        except (requests.RequestException, ValueError, KeyError) as exc:
            return label, None, str(exc)[:160]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(fetch, MODELS_COMPARE.items()))

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
    model_label=st.selectbox('Modèle météo', ['Automatique','ICON Suisse CH1','ICON Suisse CH2','AROME France HD','ICON Europe','AROME France'],help='La disponibilité dépend du fournisseur et de la zone.')
    model={'Automatique':'Automatique','ICON Suisse CH1':'meteoswiss_icon_ch1','ICON Suisse CH2':'meteoswiss_icon_ch2','AROME France HD':'meteofrance_arome_france_hd','ICON Europe':'icon_eu','AROME France':'meteofrance_arome_france'}[model_label]
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

tab_map,tab_compare,tab_hour,tab_webcams,tab_safety=st.tabs(['CARTE + RADAR','COMPARAISON MODÈLES','PRÉVISIONS 72 H','WEBCAMS','SÉCURITÉ MONTAGNE'])
with tab_map:
    st.markdown('#### RADAR INTERACTIF — OBSERVATIONS')
    st.markdown('<div class="radar-note"><b>Zoom et déplacement conservés.</b> Choisis une image radar dans la chronologie. Les images RainViewer couvrent généralement une courte période récente : <b>48 h d’archives et les prévisions radar ne sont pas disponibles dans cette source gratuite</b>. La prévision horaire du modèle est présentée séparément plus bas.</div>',unsafe_allow_html=True)
    host,frames=None,[]
    if radar_on:
        try:
            host,frames=radar_frames()
        except requests.RequestException:
            st.warning('Radar RainViewer temporairement indisponible. La carte reste utilisable.')
    if frames:
        times=[dt.datetime.fromtimestamp(f['time'],tz=ZoneInfo('Europe/Zurich')).strftime('%d/%m %H:%M') for f in frames]
        selected_index=st.slider('Historique radar disponible · heure suisse',min_value=0,max_value=len(frames)-1,value=len(frames)-1,format='%d',help='Déplace le curseur pour consulter les images radar archivées par RainViewer.')
        st.caption(f'Image sélectionnée : {times[selected_index]} · {len(frames)} images disponibles, du {times[0]} au {times[-1]} (heure suisse).')
    else:
        selected_index=None
        if radar_on:st.info('Aucune image radar disponible pour le moment.')
    if 'map_view' not in st.session_state:
        st.session_state.map_view={'center':{'lat':46.01,'lng':6.94},'zoom':9}
    view=st.session_state.map_view
    m=folium.Map(location=[view['center']['lat'],view['center']['lng']],zoom_start=view['zoom'],tiles=None,control_scale=True,zoom_control=True,prefer_canvas=True)
    folium.TileLayer('OpenStreetMap',name='Plan',control=True).add_to(m)
    folium.TileLayer('OpenTopoMap',name='Relief topographique',control=True,show=True).add_to(m)
    for name,(la,lo,el,zone) in LOCATIONS.items():
        if region!='Tous' and zone!=region:continue
        folium.CircleMarker([la,lo],radius=7 if name==place else 4,color='#baff35' if name==place else '#ff565e',weight=2,fill=True,fill_opacity=.95,
                            popup=folium.Popup(f'<b>{html.escape(name)}</b><br>{el} m · {html.escape(zone)}',max_width=240),tooltip=name).add_to(m)
    if radar_on and selected_index is not None:
        frame=frames[selected_index]
        tile=f"{host}{frame['path']}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
        folium.TileLayer(tiles=tile,attr='RainViewer',name='Radar · image sélectionnée',overlay=True,control=True,show=True,opacity=.75,max_zoom=19,max_native_zoom=7).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    result=st_folium(m,height=560,use_container_width=True,key='main_radar_map',returned_objects=['center','zoom'])
    if result and result.get('center') and result.get('zoom') is not None:
        st.session_state.map_view={'center':result['center'],'zoom':result['zoom']}
    st.caption('La carte peut être agrandie et déplacée. À fort zoom, les pixels du radar deviennent plus gros : la résolution des mesures ne s’améliore pas. Si les tuiles ne chargent pas, désactive puis réactive le radar.')
    st.markdown('#### PRÉVISIONS DE PRÉCIPITATIONS — MODÈLE MÉTÉO')
    st.caption('Ce graphique représente les prévisions Open-Meteo au point et à l’altitude choisis, et non une animation de radar. Les données ne décrivent pas précisément chaque versant.')
    if data and data.get('hourly'):
        ph=pd.DataFrame(data['hourly'])
        ph['time']=pd.to_datetime(ph['time'])
        ph=ph[['time','precipitation','snowfall']].rename(columns={'time':'Heure','precipitation':'Pluie / précipitations (mm)','snowfall':'Neige (cm)'})
        st.line_chart(ph.set_index('Heure'),height=220)
        st.dataframe(ph,hide_index=True,use_container_width=True)
    else:
        st.info('Prévisions horaires indisponibles actuellement.')
with tab_compare:
    st.markdown('#### COMPARATEUR MULTIMODÈLE — VERBIER / CHAMONIX / MEGÈVE')
    st.info('Les modèles sont comparés pour le même point et la même altitude demandée. Le pas de 50 m est un ajustement vertical du modèle, et non une mesure à cette résolution. Les modèles peuvent partager des biais.')
    with st.spinner('Interrogation de MétéoSuisse, Météo-France et ECMWF…'):
        comparisons = model_comparison(lat, lon, target)
    valid = {label: frame for label, frame, error in comparisons if frame is not None}
    failed = [(label, error) for label, frame, error in comparisons if frame is None]
    if failed:
        st.warning('Sources indisponibles ou hors couverture : ' + '; '.join(label for label, _ in failed) + '. Elles ne sont pas incluses dans les statistiques.')
        with st.expander('Détails des erreurs de récupération'):
            for label, error in failed:
                st.write(f'{label} : {error}')
    if valid:
        variable = st.selectbox('Paramètre à comparer', [
            'Température (°C)', 'Précipitations (mm/h)', 'Vent à 10 m (km/h)', 'Rafales (km/h)'])
        key = {'Température (°C)': 'temperature_2m', 'Précipitations (mm/h)': 'precipitation',
               'Vent à 10 m (km/h)': 'wind_speed_10m', 'Rafales (km/h)': 'wind_gusts_10m'}[variable]
        joined = pd.concat({name: df[key] for name, df in valid.items() if key in df}, axis=1).sort_index()
        now = pd.Timestamp.now(tz='Europe/Zurich').tz_localize(None)
        joined = joined.loc[joined.index >= now.floor('h')].head(36)
        if not joined.empty:
            st.line_chart(joined, height=310)
            summary = pd.DataFrame(index=joined.index)
            summary['Médiane des modèles'] = joined.median(axis=1)
            summary['Minimum des modèles'] = joined.min(axis=1)
            summary['Maximum des modèles'] = joined.max(axis=1)
            summary['Écart max–min'] = summary['Maximum des modèles'] - summary['Minimum des modèles']
            st.markdown('**Fourchette intermodèle (prochaines 36 heures)**')
            st.dataframe(summary.round(1), use_container_width=True)
            st.download_button('Télécharger la comparaison CSV', joined.to_csv().encode('utf-8-sig'),
                               file_name='mtblanc_vcmm_comparaison_modeles.csv', mime='text/csv')
            st.caption('La médiane est un indicateur de comparaison, pas une prévision officiellement validée. Un faible écart entre modèles ne garantit pas la justesse, notamment en terrain complexe.')
        else:
            st.info('Aucune heure commune disponible pour le moment.')
    else:
        st.error('Aucun modèle n’a répondu. Réessayez plus tard ou changez de point.')
    st.markdown('**Sources :** [MétéoSuisse](https://www.meteosuisse.admin.ch/) · [Météo-France](https://meteofrance.com/) · [ECMWF](https://www.ecmwf.int/) · [Open-Meteo](https://open-meteo.com/)')
    st.caption('Pour les décisions opérationnelles, vérifier les mesures sur site, les alertes et les bulletins officiels. Les prévisions n’assurent pas la sécurité d’un itinéraire.')

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
st.caption('MTBLANC-VCMM · Version Streamlit V8 · Open-Meteo / OpenTopoMap / RainViewer. L’ajustement d’altitude par 50 m n’équivaut pas à une résolution réelle de 50 m. Les observations, modèles et radars peuvent diverger.')
