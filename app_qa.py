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

# 你原来的页面标题（现在会固定不动）
st.title("工小财")
st.divider()  # 分隔符

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

# 初始化快捷提问状态
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
    # 执行后立刻清空快捷提问！防止残留
    st.session_state["quick_question"] = None

    # 输出用户的提问并保存
    st.chat_message("user", avatar="👨‍🎓").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    # ===================== 修改后的流式输出逻辑 =====================
    with st.chat_message("assistant", avatar="🤵🏻"):
        with st.spinner("工小财正在思考中..."):
            # 获取数据流 (去掉了 time.sleep，spinner 会自动处理加载状态)
            res = st.session_state["rag"].chain.stream({"input": prompt}, config.session_config)
            
        # 原生方法直接渲染流，会自动产生打字机效果，并返回完整拼接后的字符串
        full_response = st.write_stream(res)
        
    # 直接将完整回复存入历史记录
    st.session_state["message"].append({"role": "assistant", "content": full_response})
