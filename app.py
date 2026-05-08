import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(page_title="AP选课系统", layout="centered")

# --- 初始化 Google Sheets 连接 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 强制通过 CSS 将基本信息的标签设为白色 ---
st.markdown("""
    <style>
    /* 针对基本信息部分的输入框标签进行颜色设置 */
    /* 我们通过选择器定位到这些标签并强制设为白色 */
    .stTextInput label, .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: bold;
    }
    
    /* 保持下方学科组折叠面板内的文字为清晰的深色（防止背景冲突） */
    .stExpander label {
        color: #1f2937 !important;
    }

    /* 学科组标题文字 */
    .stExpander .stMarkdown p {
        color: #1f2937 !important;
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
    country = st.text_input("拟申请国家",placeholder="请填写")
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
    
    # 【关键：这里必须定义这个变量】
    # 检查中文名、英文名、班级是否填写（你可以根据需要增加字段）
    info_incomplete = not (cn_name and en_name and class_name)
    
    # 检查必选组是否漏选
    required_groups = list(course_structure.keys())
    empty_groups = [g for g in required_groups if not final_selections[g]]
    
    # --- 开始判断 ---
    if conflict_flag:
        st.error("请先修正物理与数学的先修逻辑冲突。")
    
    elif info_incomplete:  # 现在程序认识这个变量了
        st.error("个人档案信息未填写完整（姓名、班级为必填）。")
        
    elif empty_groups:
        st.error(f"每个学科组至少需选一门，请检查：{', '.join(empty_groups)}")
        
    else:
        # 这里开始执行正常的 Google Sheets 提交逻辑...
        try:
            # (之前的 conn.read 和 conn.update 代码)
            st.success("提交成功！")
        except Exception as e:
            st.error(f"提交失败: {e}")

            # 2. 构造新的数据行 (Pandas DataFrame)
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "CN_Name": cn_name,
                "EN_Name": en_name,
                "Grade": grade,
                "Class": class_name,
                "Major": major,
                "Selections": details_text
            }])

            # 3. 关键步骤：读取现有表格数据
            # 建议将 ttl 设为 0，确保拿到的是表格最新的状态，避免覆盖别人的提交
            existing_data = conn.read(worksheet="Sheet1", ttl=0)
            
            # 4. 将新行合并到旧数据中
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            # 5. 写回 Google Sheets
            conn.update(worksheet="Sheet1", data=updated_df)

            st.balloons()
            st.success("🎉 提交成功！选课数据已同步至教务表格。")
            
        except Exception as e:
            st.error(f"提交至云端失败，请检查网络或配置。详情: {e}")
