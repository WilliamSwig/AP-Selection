import streamlit as st

# 页面配置
st.set_page_config(page_title="AP选课系统", layout="centered")

# 自定义 CSS 美化
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stCheckbox { background: white; padding: 10px; border-radius: 5px; margin: 5px 0; border: 1px solid #eee; }
    .stAlert { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 AP项目学生选课系统")
st.info("请完成基本信息填写及六大学科组选课。每组至少选择一门课程。")

# --- 1. 基本信息 ---
st.header("1. 基本信息")
col1, col2 = st.columns(2)
with col1:
    cn_name = st.text_input("中文名")
    grade = st.selectbox("年级", ["G9", "G10", "G11", "G12"])
    country = st.text_input("未来申请国家")
with col2:
    en_name = st.text_input("英文名")
    class_name = st.text_input("班级")
    major = st.text_input("专业方向")

# --- 2. 选课逻辑数据 ---
humanities_subjects = ['World History', 'American History', 'Psychology', 'Business study', 'Micro Economics', 'Macro Economics']
humanities_list = []
for s in humanities_subjects:
    humanities_list.extend([f"Pre-AP {s}", f"AP {s}"])

course_data = {
    "第一组：中文组": ["中文"],
    "第二组：英文组": ["ESL", "AP English 10", "AP English language and composition", "AP English Literature"],
    "第三组：人文组": humanities_list,
    "第四组：科学组": ["Pre-AP Physics", "AP Physics 1", "AP Physics 2", "AP Physics C Mechanics", "AP Physics C E&M", "Pre-AP Chemistry", "AP Chemistry", "Pre-AP Biology", "AP Biology"],
    "第五组：数学组": ["AP pre-Calculus", "AP Calculus AB", "AP Calculus BC", "AP Statistics", "AP Computer Science A", "AP Seminar"],
    "第六组：艺术组": ["AP 2D art and design", "AP 3D art and design"]
}

# --- 3. 渲染选课区 ---
st.header("2. 学科组选课")
selections = {}

for group_name, courses in course_data.items():
    st.subheader(group_name)
    cols = st.columns(2) # 两列显示
    group_selections = []
    for i, course in enumerate(courses):
        # 放置在交替的列中
        with cols[i % 2]:
            if st.checkbox(course, key=f"cb_{course}"):
                group_selections.append(course)
    selections[group_name] = group_selections

# --- 4. 冲突校验 ---
has_conflict = False
# 检查数学组是否选了 pre-Calculus
pre_calc_selected = "AP pre-Calculus" in selections["第五组：数学组"]
# 检查科学组是否选了 Physics C
physics_c_selected = [c for c in selections["第四组：科学组"] if "Physics C" in c]

if pre_calc_selected and physics_c_selected:
    has_conflict = True
    st.error(f"❌ 选课冲突：你选择了 AP pre-Calculus，但科学组中勾选了 {', '.join(physics_c_selected)}。")
    st.warning("⚠️ 提示：选择 AP Physics C 系列课程需要先修或同时修 AP Calculus！请修改选择。")

# --- 5. 提交校验 ---
if st.button("确认提交选课单", type="primary", use_container_width=True):
    # 检查必填项
    missing_info = not (cn_name and en_name and class_name)
    # 检查每组必选
    missing_group = [g for g, s in selections.items() if not s]
    
    if has_conflict:
        st.error("请先处理选课冲突再提交。")
    elif missing_info:
        st.error("请完整填写基本信息。")
    elif missing_group:
        st.error(f"以下学科组尚未选课：{', '.join(missing_group)}")
    else:
        st.balloons()
        st.success("🎉 提交成功！")
        st.write("### 您的选课汇总：")
        st.json({
            "学生信息": {"姓名": f"{cn_name} {en_name}", "年级": grade, "班级": class_name},
            "选课清单": selections
        })
