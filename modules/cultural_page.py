import streamlit as st


def render_cultural_page(*, cultural_page: str, render_section_heading):
    st.title(cultural_page)
    st.caption("展示侗族织绣纹样如何被转化为当代文创产品、展陈物料与品牌视觉。")
    st.divider()

    showcase_cols = st.columns(3, gap="large")
    showcase_data = [
        ("服饰配件", "围巾、披肩、手袋、首饰包装", "强调纹样与穿戴体验的结合。"),
        ("家居生活", "靠垫、桌旗、灯罩、收纳布艺", "让纹样进入日常空间，形成温和而稳定的使用场景。"),
        ("礼品周边", "明信片、笔记本、包装礼盒、纪念品", "适合博物馆、展览与文旅商店场景。"),
    ]
    for col, item in zip(showcase_cols, showcase_data):
        title, subtitle, desc = item
        with col:
            st.markdown(f"#### {title}")
            st.caption(subtitle)
            st.write(desc)

    st.divider()
    lower_cols = st.columns(2, gap="large")
    with lower_cols[0]:
        render_section_heading("展示建议", "如果后续补内容，可以优先接这些板块")
        st.markdown("- 案例卡片：作品图、用途、材料、设计说明。")
        st.markdown("- 对比视图：传统纹样原型 vs 现代转化结果。")
        st.markdown("- 标签系统：按应用类别、色彩、节庆属性筛选。")
    with lower_cols[1]:
        render_section_heading("评估维度", "用于说明文创设计是否有效")
        st.markdown("- 是否保留核心纹样识别度")
        st.markdown("- 是否适配现代审美与使用场景")
        st.markdown("- 是否体现文化来源与叙事")
        st.markdown("- 是否具备传播与商业转化潜力")
