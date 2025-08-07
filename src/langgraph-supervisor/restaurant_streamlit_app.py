import streamlit as st
from main import (
    search_hotpepper_restaurants,
    search_google_maps_restaurants,
    show_googlemap_embed_streamlit
)
from collections import defaultdict
import re

def parse_budget(budget_str):
    if not budget_str or '円' not in budget_str:
        return (0, 999999)
    nums = [int(s.replace(',', '')) for s in re.findall(r'\d+', budget_str)]
    if '～' in budget_str and len(nums) == 2:
        return (nums[0], nums[1])
    elif '以下' in budget_str and nums:
        return (0, nums[0])
    elif '以上' in budget_str and nums:
        return (nums[0], 999999)
    elif len(nums) == 1:
        return (nums[0], nums[0])
    return (0, 999999)

def merge_restaurant_info(hp_list, gm_list):
    merged = []
    for hp in hp_list:
        best_match = None
        for gm in gm_list:
            # 店名が部分一致 or 住所が部分一致
            if (hp['name'] and gm['name'] and (hp['name'] in gm['name'] or gm['name'] in hp['name'])) or \
               (hp.get('address') and gm.get('address') and (hp['address'] in gm['address'] or gm['address'] in hp['address'])):
                best_match = gm
                break
        merged_info = hp.copy()
        if best_match:
            # Googleの評価や価格帯で補完
            if not merged_info.get('rating') or merged_info['rating'] == '評価なし':
                merged_info['rating'] = best_match.get('rating', merged_info.get('rating'))
            if not merged_info.get('budget') or merged_info['budget'] == '価格要問合せ':
                merged_info['budget'] = best_match.get('price_level', merged_info.get('budget'))
            merged_info['google_rating'] = best_match.get('rating')
            merged_info['google_price_level'] = best_match.get('price_level')
            merged_info['google_maps_url'] = best_match.get('google_maps_url')
        merged.append(merged_info)
    # Google側だけにある店も追加
    hp_names = set([r['name'] for r in hp_list])
    for gm in gm_list:
        if gm['name'] not in hp_names:
            merged.append(gm)
    return merged

def get_user_budget_range(budget):
    user_max = 999999
    user_min = 0
    user_nums = [int(s.replace(',', '')) for s in re.findall(r'\d+', budget)]
    if '以下' in budget and user_nums:
        user_max = user_nums[0]
    elif '～' in budget and len(user_nums) == 2:
        user_min = user_nums[0]
        user_max = user_nums[1]
    elif '以上' in budget and user_nums:
        user_min = user_nums[0]
        user_max = 999999
    elif user_nums:
        user_max = user_nums[0]
    return user_min, user_max

st.title("🍽️ レストラン検索（HotPepper+Google総合評価順）")

with st.form("search_form"):
    location = st.text_input("エリア名 (例: 大崎, 渋谷, 新宿)", "大崎")
    cuisine = st.text_input("ジャンル (例: 居酒屋, イタリアン, 中華)", "")
    budget = st.text_input("予算 (例: 3000円以下)", "")
    submitted = st.form_submit_button("検索")

if submitted:
    user_min, user_max = get_user_budget_range(budget) if budget else (0, 999999)
    with st.spinner("HotPepper・Google両方から検索中..."):
        hp_result = search_hotpepper_restaurants(location, cuisine, budget) if (location or cuisine or budget) else {"restaurants": []}
        gm_result = search_google_maps_restaurants(location, cuisine) if (location or cuisine) else {"restaurants": []}
    hp_list = hp_result.get("restaurants", [])
    gm_list = gm_result.get("restaurants", [])
    merged = merge_restaurant_info(hp_list, gm_list)
    # 価格帯でフィルタ
    filtered = []
    for r in merged:
        shop_min, shop_max = parse_budget(r.get('budget', ''))
        if shop_max < user_min or shop_min > user_max:
            continue
        filtered.append(r)
    # 総合スコア: rating（なければ0）- price_level（なければ0, 低いほど高評価）
    for r in filtered:
        try:
            rating = float(r.get('rating', 0)) if r.get('rating') and r.get('rating') != '評価なし' else 0.0
        except:
            rating = 0.0
        try:
            price = float(r.get('google_price_level', 0) or r.get('budget', 0))
        except:
            price = 0.0
        r['_score'] = rating - 0.1 * price  # 価格が高いほど少し減点
    filtered = sorted(filtered, key=lambda x: x['_score'], reverse=True)
    if not filtered:
        st.warning("該当するレストランが見つかりませんでした。")
    else:
        for i, r in enumerate(filtered, 1):
            name = r.get('name', '')
            rating = r.get('rating', '評価なし')
            budget = r.get('budget') or r.get('google_price_level') or '不明'
            genre = r.get('cuisine') or '不明'
            address = r.get('address') or '不明'
            st.markdown(f"**{i}. {name}**  ")
            st.caption(f"評価: {rating} | 予算: {budget} | ジャンル: {genre} | 住所: {address}")
            if r.get('google_maps_url'):
                st.markdown(f"[Googleマップで見る]({r['google_maps_url']})")
            if r.get('address'):
                show_googlemap_embed_streamlit(r['address'], title="Googleマッププレビュー")
            st.write("") 