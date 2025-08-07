import streamlit as st
from main import search_spotify_tracks

st.title("🎵 Spotify楽曲検索＆埋め込み再生（モダンUI）")

with st.form("music_search_form"):
    query = st.text_input("検索したい楽曲名またはアーティスト名", "夜に駆ける")
    submitted = st.form_submit_button("検索")

if submitted:
    with st.spinner("Spotifyで検索中..."):
        result = search_spotify_tracks(query)
    if 'error' in result:
        st.error(f"エラー: {result['error']}")
    else:
        tracks = result.get('results', [])
        st.success(result.get('message', f"{len(tracks)}件見つかりました。"))
        if tracks:
            st.subheader("検索結果プレビュー（上位5件）")
            for i, track in enumerate(tracks[:5], 1):
                cols = st.columns([1, 2, 2])
                # アートワーク
                with cols[0]:
                    if track.get('album_art'):
                        st.image(track['album_art'], width=80)
                # 曲情報
                with cols[1]:
                    st.markdown(f"**{track['name']}**")
                    st.caption(f"アーティスト: {track['artist']}")
                    st.caption(f"アルバム: {track['album']}")
                    st.caption(f"リリース: {track['release_date']}")
                    if track.get('spotify_url'):
                        st.markdown(f"[Spotifyで開く]({track['spotify_url']})")
                # 埋め込みプレイヤー
                with cols[2]:
                    url = track.get('spotify_url')
                    if url and 'track/' in url:
                        track_id = url.split('track/')[-1].split('?')[0]
                        embed_url = f"https://open.spotify.com/embed/track/{track_id}"
                        st.markdown(
                            f'''
                            <div style="border-radius:16px; overflow:hidden; background:#191414; width:320px; height:80px;">
                              <iframe src="{embed_url}" width="320" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius:16px; background:#191414;"></iframe>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                st.markdown("---")
        else:
            st.warning("該当する楽曲が見つかりませんでした。") 