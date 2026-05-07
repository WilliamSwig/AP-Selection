import streamlit as st

# 页面基础配置：设置标题与布局
st.set_page_config(page_title="AP选课系统", layout="centered")

# 强制通过 CSS 确保在任何主题下文字颜色均清晰（深灰色），避免白字问题
st.markdown("""
    <style>
    .stMarkdown, .stCheckbox, label, .stHeader { color: #1f2937 !important; }
    .stExpander { border: 1px solid #d1d5db !important; border-radius: 8px !important; margin-bottom: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 万科高中部 AP 项目选课系统")
st.info("提示：请根据最新教学大纲进行勾选。每个学科组必须至少选择一门课程。")

# --- 第一部分：个人档案 ---
st.subheader("一、学生基本信息")
c1, c2 = st.columns(2)
with c1:
    cn_name = st.text_input("中文姓名", placeholder="请填写")
    grade = st.selectbox("今年9月就读年级", ["G10", "G11", "G12"])
    country = st.text_input("拟申请国家")
with c2:
    en_name = st.text_input("英文姓名", placeholder="Firstname Lastname")
    class_name = st.text_input("行政班级")
    major = st.text_input("拟申请专业方向")

st.divider()

# --- 第二部分：核心课程数据录入 (基于最新图片更新) ---
course_structure = {
    "Group 1: Language A - 中文文学 (必修)": [
        "中文文学 2 (基础)", "中文文学 3 (基础)", "中文文学 4 (荣誉)"
    ],
    "Group 2: World Languages: English - 英语课程 (必修)": [
        "ESL 2 (基础)", "10年级英语 (荣誉)", "EFL 2 (荣誉)", "英语文学 2 (荣誉)",
        "ESL 3 (基础)", "英语文学 3 (荣誉)", 
        "AP 英语语言与写作 (荣誉)", "AP 英语语言与文学 (荣誉)",
        "英语文学 4 (荣誉)"
    ],
    "Group 3: Humanities - 人文科学 (必修1-2门)": [
        "预修AP商科 (基础)", "AP商科 (荣誉)", "AP 微观经济 (荣誉)", "AP 宏观经济 (荣誉)",
        "基础美国历史 (基础)", "AP 美国历史 (荣誉)", "AP 世界历史 (荣誉)",
        "预修AP心理学 (基础)", "AP 心理学 (荣誉)"
    ],
    "Group 4: Sciences - 科学 (必修1-2门)": [
        "AP 物理 1 (荣誉)", "AP 物理 C 力学 (荣誉)", "预修AP物理（力学） (基础)",
        "AP 物理 C 电磁 (荣誉)", "预修 AP 生物 (基础)", "AP 生物 (荣誉)",
        "预修 AP 化学 (基础)", "AP 化学 (荣誉)"
    ],
    "Group 5: Mathematics and Computer Science - 数学与计算机 (必修)": [
        "IG0580 2 (基础)", "IG0606 2 (基础)", "AP 预修微积分 (荣誉)",
        "AP 微积分 AB (荣誉)", "AP 微积分 BC (荣誉)", "AP 统计 (荣誉)",
        "线性代数 (荣誉)", "多元微积分 (荣誉)", "AP 计算机应用 (荣誉)"
    ],
    "Group 6: Arts - 艺术 (选修)": [
        "基础艺术 (基础)", "AP 艺术-2D (荣誉)", "AP 艺术-3D (荣誉)", 
        "AP 绘画 (荣誉)", "艺术鉴赏 (荣誉)", "音乐史 (荣誉)"
    ],
    "School cores - 校本核心课程": [
        "社团 (基础)", "体育&赛艇 (基础)", "职业规划 (基础)", 
        "升学指导 (基础)", "AP 研讨 (荣誉)", "AP 自由课题 (荣誉)"
    ]
}

# --- 第三部分：动态选课界面渲染 ---
st.subheader("二、学科组选课")
final_selections = {}

for g_title, courses in course_structure.items():
    # 使用折叠面板保持界面整洁
    with st.expander(f"📖 {g_title}", expanded=True):
        selected_list = []
        cols = st.columns(2)
        for idx, course_name in enumerate(courses):
            with cols[idx % 2]:
                if st.checkbox(course_name, key=f"sel_{course_name}"):
                    selected_list.append(course_name)
        final_selections[g_title] = selected_list

# --- 第四部分：底层逻辑冲突校验 ---
math_choices = final_selections["Group 5: Mathematics and Computer Science - 数学与计算机 (必修)"]
sci_choices = final_selections["Group 4: Sciences - 科学 (必修1-2门)"]

has_pre_calc = "AP 预修微积分 (荣誉)" in math_choices
has_physics_c = any("物理 C" in s for s in sci_choices)
# 检查是否选择了 Calculus AB 或 BC 来满足修读 Physics C 的同步学习条件
has_calculus = any("微积分 AB" in s or "微积分 BC" in s for s in math_choices)

conflict_flag = False
if has_physics_c and has_pre_calc and not has_calculus:
    conflict_flag = True
    st.error("⚠️ 选课逻辑冲突提示：")
    st.markdown("""
    **检测到冲突：** 您勾选了 **AP 物理 C 系列**，但数学组仅选择了 **AP 预修微积分**。
    
    **规则说明：** 根据教学手册，修读 AP 物理 C 必须先修或同步修读 **AP 微积分 AB 或 BC**。
    请调整数学选课或更改科学组科目。
    """)

# --- 第五部分：提交与结果汇总 ---
st.divider()
if st.button("确认并提交选课申请", type="primary", use_container_width=True):
    # 基础信息完整性校验
    info_incomplete = not (cn_name and en_name and class_name)
    # 必选学科组校验
    required_groups = list(course_structure.keys())
    empty_groups = [g for g in required_groups if not final_selections[g]]
    
    if conflict_flag:
        st.error("请先修正物理与数学的先修逻辑冲突。")
    elif info_incomplete:
        st.error("个人档案信息未填写完整。")
    elif empty_groups:
        st.error(f"每个学科组至少需选一门，请检查：{', '.join(empty_groups)}")
    else:
        st.balloons()
        st.success("🎉 提交成功！请截图保存此页面汇总。")
        st.write("---")
        st.write(f"**学生：** {cn_name} | {en_name}  **班级：** {class_name}")
        for g, clist in final_selections.items():
            st.write(f"**{g}：** {', '.join(clist)}")
