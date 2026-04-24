"""
update_dashboard.py
═══════════════════════════════════════════════════════════════
WX Dashboard – Script de Atualização de Dados
═══════════════════════════════════════════════════════════════

COMO USAR:
  1. Coloque os arquivos Excel exportados na pasta 'data/' deste repositório
  2. Execute: python update_dashboard.py
  3. O arquivo data.json será atualizado automaticamente
  4. Faça commit e push para o GitHub → o dashboard atualiza!

ARQUIVOS ESPERADOS na pasta data/:
  - eventos.xlsx     → relatório de eventos (Pipefy / sistema de solicitações)
  - csat.xlsx        → relatório de CSAT (satisfação pós-evento)

DEPENDÊNCIAS:
  pip install pandas openpyxl
"""

import pandas as pd
import json
import math
import os
import glob
import sys
from datetime import datetime

# ──────────────────────────────────────────────────────
# LOCALIZAR ARQUIVOS
# ──────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT = os.path.join(os.path.dirname(__file__), 'data.json')

def find_file(data_dir, keywords, label):
    """Procura arquivo Excel por palavras-chave no nome."""
    for kw in keywords:
        matches = glob.glob(os.path.join(data_dir, f'*{kw}*.xlsx'), recursive=False)
        matches += glob.glob(os.path.join(data_dir, f'*{kw}*.xls'), recursive=False)
        if matches:
            print(f'  ✅ {label}: {os.path.basename(matches[0])}')
            return matches[0]
    print(f'  ⚠️  {label}: não encontrado em {data_dir}')
    print(f'       Coloque um arquivo .xlsx com "{keywords[0]}" no nome.')
    return None

# ──────────────────────────────────────────────────────
# COLUNAS (compatível com export do Pipefy / sistema WX)
# ──────────────────────────────────────────────────────
EV_RENAME = {
    'Fase atual': 'status',
    '🇧🇷Em qual país será realizado seu evento? // 🇺🇲 In which country will your event be held? // 🇲🇽  ¿En qué país se realizará el evento?': 'country',
    '🇧🇷 Qual a sua BU? // 🇺🇲 What is your BU? // 🇲🇽  Cuál es su BU?': 'bu',
    '🇧🇷Quantos dias será o seu evento? // 🇺🇲 How long will your event last? // 🇲🇽  Cuánto durará su evento?': 'days',
    '🇧🇷 Data do evento. // 🇺🇲 Date of the event. // 🇲🇽  Fecha del evento.': 'date',
    '🇧🇷 Em qual HQ do Brasil você gostaria de fazer seu evento? // 🇺🇲 In which HQ in Brazil would you like to hold your event? // 🇲🇽 ¿En cuál sede de Brasil te gustaría hacer tu evento?': 'hq_brazil',
    '🇧🇷 Em qual local do México você gostaria de fazer seu evento? // 🇺🇲 In which location in Mexico would you like to hold your event? // 🇲🇽 ': 'location_mx',
    '🇧🇷 A data do evento é na mesma semana da sua BU no escritório? // 🇺🇲  Is the event taking place during the same week that your BU will be at the office? // 🇲🇽  El evento se realizará durante la misma semana en que tu BU estará en la oficina?': 'same_week_bu',
    '🇧🇷 Quantidade de pessoas. // 🇺🇲  The number of people. // 🇲🇽  Número de personas.': 'people',
    '🇧🇷 O evento terá participantes externos? // 🇺🇲  Will the event have external participants? // 🇲🇽  El evento tendrá participantes externos?': 'has_external',
    '🇧🇷 Quantos participantes são externos? // How many participants are external? // 🇲🇽 ¿Cuántos participantes externos habrá?': 'external_count',
    '🇧🇷 Horário de Início. // 🇺🇲  Time to begin. // 🇲🇽  Hora de inicio.': 'start_time',
    '🇧🇷 Horário de término. // 🇺🇲  End time. // 🇲🇽  Hora de término.': 'end_time',
    '🇧🇷 Seu evento é confidencial? // 🇺🇲  Is your event classified? // 🇲🇽 ¿Su evento es confidencial?': 'confidential',
}

CSAT_RENAME = {
    'Fase atual': 'rating',
    'Criado em': 'created_at',
    'Date and time of the event // Data e horário do evento': 'event_date',
    'In which country did your event happened ? // Em qual país ocorreu seu evento?': 'country',
    'Where did the event happen? // Onde aconteceu o evento?': 'space_bra',
    'MX - Where did the event happen? // Onde aconteceu o evento?': 'space_mx',
    'Colômbia - Where did the event happen? // Onde aconteceu o evento?': 'space_col',
    '1. How satisfied were you with the space where the event took place?? // Quão satisfeito (a) você ficou com o espaço onde aconteceu o evento?': 'score_space',
    '2. How satisfied were you with the catering? Quão satisfeito (a) você ficou com o catering?': 'score_catering',
    '3. How satisfied were you with the audio and video operation/service? // Quão satisfeito (a) você ficou com o funcionamento/serviço de audio e vídeo?': 'score_av',
    '4. Overall, how would you rate your experience with this event? // Em geral, como você classifica sua experiência com este evento?': 'score_overall',
}

SCORE_MAP = {
    '😃 Amei! // I loved it!': 5, '😃Amei! // I loved it!': 5,
    '🙂 Adorei // I liked it very much': 4,
    '😐 Foi OK // It was OK': 3,
    "🙁 Gostei não // It wasn't good": 2,
    '😟 Ruim, hein?! // It was bad, huh?!': 1,
}

# ──────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────
def norm_status(s):
    if pd.isna(s): return 'Outros'
    s = str(s)
    if 'Conclu' in s: return 'Concluído'
    if 'Cancelado' in s: return 'Cancelado'
    if 'Confirmado' in s: return 'Confirmado'
    if 'Em Analise' in s: return 'Em Análise'
    if 'Solicitação' in s or 'Recebida' in s: return 'Solicitado'
    if 'sala de reunião' in s: return 'Redirecionado'
    return s

def extract_hour(t):
    if pd.isna(t): return None
    t = str(t).strip()
    try:
        if 'AM' in t or 'PM' in t:
            return pd.to_datetime(t, format='%I:%M %p').hour
        elif ':' in t:
            return int(t.split(':')[0])
    except:
        pass
    return None

def clean_json(obj):
    """Recursively clean NaN/numpy types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(i) for i in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    try:
        import numpy as np
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return None if math.isnan(float(obj)) else float(obj)
    except ImportError:
        pass
    return obj

# ──────────────────────────────────────────────────────
# PROCESS EVENTS
# ──────────────────────────────────────────────────────
def process_events(filepath):
    print('\n📋 Processando eventos...')
    df = pd.read_excel(filepath)

    # Rename columns (use partial match for flexibility)
    rename_map = {}
    for col in df.columns:
        for old, new in EV_RENAME.items():
            if old in col or col in old:
                rename_map[col] = new
                break
    df = df.rename(columns=rename_map)

    # Parse dates & derive fields
    df['date'] = pd.to_datetime(df.get('date', pd.Series()), errors='coerce')
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['day_name'] = df['date'].dt.strftime('%A')
    df['people'] = pd.to_numeric(df.get('people', pd.Series()), errors='coerce')

    df['status'] = df.get('status', pd.Series()).apply(norm_status)
    df['country'] = df.get('country', pd.Series()).fillna('Não informado')
    df['has_external'] = df.get('has_external', pd.Series()).apply(
        lambda x: 'Sim' if pd.notna(x) and 'Sim' in str(x) else 'Não'
    )
    df['hour'] = df.get('start_time', pd.Series()).apply(extract_hour)

    # Filter valid years (adjust range as needed)
    df = df[df['year'].between(2022, datetime.now().year + 1)]
    print(f'   → {len(df)} eventos carregados')

    years = sorted(df['year'].dropna().unique().astype(int).tolist())
    countries = sorted(df['country'].dropna().unique().tolist())

    def agg(df): return df.to_dict('records')

    return {
        'total': int(len(df)),
        'years': years,
        'countries': countries,
        'status': agg(df.groupby('status').size().reset_index(name='count')),
        'country_year': agg(df.groupby(['country','year']).size().reset_index(name='count')),
        'country_month': agg(df.groupby(['country','year','month_num']).size().reset_index(name='count')),
        'hq': agg(df[df['country']=='Brasil'].groupby('hq_brazil').size().reset_index(name='count')),
        'hq_year': agg(df[df['country']=='Brasil'].groupby(['hq_brazil','year']).size().reset_index(name='count')),
        'day': agg(df.groupby('day_name').size().reset_index(name='count').sort_values(
            'day_name', key=lambda s: s.map({'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6})
        )),
        'hour': agg(df.dropna(subset=['hour']).groupby('hour').size().reset_index(name='count').sort_values('hour')),
        'people_space': agg(df[df['country']=='Brasil'].groupby('hq_brazil')['people'].mean().round(1).reset_index(name='avg_people')),
        'external': agg(df.groupby(['year','has_external']).size().reset_index(name='count')),
        'monthly': agg(df.groupby(['year','month_num']).size().reset_index(name='count')),
        'bu': agg(df.groupby('bu').size().reset_index(name='count').sort_values('count', ascending=False).head(20)),
        'people_year': agg(df.groupby('year')['people'].agg(['mean','median']).round(1).reset_index().rename(columns={'mean':'avg','median':'median'})),
    }

# ──────────────────────────────────────────────────────
# PROCESS CSAT
# ──────────────────────────────────────────────────────
def process_csat(filepath):
    print('\n⭐ Processando CSAT...')
    df = pd.read_excel(filepath)

    rename_map = {}
    for col in df.columns:
        for old, new in CSAT_RENAME.items():
            if old in col or col in old:
                rename_map[col] = new
                break
    df = df.rename(columns=rename_map)

    df['event_date'] = pd.to_datetime(df.get('event_date', pd.Series()), errors='coerce')
    df['year'] = df['event_date'].dt.year
    df['month'] = df['event_date'].dt.month
    df['country'] = df.get('country', pd.Series()).fillna('Brasil')

    for field in ['rating','score_space','score_catering','score_av','score_overall']:
        col = field + '_n'
        df[col] = df.get(field, pd.Series()).map(SCORE_MAP)

    df = df[df['year'].between(2022, datetime.now().year + 1)]
    df_valid = df[~df.get('rating', pd.Series('',index=df.index)).isin(['Não Aplicavél','Feedbacks'])]
    print(f'   → {len(df_valid)} avaliações válidas carregadas')

    def agg(df): return df.to_dict('records')

    return {
        'total': int(len(df_valid)),
        'years': sorted(df['year'].dropna().unique().astype(int).tolist()),
        'rating_dist': agg(df_valid.groupby('rating').size().reset_index(name='count')),
        'year': agg(df.groupby('year').agg(
            count=('rating_n','count'), avg_overall=('rating_n','mean'),
            avg_space=('score_space_n','mean'), avg_catering=('score_catering_n','mean'), avg_av=('score_av_n','mean')
        ).round(2).reset_index()),
        'country': agg(df.groupby('country').agg(count=('rating_n','count'), avg_overall=('rating_n','mean')).round(2).reset_index()),
        'space': agg(df[df['country']=='Brasil'].groupby('space_bra').agg(
            count=('rating_n','count'), avg_overall=('rating_n','mean'), avg_space=('score_space_n','mean')
        ).round(2).reset_index().sort_values('count',ascending=False)),
        'monthly': agg(df.groupby(['year','month']).agg(count=('rating_n','count'), avg=('rating_n','mean')).round(2).reset_index()),
    }

# ──────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────
def main():
    print('═' * 55)
    print('  WX Dashboard – Atualização de Dados')
    print('═' * 55)

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f'\n📁 Pasta criada: {DATA_DIR}')
        print('   Coloque os arquivos Excel lá e execute novamente.')
        sys.exit(0)

    print(f'\n🔍 Buscando arquivos em: {DATA_DIR}')

    ev_file  = find_file(DATA_DIR, ['evento', 'event', 'wx'],  'Eventos')
    csat_file = find_file(DATA_DIR, ['csat', 'satisfa', 'relatrio', 'relatorio'], 'CSAT')

    if not ev_file or not csat_file:
        print('\n❌ Arquivos obrigatórios não encontrados. Renomeie ou coloque na pasta data/.')
        sys.exit(1)

    ev_data   = process_events(ev_file)
    csat_data = process_csat(csat_file)

    data = clean_json({'ev': ev_data, 'csat': csat_data})

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f'\n✅ data.json atualizado! ({size_kb:.1f} KB)')
    print(f'   Eventos: {ev_data["total"]:,} | CSAT: {csat_data["total"]:,}')
    print('\n📤 Próximo passo: git add data.json && git commit -m "chore: atualiza dados" && git push')
    print('   O GitHub Pages vai atualizar automaticamente em ~1 minuto.\n')

if __name__ == '__main__':
    main()
