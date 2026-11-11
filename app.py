"""MTBLANC-VCMM V10 — tableau de bord freeride, Streamlit Cloud."""
import datetime as dt
import html
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title='MTBLANC-VCMM | Freeride Snow', page_icon='🏔️', layout='wide', initial_sidebar_state='collapsed')
TZ = ZoneInfo('Europe/Zurich')
LIME, RED, BLUE = '#baff45', '#ff5663', '#59c8ff'
POINTS = {
 'Verbier':(46.096,7.228,1500,'4 Vallées'), 'Mont Fort':(46.081,7.318,3329,'4 Vallées'),
 'Les Attelas':(46.103,7.270,2727,'4 Vallées'), 'La Tzoumaz':(46.145,7.234,1500,'4 Vallées'),
 'Nendaz':(46.183,7.294,1400,'4 Vallées'), 'Veysonnaz':(46.196,7.335,1350,'4 Vallées'),
 'Thyon 2000':(46.178,7.388,2000,'4 Vallées'), 'Bruson':(46.066,7.216,1100,'4 Vallées'),
 'Martigny':(46.102,7.073,471,'Entre les massifs'), 'Trient':(46.056,6.995,1300,'Entre les massifs'),
 'Vallorcine':(46.034,6.933,1260,'Chamonix'), 'Le Tour':(46.003,6.946,1460,'Chamonix'),
 'Argentière':(45.982,6.927,1250,'Chamonix'), 'Grands Montets':(45.956,6.961,3275,'Chamonix'),
 'Chamonix':(45.924,6.869,1035,'Chamonix'), 'Brévent':(45.933,6.838,2525,'Chamonix'),
 'Les Houches':(45.890,6.799,1000,'Chamonix'), 'Saint-Gervais':(45.893,6.712,850,'Megève'),
 'Megève':(45.857,6.617,1110,'Megève'), 'Mont d’Arbois':(45.865,6.653,1833,'Megève'),
 'Rochebrune':(45.835,6.643,1754,'Megève'), 'Côte 2000':(45.829,6.675,2000,'Megève'),
 'Combloux':(45.897,6.644,960,'Megève'), 'Les Contamines':(45.821,6.728,1164,'Megève'),
 'Praz-sur-Arly':(45.837,6.573,1030,'Megève'), 'Courmayeur':(45.793,6.969,1224,'Entre les massifs'),
}
GROUPS = ['Tous les secteurs','4 Vallées','Chamonix','Megève','Entre les massifs']

st.markdown('''<style>
:root{--lime:#baff45;--bg:#090d0b;--panel:#18211c;--line:#43594a}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:#f9fff9!important}
[data-testid="stHeader"]{background:var(--bg)!important}
.block-container{max-width:1180px!important;padding:1.1rem .85rem 4rem!important}
.stApp p,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp li{color:#f8fff8!important}
[data-testid="stCaptionContainer"] p{color:#d0dfd2!important}
[data-testid="stMarkdownContainer"] a{color:var(--lime)!important;text-decoration:underline!important}
[data-testid="stButton"] button,[data-testid="stLinkButton"] a{background:#203127!important;color:#fff!important;border:2px solid #718976!important;border-radius:0!important;font-weight:750!important;min-height:45px!important}
[data-testid="stButton"] button:hover,[data-testid="stLinkButton"] a:hover{border-color:var(--lime)!important;color:var(--lime)!important}
[data-testid="stDownloadButton"] button{background:#203127!important;color:white!important;border:2px solid #718976!important;border-radius:0!important}
[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{color:white!important}
[data-baseweb="select"]>div{background:#18251d!important;color:#fff!important;border:1px solid #9db39e!important;border-radius:0!important}
[data-baseweb="select"] span,[data-baseweb="select"] input{color:#fff!important;-webkit-text-fill-color:#fff!important}
[data-baseweb="popover"] *,[role="listbox"] *{color:#151a15!important}
[data-testid="stSlider"] p{color:white!important}
[data-testid="stAlert"]{background:#1b2c20!important;border:1px solid #77937b!important;border-radius:0!important}
[data-testid="stAlert"] *{color:#fff!important}
[data-testid="stExpander"]{border:1px solid #5d7664!important;border-radius:0!important}
[data-testid="stMetric"]{background:#18211c!important;border:1px solid #6c806e!important;border-radius:0!important;padding:12px!important}
[data-testid="stMetric"] *{color:white!important;-webkit-text-fill-color:white!important}
[data-testid="stMetricValue"]{font-size:1.6rem!important}
[data-testid="stDataFrame"]{border-radius:0!important}
header{visibility:visible}
.brand{background:#162019;border-left:6px solid var(--lime);padding:15px 18px;margin-bottom:15px}
.brand small{color:var(--lime);letter-spacing:.11em;font-weight:850;font-size:.75rem}
.brand h1{font-size:clamp(1.7rem,5vw,2.65rem);margin:7px 0!important;color:#fff!important;line-height:1.1}
.brand h1 b{color:var(--lime)}
.brand .sub{color:#dce9dc;font-size:.83rem}
.section{border-left:4px solid var(--lime);padding-left:12px;margin:19px 0 10px;font-size:1.15rem;font-weight:850;color:#fff}
.snowcard{background:#17211b;border:1px solid #536c59;padding:14px;margin:0 0 12px}
.snowcard .place{font-weight:850;color:white;font-size:1.05rem}
.snowcard .amount{font-size:2rem;color:var(--lime);font-weight:900;line-height:1.35}
.snowcard .detail{font-size:.82rem;color:#e0ece1;line-height:1.6}
.note{border-left:4px solid #59c8ff;background:#13222b;padding:11px 13px;color:white;margin:10px 0}
.warning{border-left:4px solid #ff5663;background:#2a191b;padding:11px 13px;color:white;margin:10px 0}
.legend{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0;color:#fff;font-size:.88rem}
.legend span{display:inline-flex;gap:6px;align-items:center}
.legend i{width:13px;height:13px;display:inline-block}
@media(max-width:650px){.block-container{padding-left:.65rem!important;padding-right:.65rem!important}.brand{padding:12px}.snowcard .amount{font-size:1.7rem}}
</style>''',unsafe_allow_html=True)

@st.cache_data(ttl=900,show_spinner=False)
def forecast(name,altitude=None):
    lat,lon,natural,_=POINTS[name]
    params={'latitude':lat,'longitude':lon,'elevation':natural if altitude is None else altitude,
            'hourly':'temperature_2m,precipitation,rain,snowfall,snow_depth,freezing_level_height,wind_speed_10m,wind_gusts_10m',
            'forecast_days':4,'timezone':'Europe/Zurich'}
    r=requests.get('https://api.open-meteo.com/v1/forecast',params=params,timeout=14)
    r.raise_for_status(); data=r.json()
    frame=pd.DataFrame(data['hourly'])
    frame['time']=pd.to_datetime(frame['time'])
    for col in ['temperature_2m','precipitation','rain','snowfall','snow_depth','freezing_level_height','wind_speed_10m','wind_gusts_10m']:
        frame[col]=pd.to_numeric(frame[col],errors='coerce')
    return frame, data.get('generationtime_ms'), data.get('elevation')

def upcoming(df,hours=24):
    now=pd.Timestamp(dt.datetime.now(TZ).replace(tzinfo=None))
    rows=df[df.time>=now.floor('h')].head(hours)
    return rows if len(rows) else df.head(hours)

def fmt(value,unit='',dec=0):
    return '—' if pd.isna(value) else f'{value:.{dec}f}{unit}'

def place_summary(name,hours=24):
    df,_,_=forecast(name)
    sub=upcoming(df,hours)
    snow=sub['snowfall'].sum(min_count=1)
    rain=sub['rain'].sum(min_count=1)
    freeze=sub['freezing_level_height'].median()
    return {'name':name,'snow':snow,'rain':rain,'freeze':freeze,'data':df}

def selected_names(group):
    return list(POINTS) if group=='Tous les secteurs' else [k for k,v in POINTS.items() if v[3]==group]

@st.cache_data(ttl=180,show_spinner=False)
def radar_frames():
    r=requests.get('https://api.rainviewer.com/public/weather-maps.json',timeout=10);r.raise_for_status()
    j=r.json(); frames=j.get('radar',{}).get('past',[])
    return j.get('host','https://tilecache.rainviewer.com'),frames

st.markdown('<div class="brand"><small>FREERIDE / SNOW FORECAST / ALPES</small><h1>MT<b>BLANC</b>-VCMM</h1><div class="sub">VERBIER · 4 VALLÉES · CHAMONIX · MEGÈVE · CORRIDOR ALPIN</div></div>',unsafe_allow_html=True)
page=st.radio('Navigation',['❄️ Neige à venir','🗺️ Carte neige / pluie','🏔️ Par station','📷 Webcams & sécurité'],horizontal=True,label_visibility='collapsed')

if page=='❄️ Neige à venir':
    st.markdown('<div class="section">OÙ ET QUAND VA-T-IL NEIGER ?</div>',unsafe_allow_html=True)
    period=st.segmented_control('Période',['12 h','24 h','48 h','72 h'],default='24 h')
    hours=int(period.split()[0])
    group=st.selectbox('Secteur',['Tous les secteurs','4 Vallées','Chamonix','Megève','Entre les massifs'])
    names=selected_names(group)
    with st.spinner('Chargement des prévisions de neige…'):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda n: (n,place_summary(n,hours)),names))
    good=[r for _,r in results if r]
    good.sort(key=lambda r: (-r['snow'] if pd.notna(r['snow']) else float('inf')))
    st.caption(f'Classement des chutes de neige prévues sur {period} à l’altitude de chaque point. Modèle Open-Meteo, pas une mesure de neige au sol.')
    if good:
        for i in range(0,len(good),3):
            cols=st.columns(min(3,len(good)-i))
            for col,r in zip(cols,good[i:i+3]):
                name=r['name'];alt=POINTS[name][2]
                col.markdown(f'<div class="snowcard"><div class="place">{html.escape(name)} · {alt} m</div><div class="amount">{fmt(r["snow"]," cm",1)}</div><div class="detail">❄️ Neige prévue · {period}<br>🌧️ Pluie : {fmt(r["rain"]," mm",1)}<br>🌡️ Isotherme 0 °C médian : {fmt(r["freeze"]," m")}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="note">Les valeurs de neige sont des prévisions de chute de neige, pas de l’épaisseur de poudreuse disponible. Le vent, le tassement, l’exposition et les avalanches peuvent fortement changer les conditions.</div>',unsafe_allow_html=True)

elif page=='🗺️ Carte neige / pluie':
    st.markdown('<div class="section">CARTE DES PRÉCIPITATIONS — PLUIE OU NEIGE</div>',unsafe_allow_html=True)
    st.caption('Carte topographique interactive : les points sont colorés selon la prévision pour une heure sélectionnée. Le fond reste zoomable et déplaçable.')
    group=st.selectbox('Afficher le secteur',GROUPS)
    names=selected_names(group)
    now=dt.datetime.now(TZ).replace(minute=0,second=0,microsecond=0)
    offset=st.slider('Échéance prévue (heures après maintenant)',0,72,12,3)
    target=(now+dt.timedelta(hours=offset)).replace(tzinfo=None)
    show_radar=st.toggle('Afficher aussi le radar observé (historique récent)',value=False)
    st.markdown('<div class="legend"><span><i style="background:#59c8ff"></i>Neige prévue</span><span><i style="background:#ff6370"></i>Pluie prévue</span><span><i style="background:#b18cff"></i>Mixte prévu</span><span><i style="background:#baff45"></i>Peu ou pas de précipitations</span></div>',unsafe_allow_html=True)
    st.caption(f'Heure cible : {target:%d/%m %H:%M} (heure suisse). Le type de précipitation est déduit des champs pluie et neige du modèle, pas du radar.')
    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes=list(pool.map(lambda n: (n,forecast(n)),names))
    center=[46.02,6.95]
    if group=='4 Vallées':center=[46.14,7.29]
    if group=='Chamonix':center=[45.96,6.90]
    if group=='Megève':center=[45.86,6.67]
    m=folium.Map(location=center,zoom_start=10 if group=='Tous les secteurs' else 11,tiles=None,control_scale=True,prefer_canvas=True)
    folium.TileLayer('OpenStreetMap',name='Plan',control=True).add_to(m)
    folium.TileLayer(tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='© OpenTopoMap / OpenStreetMap / SRTM',name='Relief topographique',control=True,max_zoom=17).add_to(m)
    for name,(df,_,_) in outcomes:
        point=df.iloc[(df['time']-target).abs().argmin()]
        snow=float(point.snowfall) if pd.notna(point.snowfall) else 0
        rain=float(point.rain) if pd.notna(point.rain) else 0
        color='#b18cff' if snow>0.05 and rain>0.05 else BLUE if snow>0.05 else RED if rain>0.05 else LIME
        lat,lon,alt,_=POINTS[name]
        popup=f'<div style="font:14px Arial;min-width:170px"><b>{html.escape(name)} · {alt} m</b><hr>❄️ Neige : {snow:.1f} cm/h<br>🌧️ Pluie : {rain:.1f} mm/h<br>🌡️ Temp. : {fmt(point.temperature_2m," °C",1)}<br>💨 Rafales : {fmt(point.wind_gusts_10m," km/h")}</div>'
        folium.CircleMarker([lat,lon],radius=7,weight=2,color='#0b1010',fill=True,fill_color=color,fill_opacity=.95,tooltip=f'{name} : {snow:.1f} cm/h neige · {rain:.1f} mm/h pluie',popup=folium.Popup(popup,max_width=270)).add_to(m)
    if show_radar:
        try:
            host,frames=radar_frames()
            if frames:
                frame=frames[-1]
                ts=dt.datetime.fromtimestamp(frame['time'],TZ)
                folium.raster_layers.TileLayer(tiles=f'{host}{frame["path"]}/256/{{z}}/{{x}}/{{y}}/2/1_1.png',attr='RainViewer',name=f'Radar observé {ts:%H:%M}',overlay=True,control=True,opacity=.58,max_zoom=18).add_to(m)
                st.caption(f'Radar observé : {ts:%d/%m %H:%M}. Le radar ne distingue pas directement la pluie de la neige au sol.')
            else:st.warning('Aucune image radar disponible actuellement.')
        except Exception:st.warning('Radar indisponible actuellement. La carte de prévisions reste accessible.')
    folium.LayerControl(collapsed=True).add_to(m)
    st_folium(m,height=510,width=None,key='snowmap',returned_objects=[],use_container_width=True)
    st.markdown('<div class="note">Le radar montre des précipitations observées, tandis que les points bleus/rouges représentent des prévisions à l’heure choisie. Ne les confonds pas.</div>',unsafe_allow_html=True)

elif page=='🏔️ Par station':
    st.markdown('<div class="section">PRÉVISION FREERIDE PAR STATION ET ALTITUDE</div>',unsafe_allow_html=True)
    group=st.selectbox('Massif',['4 Vallées','Chamonix','Megève','Entre les massifs'])
    name=st.selectbox('Station / sommet',selected_names(group))
    alt=st.slider('Altitude étudiée',500,4000,int(round(POINTS[name][2]/50)*50),50)
    df,_,elevation=forecast(name,alt)
    h=upcoming(df,48)
    snow24=upcoming(df,24)['snowfall'].sum(min_count=1)
    rain24=upcoming(df,24)['rain'].sum(min_count=1)
    c1,c2=st.columns(2)
    c1.metric('❄️ Neige prévue / 24 h',fmt(snow24,' cm',1))
    c2.metric('🌧️ Pluie prévue / 24 h',fmt(rain24,' mm',1))
    c3,c4=st.columns(2)
    c3.metric('🌡️ Isotherme 0 °C (médiane / 24 h)',fmt(upcoming(df,24)['freezing_level_height'].median(),' m'))
    c4.metric('💨 Rafales max / 24 h',fmt(upcoming(df,24)['wind_gusts_10m'].max(),' km/h'))
    snowy=h[h['snowfall']>=.1]
    if len(snowy):
        st.success(f'Prochaine neige prévue : {snowy.iloc[0].time:%d/%m à %H:%M} · {fmt(snowy.iloc[0].snowfall," cm/h",1)}')
    else:st.info('Pas de chute de neige significative prévue sur les prochaines 48 heures à cette altitude.')
    st.markdown('<div class="section">PROCHAINES 48 HEURES — LECTURE SIMPLE</div>',unsafe_allow_html=True)
    table=h[['time','snowfall','rain','temperature_2m','wind_gusts_10m']].copy()
    table.columns=['Heure','Neige cm/h','Pluie mm/h','Température °C','Rafales km/h']
    table['Heure']=table['Heure'].dt.strftime('%d/%m %H:%M')
    st.dataframe(table,hide_index=True,use_container_width=True,height=330)
    st.caption(f'Altitude demandée : {alt} m · Altitude du modèle renvoyée : {fmt(elevation," m")}. Le pas de 50 m correspond à un ajustement vertical du modèle, pas à une mesure tous les 50 m.')
    st.markdown('<div class="warning">La présence de neige fraîche ne garantit pas un terrain skiable ni sûr. Vérifie le bulletin avalanche, le vent, la visibilité et les observations locales avant toute sortie hors-piste.</div>',unsafe_allow_html=True)

else:
    st.markdown('<div class="section">WEBCAMS ET CONDITIONS OFFICIELLES</div>',unsafe_allow_html=True)
    st.caption('Liens lisibles vers les sites des stations et les bulletins officiels. Les webcams ne sont pas intégrées sans autorisation du fournisseur.')
    links=[('Webcams Verbier 4 Vallées','https://verbier4vallees.ch/'),('Webcams Chamonix','https://www.chamonix.com/'),('Webcams Megève','https://www.megeve-tourisme.fr/'),('Webcams Les Houches','https://www.chamonix.com/'),('Webcams Nendaz','https://www.nendaz.ch/'),('Webcams Saint-Gervais','https://www.saintgervais.com/'),('Bulletin avalanche SLF (Suisse)','https://www.slf.ch/fr/bulletin-davalanches-et-situation-nivologique/'),('Météo-France Montagne','https://meteofrance.com/meteo-montagne'),('MétéoSuisse','https://www.meteosuisse.admin.ch/'),('Avalanches Vallée d’Aoste','https://bollettinovalanghe.regione.vda.it/')]
    for label,url in links:
        st.link_button('↗ '+label,url,use_container_width=True)
    st.markdown('<div class="warning">MTBLANC-VCMM est un outil de préparation freeride, pas un service de sécurité certifié. Les bulletins officiels d’avalanches et les consignes locales font autorité.</div>',unsafe_allow_html=True)

st.divider()
st.caption('MTBLANC-VCMM V10 · Prévisions : Open-Meteo · Carte : OpenStreetMap / OpenTopoMap · Radar optionnel : RainViewer. Les modèles ne sont pas actualisés toutes les minutes. Les prévisions peuvent être erronées en haute montagne.')
