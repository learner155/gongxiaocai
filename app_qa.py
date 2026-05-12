import time
from rag import RagService
import streamlit as st
import config_data as config

# 标题样式
st.markdown("""
<style>
.stApp > header {
    background-color: #f9f9f9;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999999;
    padding: 1rem 1rem 0rem 1rem;
    border-bottom: 1px solid #eee;
}
.main .block-container {
    margin-top: 65px; 
}
</style>
""", unsafe_allow_html=True)

# ===================== 固定在顶部的网页标题 =====================
st.set_page_config(page_title="工小财-兰州理工财务助手", page_icon="💰")
st.title("工小财")
st.divider()

with st.sidebar:
    st.subheader("常见问题")
    if st.button("📋 报销流程指引"):
        st.session_state["quick_question"] = "请问报销的完整流程和需要准备的材料是什么？"
    if st.button("💳 学费缴费问题"):
        st.session_state["quick_question"] = "请问学费怎么缴费？"
    if st.button("📞 财务处联系方式"):
        st.session_state["quick_question"] = "财务处的办公电话和地点是什么？"

# 初始化状态
if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "您好，我是兰州理工大学财务处助手：工小财。请问您在财务方面遇到什么问题了呢？"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

if "quick_question" not in st.session_state:
    st.session_state["quick_question"] = None

# 渲染历史对话
for message in st.session_state["message"]:
    if message["role"] == "user":
        st.chat_message("user", avatar="👨‍🎓").write(message["content"])
    else:
        st.chat_message("assistant", avatar="🤵🏻").write(message["content"])

user_input = st.chat_input("请输入问题")

if st.session_state["quick_question"]:
    prompt = st.session_state["quick_question"]
else:
    prompt = user_input

if prompt:
    st.session_state["quick_question"] = None

    # 渲染用户输入
    st.chat_message("user", avatar="👨‍🎓").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    # 流式渲染大模型输出
    with st.chat_message("assistant", avatar="🤵🏻"):
        with st.spinner("工小财正在思考中..."):
            # 获取数据流
            res = st.session_state["rag"].chain.stream({"input": prompt}, config.session_config)
            
        # 使用 Streamlit 原生方法直接渲染流
        full_response = st.write_stream(res)
        
    # 保存完整结果
    st.session_state["message"].append({"role": "assistant", "content": full_response})
