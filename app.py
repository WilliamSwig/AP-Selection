import streamlit as st

# 设置页面
st.set_page_config(page_title="AP选课系统", layout="centered")

# 标题
st.title("🎓 AP项目学生选课系统")
st.write("请填写基本信息并完成六大学科组选课（每组至少选一门）。")

# 1. 基本信息填写
st.subheader("一、基本信息")
col1, col2 = st.columns(2)
with col1:
    cn_name = st.text_input("中文名")
    grade = st.selectbox("年级", ["G9", "G10", "G11", "G12"])
    country = st.text_input("未来申请国家")
with col2:
    en_name = st.text_input("英文名")
    class_name = st.text_input("班级")
    major = st.text_input("专业方向")

# 2. 准备课程数据
h_raw = ['World History', 'American History', 'Psychology', 'Business study', 'Micro Economics', 'Macro Economics']
humanities = []
for item in h_raw:
    humanities.append(f"Pre-AP {item}")
    humanities.append(f"AP {item}")

course_groups = {
    "第一组：中文组": ["中文"],
    "第二组：英文组": ["ESL", "AP English 10", "AP English language and composition", "AP English Literature"],
    "第三组：人文组": humanities,
    "第四组：科学组": ["Pre-AP Physics", "AP Physics 1", "AP Physics 2", "AP Physics C Mechanics", "AP Physics C E&M", "Pre-AP Chemistry", "AP Chemistry", "Pre-AP Biology", "AP Biology"],
    "第五组：数学组": ["AP pre-Calculus", "AP Calculus AB", "AP Calculus BC", "AP Statistics", "AP Computer Science A", "AP Seminar"],
    "第六组：艺术组": ["AP 2D art and design", "AP 3D art and design"]
}

# 3. 渲染选课界面
st.subheader("二、学科组选课")
selections = {}

for group_name, courses in course_groups.items():
    st.markdown(f"**{group_name}**")
    selected_in_group = []
    # 课程较多时分两列显示
    cols = st.columns(2)
    for i, course in enumerate(courses):
        with cols[i % 2]:
            if st.checkbox(course, key=f"key_{group_name}_{course}"):
                selected_in_group.append(course)
    selections[group_name] = selected_in_group
    st.write("") # 间距

# 4. 冲突逻辑校验
math_sel = selections["第五组：数学组"]
sci_sel = selections["第四组：科学组"]

has_pre_calc = "AP pre-Calculus" in math_sel
physics_c = [c for c in sci_sel if "Physics C" in c]

conflict = False
if has_pre_calc and physics_c:
    conflict = True
    st.error(f"❌ 选课冲突：你选择了 AP pre-Calculus，不能同时选择 {', '.join(physics_c)}。")
    st.warning("💡 提示：选择 AP Physics C 系列课程需要先修或同时修 AP Calculus。")

# 5. 提交结果
st.divider()
if st.button("确认提交选课单", type="primary", use_container_width=True):
    # 检查必填项
    missing_info = not (cn_name and en_name and class_name)
    missing_group = [g for g, s in selections.items() if not s]
    
    if conflict:
        st.error("请先解决选课冲突。")
    elif missing_info:
        st.error("请完整填写基本个人信息。")
    elif missing_group:
        st.error(f"请确保每一组都至少选了一门课。漏选组别：{', '.join(missing_group)}")
    else:
        st.balloons()
        st.success("🎉 提交成功！")
        st.markdown("### 选课汇总清单：")
        st.write(f"**学生：** {cn_name} ({en_name}) | **年级班级：** {grade} {class_name}")
        for g, s in selections.items():
            st.write(f"**{g}：** {', '.join(s)}")
