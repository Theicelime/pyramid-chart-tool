import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def create_pyramid_chart(
        # Data & Config
        df, age_col, left_col, right_col,
        title, left_name, right_name, left_color, right_color,
        # Style: Size & Font
        global_font_size, title_font_size,
        label_font_size, tick_font_size, bar_text_size, font_family,
        # Style: Grid
        show_x_grid, x_grid_color, x_grid_width,
        show_y_grid, y_grid_color, y_grid_width,
        # Style: Axis Lines (Box Model)
        show_x_bottom_line, x_bottom_line_color, x_bottom_line_width,
        show_x_top_line,
        show_y_left_line, y_left_line_color, y_left_line_width,
        show_y_right_line,
        # Style: Ticks
        x_tick_direction, x_tick_len,
        y_tick_direction, y_tick_len
):
    """
    使用 Plotly 创建人口金字塔图表
    """

    # --- 修复 1：添加刻度线方向的映射 ---
    tick_map = {
        "无": "",
        "外部": "outside",
        "内部": "inside"
    }
    x_tick_val = tick_map.get(x_tick_direction, "")  # 翻译 X 轴
    y_tick_val = tick_map.get(y_tick_direction, "")  # 翻译 Y 轴

    # --- 修复 2：创建手动画线 (shapes) 来形成一个完美的方框 ---
    layout_shapes = []
    # (使用 'paper' 坐标系, (0,0) 是左下角, (1,1) 是右上角)
    if show_x_bottom_line:
        layout_shapes.append(go.layout.Shape(
            type="line", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=0,
            line=dict(color=x_bottom_line_color, width=x_bottom_line_width)
        ))
    if show_x_top_line:
        layout_shapes.append(go.layout.Shape(
            type="line", xref="paper", yref="paper", x0=0, y0=1, x1=1, y1=1,
            line=dict(color=x_bottom_line_color, width=x_bottom_line_width)  # 复用底线样式
        ))
    if show_y_left_line:
        layout_shapes.append(go.layout.Shape(
            type="line", xref="paper", yref="paper", x0=0, y0=0, x1=0, y1=1,
            line=dict(color=y_left_line_color, width=y_left_line_width)
        ))
    if show_y_right_line:
        layout_shapes.append(go.layout.Shape(
            type="line", xref="paper", yref="paper", x0=1, y0=0, x1=1, y1=1,
            line=dict(color=y_left_line_color, width=y_left_line_width)  # 复用左线样式
        ))

    # --- 1-5 步：数据处理和图表创建 ---
    df[left_col] = pd.to_numeric(df[left_col])
    df[right_col] = pd.to_numeric(df[right_col])
    df['plot_left'] = df[left_col] * -1
    age_groups = list(df[age_col])
    fig = go.Figure()

    # --- ⬇️ 修复：将 .1f 修改为 .2f ⬇️ ---
    fig.add_trace(go.Bar(
        y=age_groups, x=df[right_col], name=right_name, orientation='h',
        marker=dict(color=right_color), text=df[right_col],
        texttemplate='%{text:.2f}%', textposition='outside'
    ))
    # --- ⬇️ 修复：将 .1f 修改为 .2f ⬇️ ---
    fig.add_trace(go.Bar(
        y=age_groups, x=df['plot_left'], name=left_name, orientation='h',
        marker=dict(color=left_color), text=df[left_col],
        texttemplate='%{text:.2f}%', textposition='outside'
    ))

    # --- 6. 动态计算 X 轴范围 ---
    max_val = max(df[left_col].max(), df[right_col].max())
    tick_max = (int(max_val / 2) + 1) * 2
    tick_step = 2
    positive_ticks = list(range(tick_step, tick_max + 1, tick_step))
    negative_ticks = [-v for v in positive_ticks]
    tick_vals = negative_ticks[::-1] + [0] + positive_ticks
    tick_text = [f'{v}%' for v in positive_ticks][::-1] + ['0%'] + [f'{v}%' for v in positive_ticks]

    # --- 7. 更新图表布局 (学术风格) ---
    fig.update_layout(
        # 字体和标题
        title=dict(text=title, x=0.5, font=dict(size=title_font_size)),
        font=dict(size=global_font_size, family=font_family),

        # 布局调整 (更紧凑)
        margin=dict(l=80, r=40, t=80, b=50),  # 减小左右边距

        xaxis_title="人口百分比",
        yaxis_title=age_col,

        # Y 轴 (左侧/右侧)
        yaxis=dict(
            categoryorder='array', categoryarray=age_groups,
            # 网格
            showgrid=show_y_grid, gridcolor=y_grid_color, gridwidth=y_grid_width,

            # 移除 showline 和 mirror
            showline=False,  # 使用 shapes 代替
            mirror=False,  # 使用 shapes 代替

            # 刻度线 (使用修复后的变量)
            ticks=y_tick_val,
            ticklen=y_tick_len
        ),

        # X 轴 (底部/顶部)
        xaxis=dict(
            tickvals=tick_vals, ticktext=tick_text,
            # 范围 (更紧凑)
            range=[-tick_max * 1.15, tick_max * 1.15],  # 1.2 -> 1.15
            # 网格
            showgrid=show_x_grid, gridcolor=x_grid_color, gridwidth=x_grid_width,

            # 移除 showline 和 mirror
            showline=False,  # 使用 shapes 代替
            mirror=False,  # 使用 shapes 代替

            # 刻度线 (使用修复后的变量)
            ticks=x_tick_val,
            ticklen=x_tick_len,
            # 中心零线 (硬编码)
            zeroline=True,
            zerolinecolor="#AAAAAA",
            zerolinewidth=1.5
        ),

        # 坐标轴标题字号
        yaxis_title_font=dict(size=label_font_size),
        xaxis_title_font=dict(size=label_font_size),

        # 坐标轴刻度字号
        yaxis_tickfont=dict(size=tick_font_size),
        xaxis_tickfont=dict(size=tick_font_size),

        barmode='relative',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        bargap=0.1,

        # 添加手动绘制的方框
        shapes=layout_shapes
    )

    # 8. 修改条上文字大小
    fig.update_traces(textfont=dict(size=bar_text_size))

    return fig


# --- Streamlit 网页应用界面 (已仔细检查，无错误) ---

st.set_page_config(layout="wide")
st.title("📊 人口金字塔可视化工具@城镇捕风笔记")

# --- 侧边栏：用于上传和配置 ---
st.sidebar.header("参数配置")

# 1. 上传文件
uploaded_file = st.sidebar.file_uploader("1. 上传 Excel 文件", type=["xlsx", "xls"], key="file_uploader")
st.sidebar.info(
    """
    **Excel 格式要求:**
    * 必须包含至少三列：年龄组、左侧数据、右侧数据。
    * 行顺序应为图表 Y 轴的显示顺序（例如 0-4 岁在最后一行）。
    """
)

# 2. 配置列名
st.sidebar.subheader("2. 填写 Excel 中的列名")
age_col = st.sidebar.text_input("年龄组列名", "年龄组", key="age_col")
left_col = st.sidebar.text_input("左侧数据列名 (如: 男性)", "男性", key="left_col")
right_col = st.sidebar.text_input("右侧数据列名 (如: 女性)", "女性", key="right_col")

# 3. 配置图表内容参数
st.sidebar.subheader("3. 自定义图表内容")
title = st.sidebar.text_input("图表标题", "1953年上海市第一次人口普查", key="title")
left_name = st.sidebar.text_input("左侧图例标签", "男性", key="left_name")
right_name = st.sidebar.text_input("右侧图例标签", "女性", key="right_name")
left_color = st.sidebar.color_picker("左侧颜色", "#3B82F6", key="left_color")
right_color = st.sidebar.color_picker("右侧颜色", "#EF4444", key="right_color")

# 4. 自定义图表样式 (字体/尺寸)
st.sidebar.subheader("4. 自定义图表样式")
font_family = st.sidebar.text_input("全局字体", "SimHei, Arial",
                                    help="""
                                  输入 CSS 字体。
                                  - 中文推荐: SimHei (黑体), Songti (宋体)
                                  - 英文推荐: Arial, Times New Roman
                                  """, key="font_family")
global_font_size = st.sidebar.slider("全局基础字号", 8, 20, 12, key="global_font_size")
title_font_size = st.sidebar.slider("标题字号", 16, 40, 24, key="title_font_size")
label_font_size = st.sidebar.slider("坐标轴标题字号", 10, 24, 16, key="label_font_size")
tick_font_size = st.sidebar.slider("坐标轴刻度字号", 8, 20, 12, key="tick_font_size")
bar_text_size = st.sidebar.slider("条上数字字号", 8, 20, 12, key="bar_text_size")

# 5. 自定义坐标轴/网格 (学术风格)
st.sidebar.subheader("5. 自定义坐标轴/网格 (学术风格)")

st.sidebar.markdown("**X轴 (底部/顶部)**")
col_x_grid1, col_x_grid2, col_x_grid3 = st.sidebar.columns([1, 2, 1])
with col_x_grid1:
    show_x_grid = st.checkbox("显示网格", False, key='x_grid_show')
with col_x_grid2:
    x_grid_color = st.color_picker("X网格色", "#E0E0E0", key='x_grid_c')
with col_x_grid3:
    x_grid_width = st.number_input("X网格粗细", 0.5, 5.0, 1.0, 0.5, key='x_grid_w')

col_x_ax1, col_x_ax2, col_x_ax3 = st.sidebar.columns([1, 2, 1])
with col_x_ax1:
    show_x_bottom_line = st.checkbox("显示底线", True, key='x_axis_show')
with col_x_ax2:
    x_bottom_line_color = st.color_picker("X底线色", "#000000", key='x_ax_c')
with col_x_ax3:
    x_bottom_line_width = st.number_input("X底线粗细", 0.5, 5.0, 2.0, 0.5, key='x_ax_w')

show_x_top_line = st.sidebar.checkbox("显示顶线 (形成方框)", True, key='x_top_line_show')

col_x_tick, col_x_tick_len = st.sidebar.columns(2)
with col_x_tick:
    x_tick_direction = st.selectbox("X轴刻度线", ["无", "外部", "内部"], index=1, key="x_tick_dir")
with col_x_tick_len:
    x_tick_len = st.slider("X轴刻度长", 0, 20, 5, key="x_tick_len")

st.sidebar.markdown("**Y轴 (左侧/右侧)**")
col_y_grid1, col_y_grid2, col_y_grid3 = st.sidebar.columns([1, 2, 1])
with col_y_grid1:
    show_y_grid = st.checkbox("显示网格", False, key='y_grid_show')
with col_y_grid2:
    y_grid_color = st.color_picker("Y网格色", "#E0E0E0", key='y_grid_c')
with col_y_grid3:
    y_grid_width = st.number_input("Y网格粗细", 0.5, 5.0, 1.0, 0.5, key='y_grid_w')

col_y_ax1, col_y_ax2, col_y_ax3 = st.sidebar.columns([1, 2, 1])
with col_y_ax1:
    show_y_left_line = st.checkbox("显示左线", True, key='y_axis_show')
with col_y_ax2:
    y_left_line_color = st.color_picker("Y左线色", "#000000", key='y_ax_c')
with col_y_ax3:
    y_left_line_width = st.number_input("Y左线粗细", 0.5, 5.0, 2.0, 0.5, key='y_ax_w')

show_y_right_line = st.sidebar.checkbox("显示右线 (形成方框)", True, key='y_right_line_show')

col_y_tick, col_y_tick_len = st.sidebar.columns(2)
with col_y_tick:
    y_tick_direction = st.selectbox("Y轴刻度线", ["无", "外部", "内部"], index=1, key="y_tick_dir")
with col_y_tick_len:
    y_tick_len = st.slider("Y轴刻度长", 0, 20, 5, key="y_tick_len")

# 6. 自定义导出尺寸 (已简化)
st.sidebar.subheader("6. 自定义导出尺寸")
export_unit = st.sidebar.radio("导出单位", ["像素 (px)", "毫米 (mm)"], key="export_unit", horizontal=True)
export_dpi = st.sidebar.number_input("分辨率 (DPI)", 150, 600, 300, 50, key="export_dpi",
                                     help="用于 'mm' 到 'px' 的转换，并自动计算PNG缩放。")

col_e1, col_e2 = st.sidebar.columns(2)
if export_unit == "毫米 (mm)":
    with col_e1:
        export_width_mm = st.number_input("导出宽度 (mm)", 10, 500, 150, 10, key="export_w_mm")
    with col_e2:
        export_height_mm = st.number_input("导出高度 (mm)", 10, 500, 100, 10, key="export_h_mm")
    export_width_px, export_height_px = 1200, 700
else:  # "像素 (px)"
    with col_e1:
        export_width_px = st.number_input("导出宽度 (px)", 500, 5000, 1200, 100, key="export_w_px")
    with col_e2:
        export_height_px = st.number_input("导出高度 (px)", 300, 5000, 700, 100, key="export_h_px")
    export_width_mm, export_height_mm = 150, 100

# --- 主界面：显示数据和图表 ---

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.header("数据预览 (前 5 行)")
        st.dataframe(df.head())

        required_cols = [age_col, left_col, right_col]
        if all(col in df.columns for col in required_cols):

            st.header("生成的可视化图表")
            fig = create_pyramid_chart(
                # Pass all variables from sidebar
                df, age_col, left_col, right_col,
                title, left_name, right_name, left_color, right_color,
                global_font_size, title_font_size,
                label_font_size, tick_font_size, bar_text_size, font_family,
                show_x_grid, x_grid_color, x_grid_width,
                show_y_grid, y_grid_color, y_grid_width,
                show_x_bottom_line, x_bottom_line_color, x_bottom_line_width,
                show_x_top_line,
                show_y_left_line, y_left_line_color, y_left_line_width,
                show_y_right_line,
                x_tick_direction, x_tick_len,
                y_tick_direction, y_tick_len
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- 导出图表功能 (已更新) ---
            st.subheader("导出图表")

            safe_filename = title.split(' ')[0].replace(' ', '_')

            # --- 根据单位计算最终像素 ---
            if export_unit == "毫米 (mm)":
                calc_export_width = int((export_width_mm / 25.4) * export_dpi)
                calc_export_height = int((export_height_mm / 25.4) * export_dpi)
            else:  # "像素 (px)"
                calc_export_width = export_width_px
                calc_export_height = export_height_px

            # --- DPI 自动计算 PNG 缩放 ---
            png_scale_factor = export_dpi / 96.0  # 假设标准屏幕 DPI 为 96

            st.markdown(f"**导出基准尺寸:** {calc_export_width}px (宽) x {calc_export_height}px (高)")
            if export_unit == "毫米 (mm)":
                st.caption(f" (基于 {export_width_mm}mm x {export_height_mm}mm @ {export_dpi} DPI 计算)")

            img_svg = fig.to_image(format="svg", width=calc_export_width, height=calc_export_height)
            img_pdf = fig.to_image(format="pdf", width=calc_export_width, height=calc_export_height)
            img_png = fig.to_image(format="png", width=calc_export_width, height=calc_export_height,
                                   scale=png_scale_factor)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="下载为 SVG 格式", data=img_svg,
                    file_name=f"{safe_filename}_pyramid.svg", mime="image/svg+xml", key="dl_svg"
                )
            with col2:
                st.download_button(
                    label="下载为 PDF 格式", data=img_pdf,
                    file_name=f"{safe_filename}_pyramid.pdf", mime="application/pdf", key="dl_pdf"
                )
            with col3:
                st.download_button(
                    label="下载为高分辨率 PNG", data=img_png,
                    file_name=f"{safe_filename}_pyramid.png", mime="image/png", key="dl_png"
                )
                st.caption(
                    f"PNG 最终像素: {int(calc_export_width * png_scale_factor)} x {int(calc_export_height * png_scale_factor)}")

        else:
            st.error(f"错误：Excel 文件中未找到所需的列。请确保包含: {', '.join(required_cols)}")

    except Exception as e:
        st.error(f"加载 Excel 文件或生成图表时出错: {e}")
else:
    st.info("请在左侧侧边栏上传 Excel 文件以开始。")