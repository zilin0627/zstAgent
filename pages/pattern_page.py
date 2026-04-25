import streamlit as st


FILTER_OPTIONS = ["全部", "动物纹", "人物纹", "植物纹 / 天体纹", "组合纹", "几何纹 / 花卉纹"]
SCAN_FILTER_OPTIONS = ["全部", "龙纹类", "花纹类", "盘型类", "树纹类"]


def _inject_css():
    st.markdown(
        """
        <style>
        /* 列内图片：固定高度 + contain，完整显示，暖色填充空白 */
        [data-testid="column"] [data-testid="stImage"] img {
            height: 200px !important;
            width: 100% !important;
            object-fit: contain !important;
            background: #f7f2eb !important;
            border-radius: 6px !important;
            padding: 6px !important;
            display: block;
        }
        /* 灯箱弹窗：还原为自然尺寸，不受列内 CSS 影响 */
        [data-baseweb="modal"] img,
        [role="dialog"] img,
        [data-testid="stFullScreenFrame"] img {
            height: auto !important;
            max-height: 85vh !important;
            width: auto !important;
            max-width: 90vw !important;
            object-fit: contain !important;
            background: transparent !important;
            padding: 0 !important;
            border-radius: 4px !important;
        }
        /* 板块标题 */
        .sec-hd {
            padding: 10px 18px 9px;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .sec-hd-title {
            font-size: 15px;
            font-weight: 700;
            color: #fff;
            letter-spacing: 0.3px;
        }
        .sec-hd-sub {
            font-size: 12px;
            color: rgba(255,255,255,0.78);
            margin-top: 3px;
        }
        /* 卡片间距底线 */
        .card-divider {
            border: none;
            border-top: 1px solid #f0e8dc;
            margin: 10px 0 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sec_header(title: str, subtitle: str, color: str):
    sub = f'<div class="sec-hd-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="sec-hd" style="background:{color};">'
        f'<div class="sec-hd-title">{title}</div>{sub}</div>',
        unsafe_allow_html=True,
    )


def _render_pattern_card(*, item, guide_page: str, cocreate_page: str, apply_cocreate_preset):
    try:
        st.image(item["image"], use_container_width=True)
    except Exception:
        st.caption("图片暂无法显示")

    st.markdown(f"**{item['name']}**")
    st.caption(f"{item['category']}  ·  {' / '.join(item['tags'])}")

    if item.get("keywords"):
        st.caption("·  ".join(item["keywords"]))

    with st.expander("图案特征", expanded=False):
        if item.get("summary"):
            st.write(item["summary"])
        st.markdown(f"**常见载体**：{item.get('carrier', '—')}")
        for feature in item.get("features", []):
            st.markdown(f"- {feature}")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("查看", key=f"view_{item['name']}", use_container_width=True):
            st.session_state["current_page"] = guide_page
            st.session_state["preset_prompt"] = f"介绍{item['name']}的特点和常见用法"
            st.rerun()
    with btn_col2:
        if st.button("去设计", key=f"design_{item['name']}", use_container_width=True):
            apply_cocreate_preset(
                item["name"],
                f"{item['name']}的现代转化",
                "海报视觉",
                "传统庄重",
                f"保留{item['name']}的核心视觉特征",
            )
            st.session_state["current_page"] = cocreate_page
            st.rerun()


def _render_scan_card(*, item, idx: int, guide_page: str, cocreate_page: str, apply_cocreate_preset):
    scan_key = str(idx)
    try:
        st.image(item["image"], use_container_width=True)
    except Exception:
        st.caption("图片暂无法显示")

    st.markdown(f"**{item['name']}**")
    st.caption(f"类别：{item['category']}  ·  图谱：{item['related_pattern']}")
    if item.get("caption"):
        st.write(item["caption"])

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("查看关联", key=f"scan_view_{scan_key}", use_container_width=True):
            st.session_state["preset_prompt"] = (
                f"介绍{item['related_pattern']}，结合真实绣片说明构图和工艺特点"
            )
            st.session_state["current_page"] = guide_page
            st.rerun()
    with btn_col2:
        if st.button("去设计", key=f"scan_design_{scan_key}", use_container_width=True):
            apply_cocreate_preset(
                item["related_pattern"],
                f"基于{item['name']}的现代转化",
                "海报视觉",
                "传统庄重",
                f"结合扫图《{item['name']}》的特征：{item.get('caption', '')}",
            )
            st.session_state["current_page"] = cocreate_page
            st.rerun()


def render_pattern_page(
    *,
    guide_page: str,
    cocreate_page: str,
    pattern_items: list[dict],
    pattern_scan_items: list[dict],
    apply_cocreate_preset,
    render_section_heading,
):
    _inject_css()

    st.title("纹样图谱")
    st.caption("知识入口页：先从母题和真实扫图建立视觉观察，再进入智能导览或设计工作台。")
    st.markdown(
        '<hr style="border:none;border-top:2px solid #c9a227;margin:6px 0 16px;">',
        unsafe_allow_html=True,
    )

    # 概览指标
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("图谱类型", "5 类", help="动物、人物、组合、植物/天体、几何/花卉")
    m2.metric("图谱卡片", str(len(pattern_items)))
    m3.metric("扫图样本", str(len(pattern_scan_items)))
    m4.metric("联通方式", "导览 + 设计", help="每张卡片可直接跳转导览或工作台")

    st.markdown("---")

    # ── 板块 1：典型纹样图谱 ──────────────────────────────
    _sec_header(
        "典型纹样图谱",
        "先按类型筛选，再逐一查看 · 点「查看」进导览，点「去设计」预填工作台",
        "#1a5c4f",
    )

    selected_filter = st.radio(
        "按类型筛选", FILTER_OPTIONS, horizontal=True, key="pattern_filter"
    )
    visible_items = [
        item
        for item in pattern_items
        if selected_filter == "全部" or item["category"] == selected_filter
    ]

    if not visible_items:
        st.info("当前筛选条件下暂无纹样卡片。")
    else:
        for start in range(0, len(visible_items), 4):
            cols = st.columns(4, gap="medium")
            for col, item in zip(cols, visible_items[start : start + 4]):
                with col:
                    _render_pattern_card(
                        item=item,
                        guide_page=guide_page,
                        cocreate_page=cocreate_page,
                        apply_cocreate_preset=apply_cocreate_preset,
                    )
            st.write("")  # 行间距

    st.markdown("---")

    # ── 板块 2：真实刺绣扫图 ──────────────────────────────
    _sec_header(
        "真实刺绣扫图",
        "查看关联 → 跳到智能导览 · 去设计 → 直接预填设计工作台",
        "#1e3a5f",
    )

    selected_scan_filter = st.radio(
        "按类别浏览", SCAN_FILTER_OPTIONS, horizontal=True, key="pattern_scan_filter"
    )
    visible_scan_items = [
        item
        for item in pattern_scan_items
        if selected_scan_filter == "全部" or item["category"] == selected_scan_filter
    ]

    if visible_scan_items:
        for start in range(0, len(visible_scan_items), 4):
            cols = st.columns(4, gap="medium")
            for offset, (col, item) in enumerate(
                zip(cols, visible_scan_items[start : start + 4])
            ):
                with col:
                    _render_scan_card(
                        item=item,
                        idx=start + offset,
                        guide_page=guide_page,
                        cocreate_page=cocreate_page,
                        apply_cocreate_preset=apply_cocreate_preset,
                    )
            st.write("")
    else:
        st.info("当前筛选条件下暂无扫图样本。")
