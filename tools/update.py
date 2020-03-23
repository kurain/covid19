import json
import pandas as pd
import requests
import datetime

from pathlib import Path


# color scheme
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# regions and prefectures
region_to_prefecture = {
    '北海道': ['北海道'],
    '東北': ['青森県', '岩手県', '秋田県', '宮城県', '山形県', '福島県'],
    '関東': ['茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県'],
    '中部': ['新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県'],
    '近畿': ['三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県'],
    '中国': ['鳥取県', '島根県', '岡山県', '広島県', '山口県'],
    '四国': ['徳島県', '香川県', '愛媛県', '高知県'],
    '九州沖縄': ['福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
}
prefectures = []
for k,v in region_to_prefecture.items():
    prefectures += v

# From Toyo Keizai
SOURCE_URL= 'https://raw.githubusercontent.com/kaz-ogiwara/covid19/master/data/individuals.csv'

raw = pd.read_csv(SOURCE_URL)

raw['date'] = pd.to_datetime(raw.apply(lambda r: f"{r['確定年']}-{r['確定月']:02d}-{r['確定日']:02d}", axis=1))
count_by_location = raw[['date', '居住地1','新No.']].pivot_table(index='date',columns='居住地1',values='新No.',aggfunc='count')

s = count_by_location.index[0]
t =  count_by_location.index[-1]
dummy = pd.DataFrame([[d, None] for d in pd.date_range(s, t)],columns=['date','dummy']).set_index('date')

count_by_location = dummy.join(count_by_location)
count_by_location = count_by_location.drop('dummy',axis=1)
count_by_location = count_by_location.fillna(0)

assert(len(count_by_location) == len(dummy))
assert(len(raw) == count_by_location.sum(axis=1).sum())


for region, prefs in region_to_prefecture.items():
    target = [e for e in prefs if e in count_by_location.columns]
    count_by_location[region] = count_by_location[target].sum(axis=1)


res = {
    'original_date' : {},
}
for location in count_by_location.columns:
    res['original_date'][location] = {
        'daily_count': list(count_by_location[location]),
        'cumulative': list(count_by_location[location].cumsum()),
    }
res['date'] = [d.isoformat() for d in count_by_location[location].index]
res['prefectures'] = prefectures

latest = count_by_location[set(count_by_location.columns) & set(prefectures)].cumsum().iloc[-1]
res['top10'] = list(latest.sort_values(ascending=False).index)[:10]

def tuple2css(t):
    return f'rgb({t[0]}, {t[1]}, {t[2]})'

res['colors'] = {p: tuple2css(tableau20[i%20]) for i, p in enumerate(prefectures)}
res['last_update'] = datetime.datetime.now().isoformat()

with open(Path(__file__).parent / '../docs/count_by_location.json', 'w') as f:
    json.dump(res, f)
