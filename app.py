import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(page_title="AP选课系统", layout="centered")

# --- 初始化 Google Sheets 连接 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 更改点：使用 CSS 变量 --text-color 代替固定颜色
st.markdown("""
    <style>
    /* 针对基本信息部分的输入框标签：跟随系统文本颜色变量 */
    .stTextInput label, .stSelectbox label {
        color: var(--text-color) !important;
        font-weight: bold;
    }
    
    /* 针对折叠面板 (Expander) 内的文字：同样跟随系统变量 */
    .stExpander label {
        color: var(--text-color) !important;
    }

    /* 针对学科组标题文字 */
    .stExpander .stMarkdown p {
        color: var(--text-color) !important;
    }
    
    /* 可选：如果你希望分界线颜色也自适应 */
    hr {
        border-color: var(--secondary-bg-color) !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 VSPH AP 项目选课系统")
st.info("提示：请根据最新教学大纲进行勾选。每个学科组必须至少选择一门课程。")

# --- 第一部分：个人档案 ---
st.subheader("一、学生基本信息")
c1, c2 = st.columns(2)
with c1:
    cn_name = st.text_input("中文姓名", placeholder="请填写")
    grade = st.selectbox("当前就读年级", ["G9","G10", "G11"])
    country = st.text_input("拟申请国家或地区",placeholder="请填写")
with c2:
    en_name = st.text_input("英文姓名", placeholder="请填写")
    class_name = st.text_input("行政班级",placeholder="请填写")
    major = st.text_input("拟申请专业方向",placeholder="请填写")

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
        "预修 AP商科 (基础)", "AP 商科 (荣誉)", "AP 微观经济 (荣誉)", "AP 宏观经济 (荣誉)",
        "基础美国历史 (基础)", "AP 美国历史 (荣誉)", "AP 世界历史 (荣誉)",
        "预修 AP 心理学 (基础)", "AP 心理学 (荣誉)"
    ],
    "Group 4: Sciences - 科学 (必修1-2门)": [
        "AP 物理 1 (荣誉)", "AP 物理 C 力学 (荣誉)", "预修 AP 物理（力学） (基础)",
        "AP 物理 C 电磁 (荣誉)", "预修 AP 生物 (基础)", "AP 生物 (荣誉)",
        "预修 AP 化学 (基础)", "AP 化学 (荣誉)"
    ],
    "Group 5: Mathematics and Computer Science - 数学与计算机 (必修)": [
        "IG 0580 2 (基础)", "AP 预备微积分 (荣誉)",
        "AP 微积分 AB (荣誉)", "AP 微积分 BC (荣誉)", "AP 统计 (荣誉)",
        "线性代数 (荣誉)", "多元微积分 (荣誉)", "AP 计算机应用 (荣誉)"
    ],
    "Group 6: Arts - 艺术 (选修)": [
        "基础艺术 (基础)", "AP 艺术 - 2D (荣誉)", "AP 艺术 - 3D (荣誉)", 
        "AP 绘画 (荣誉)", "艺术鉴赏 (荣誉)", "音乐史 (荣誉)"
    ],
    "School cores - 校本核心课程": [
        "社团 (基础)", "体育&赛艇 (基础)", "职业规划 (基础)", 
        "升学指导 (基础)", "AP 研讨 (荣誉)", "AP 自由课题 (荣誉)"
    ]
}

# --- 第三部分：动态选课界面渲染 (全量重构版) ---
st.subheader("二、学科组选课")
final_selections = {}

# 1. 逻辑配置映射
chinese_mapping = {"G9": ["中文文学 2 (基础)"], "G10": ["中文文学 3 (基础)"], "G11": ["中文文学 4 (荣誉)"]}

english_mapping = {
    "G9": ["ESL 2 (基础)", "10年级英语 (荣誉)", "EFL 2 (荣誉)", "英语文学 2 (荣誉)"],
    "G10": ["ESL 3 (基础)", "英语文学 3 (荣誉)", "AP 英语语言与写作 (荣誉)", "AP 英语语言与文学 (荣誉)"],
    "G11": ["ESL 3 (基础)", "英语文学 4 (荣誉)", "AP 英语语言与写作 (荣誉)", "AP 英语语言与文学 (荣誉)"]
}

humanities_mapping = {
    "G9": ["预修 AP 商科 (基础)", "AP 微观经济 (荣誉)", "基础美国历史 (基础)", "预修 AP 心理学 (基础)"],
    "G10": ["预修 AP 商科 (基础)", "AP 商科 (荣誉)", "AP 微观经济 (荣誉)", "AP 宏观经济 (荣誉)", "AP 美国历史 (荣誉)", "AP 世界历史 (荣誉)", "预修 AP 心理学 (基础)", "AP 心理学 (荣誉)"],
    "G11": ["AP 商科 (荣誉)", "AP 宏观经济 (荣誉)", "AP 美国历史 (荣誉)", "AP 世界历史 (荣誉)", "AP 心理学 (荣誉)"]
}

science_mapping = {
    "G9": ["AP 物理 1 (荣誉)", "AP 物理 C 力学 (荣誉)", "预修 AP 物理（力学） (基础)", "预修 AP 生物 (基础)", "预修 AP 化学 (基础)"],
    "G10": course_structure["Group 4: Sciences - 科学 (必修1-2门)"],
    "G11": ["AP 物理 C 电磁 (荣誉)", "AP 生物 (荣誉)", "AP 化学 (荣誉)"]
}

# 数学组逻辑映射 (根据您的新要求)
math_mapping = {
    "G9": ["IG 0580 2 (基础)", "AP 预备微积分 (荣誉)", "AP 微积分 AB (荣誉)", "AP 微积分 BC (荣誉)", "AP 计算机应用 (荣誉)"],
    "G10": ["AP 预备微积分 (荣誉)", "AP 微积分 AB (荣誉)", "AP 微积分 BC (荣誉)", "AP 统计 (荣誉)", "线性代数 (荣誉)", "多元微积分 (荣誉)", "AP 计算机应用 (荣誉)"],
    "G11": ["AP 预备微积分 (荣誉)", "AP 微积分 AB (荣誉)", "AP 微积分 BC (荣誉)", "AP 统计 (荣誉)", "线性代数 (荣誉)", "多元微积分 (荣誉)", "AP 计算机应用 (荣誉)"]
}

# 互斥定义
exclusive_pairs = [
    ("预修AP商科 (基础)", "AP商科 (荣誉)"),
    ("预修AP心理学 (基础)", "AP 心理学 (荣誉)"),
    ("预修AP物理（力学） (基础)", "AP 物理 C 力学 (荣誉)"),
    ("预修 AP 生物 (基础)", "AP 生物 (荣誉)"),
    ("预修 AP 化学 (基础)", "AP 化学 (荣誉)")
]
calculus_trio = ["IG 0580 2" , "AP 预备微积分 (荣誉)", "AP 微积分 AB (荣誉)", "AP 微积分 BC (荣誉)"]

# 在这里添加艺术组定义
art_exclusive_group = [
    "基础艺术 (基础)", 
    "AP 艺术-2D (荣誉)", 
    "AP 艺术-3D (荣誉)", 
    "AP 绘画 (荣誉)", 
    "艺术鉴赏 (荣誉)"
]

# 2. 循环渲染学科组
for g_title, courses in course_structure.items():
    with st.expander(f"📖 {g_title}", expanded=True):
        selected_list = []
        cols = st.columns(2)
        
        # --- 分学科组逻辑处理 ---
        
        # A. 中文与英语组
        if "Group 1" in g_title or "Group 2" in g_title:
            allowed = chinese_mapping.get(grade, []) if "Group 1" in g_title else english_mapping.get(grade, [])
            for idx, course_name in enumerate(courses):
                with cols[idx % 2]:
                    is_in_grade = course_name in allowed
                    if st.checkbox(course_name, disabled=not is_in_grade, key=f"lang_{course_name}_{grade}"):
                        selected_list.append(course_name)

        # B. 人文与科学组 (包含前后期课程互斥)
        elif "Group 3" in g_title or "Group 4" in g_title:
            allowed = humanities_mapping.get(grade, []) if "Group 3" in g_title else science_mapping.get(grade, [])
            prefix = "hu" if "Group 3" in g_title else "sci"
            for idx, course_name in enumerate(courses):
                with cols[idx % 2]:
                    is_in_grade = course_name in allowed
                    is_excluded = False
                    # 检查互斥对
                    for p1, p2 in exclusive_pairs:
                        if course_name == p1 and st.session_state.get(f"{prefix}_{p2}_{grade}", False): is_excluded = True
                        if course_name == p2 and st.session_state.get(f"{prefix}_{p1}_{grade}", False): is_excluded = True
                    
                    checked = st.session_state.get(f"{prefix}_{course_name}_{grade}", False)
                    if st.checkbox(course_name, value=checked if is_in_grade else False, 
                                   disabled=not is_in_grade or (is_excluded and not checked), 
                                   key=f"{prefix}_{course_name}_{grade}"):
                        selected_list.append(course_name)

        # C. 数学组 (微积分三选一互斥 + 年级过滤)
        elif "Group 5" in g_title:
            allowed = math_mapping.get(grade, [])
            # 检查当前微积分三选一是否有任何一个已被勾选
            any_calc_selected = any(st.session_state.get(f"math_{c}_{grade}", False) for c in calculus_trio)
            
            for idx, course_name in enumerate(courses):
                with cols[idx % 2]:
                    is_in_grade = course_name in allowed
                    is_calc_excluded = False
                    
                    # 微积分互斥逻辑
                    if course_name in calculus_trio:
                        is_this_selected = st.session_state.get(f"math_{course_name}_{grade}", False)
                        if any_calc_selected and not is_this_selected:
                            is_calc_excluded = True
                    
                    checked = st.session_state.get(f"math_{course_name}_{grade}", False)
                    if st.checkbox(course_name, value=checked if is_in_grade else False,
                                   disabled=not is_in_grade or is_calc_excluded,
                                   key=f"math_{course_name}_{grade}"):
                        selected_list.append(course_name)

        # --- D. 艺术组 ---
        elif "Group 6" in g_title:
            any_art_selected = any(st.session_state.get(f"art_{a}_{grade}", False) for a in art_exclusive_group)
            for idx, course_name in enumerate(courses):
                with cols[idx % 2]:
                    is_art_excluded = False
                    if course_name in art_exclusive_group:
                        is_this_art_selected = st.session_state.get(f"art_{course_name}_{grade}", False)
                        if any_art_selected and not is_this_art_selected: is_art_excluded = True
                    if st.checkbox(course_name, disabled=is_art_excluded, key=f"art_{course_name}_{grade}"):
                        selected_list.append(course_name)

        # --- E. 校本核心课程 (逻辑重构) ---
        elif "School cores" in g_title:
            for idx, course_name in enumerate(courses):
                with cols[idx % 2]:
                    # 默认状态逻辑
                    is_fixed_selected = False
                    is_disabled = False
                    
                    # 1. 必选：社团、体育&赛艇
                    if course_name in ["社团 (基础)", "体育&赛艇 (基础)"]:
                        is_fixed_selected = True
                        is_disabled = True
                    
                    # 2. 必选分支：职业规划 (G9) / 升学指导 (G10/G11)
                    elif course_name == "职业规划 (基础)":
                        if grade == "G9":
                            is_fixed_selected = True
                            is_disabled = True
                        else:
                            is_disabled = True # 非G9不可选
                    elif course_name == "升学指导 (基础)":
                        if grade in ["G10", "G11"]:
                            is_fixed_selected = True
                            is_disabled = True
                        else:
                            is_disabled = True # G9不可选
                    
                    # 3. 选修逻辑：AP研讨(全员) / AP自由课题(G10/11)
                    elif course_name == "AP 自由课题 (荣誉)":
                        if grade == "G9":
                            is_disabled = True

                    # 渲染复选框
                    if st.checkbox(course_name, value=is_fixed_selected, disabled=is_disabled, key=f"core_{course_name}_{grade}"):
                        selected_list.append(course_name)
                    elif is_fixed_selected: # 即使disabled也要记录在最终名单中
                        selected_list.append(course_name)

        final_selections[g_title] = selected_list
        
# --- 第四部分：底层逻辑冲突校验 (逻辑更新点) ---

# 获取数学组和科学组的当前选择结果
math_choices = final_selections.get("Group 5: Mathematics and Computer Science - 数学与计算机 (必修)", [])
sci_choices = final_selections.get("Group 4: Sciences - 科学 (必修1-2门)", [])

# 逻辑定义
has_pre_calc = "AP 预备微积分 (荣誉)" in math_choices
# 检查是否选了任何一门物理 C (力学或电磁)
has_physics_c = any("物理 C" in s for s in sci_choices)
# 检查是否选择了 Calculus AB 或 BC 来满足修读 Physics C 的条件
has_calculus = any("微积分 AB" in s or "微积分 BC" in s for s in math_choices)

conflict_flag = False

# --- 核心逻辑更改之处 ---
# 规则：选了预备微积分，则不能选物理 C；或者：选了物理 C 必须有 Calculus
if has_physics_c:
    if has_pre_calc or not has_calculus:
        conflict_flag = True
        st.error("⚠️ 选课逻辑冲突：数学基础不足")
        st.markdown("""
        **检测到冲突：** 您勾选了 **AP 物理 C 系列**，但数学组选择了 **AP 预备微积分** 或未选择 **AP 微积分 AB/BC**。
        
        **规则说明：** 修读 AP 物理 C 必须先修或同步修读 **AP 微积分 AB 或 BC**。
        请将数学更改为 AP 微积分 AB/BC，或将科学组改为 AP 物理 1 等其他科目。
        """)

# --- 第五部分：提交与结果汇总 ---
st.divider()

if st.button("确认并提交选课申请", type="primary", use_container_width=True):
    
    # 1. 变量定义与校验 (确保这些变量你已经定义好了)
    info_incomplete = not (cn_name and en_name and class_name)
    required_groups = list(course_structure.keys())
    empty_groups = [g for g in required_groups if not final_selections[g]]
    
    # 2. 条件判断
    if conflict_flag:
        st.error("请先修正逻辑冲突。")
        
    elif info_incomplete:
        st.error("个人档案信息未填写完整。")
        
    elif empty_groups:
        st.error(f"每个学科组至少需选一门，请检查：{', '.join(empty_groups)}")
        
    else:  # <--- 确保这一行最左侧的空格数，与上面的 if/elif 完全一致
        try:
            # 这里开始是 else 内部的代码，需要再往右缩进 4 个空格
            record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "CN_Name": cn_name,
                "EN_Name": en_name,
                "Grade": grade,
                "Class": class_name,
                "Country": country,
                "Major": major
            }

            # 2. 动态拆分学科组到不同列
            for group_name, selected_courses in final_selections.items():
                record[group_name] = ", ".join(selected_courses)

            # 3. 转换为 DataFrame
            new_row = pd.DataFrame([record])

            # 4. 写入 Google Sheets
            existing_data = conn.read(worksheet="AP_Selection_Database", ttl=0)
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="AP_Selection_Database", data=updated_df)
            
            st.balloons()
            st.success("🎉 选课数据已按学科组分列写入表格！")

        except Exception as e:
            st.error(f"写入失败。具体原因: {e}")
