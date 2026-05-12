import os
# 修复protobuf报错（必须第一行）
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import time
from rag import RagService
import streamlit as st
import config_data as config

#标题固定样式
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

# 页面配置
st.set_page_config(page_title="工小财-兰州理工财务助手", page_icon="💰")
st.title("工小财")
st.divider ()          

# 侧边栏快捷问题
with st.sidebar:
    st.subheader("常见问题")
    if st.button("📋 报销流程指引"):
        st.session_state["quick_question"] = "请问报销的完整流程和需要准备的材料是什么？"
    if st.button("💳 学费缴费问题"):
        st.session_state["quick_question"] = "请问学费怎么缴费？"
    if st.button("📞 财务处联系方式"):
        st.session_state["quick_question"] = "财务处的办公电话和地点是什么？"

# 初始化会话
if "message" not in st.session_state:
    st.session_state["message"]=[{"role":"assistant","content":"您好，我是兰州理工大学财务处助手：工小财。请问您在财务方面遇到什么问题了呢？"}]

if "rag" not in st.session_state:
    st.session_state["rag"]=RagService()

if "quick_question" not in st.session_state:
    st.session_state["quick_question"] = None

# 渲染完整聊天记录
for message in st.session_state["message"]:
    if message["role"] == "user":
        st.chat_message("user", avatar="👨‍🎓").write(message["content"])
    else:
        st.chat_message("assistant", avatar="🤵🏻").write(message["content"])

# 输入框
user_input=st.chat_input("请输入问题")

# 获取提问内容
if st.session_state["quick_question"]:
    prompt = st.session_state["quick_question"]
else:
    prompt = user_input

# 核心对话逻辑（保留time.sleep + 修复所有报错）
if prompt:
    st.session_state["quick_question"] = None

    # 显示用户消息
    st.chat_message("user",avatar="👨‍🎓").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    ai_res=[]
    with st.spinner("工小财正在思考中"):
        # 🔥 修复核心报错：直接定义固定的session_id，不再调用config
        session_config = {"configurable": {"session_id": "gongxiaocai_123"}}
        res=st.session_state["rag"].chain.stream({"input":prompt}, config=session_config)
        # 完全保留你要求的 time.sleep(1)
        time.sleep(1)

        # 你的原捕获函数，完全不动
        def capture(generator,cache_list):
            for chunk in generator:
                if chunk.strip():  # 过滤空内容
                    cache_list.append(chunk)
                    yield chunk

        # 修复头像错误，原格式不动
        st.chat_message("assistant",avatar="🤵🏻").write_stream(capture(res,ai_res))
        
        # 保存完整聊天记录，原格式不动
        full_answer = "".join(ai_res)
        st.session_state["message"].append({"role":"assistant","content":full_answer})
