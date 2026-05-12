




"""
基于streamlit完成web网页上传服务


Streamlit当web页面元素发生变化，则代码重新执行一遍，会造成状态的丢失
"""
import time

from docx import Document
from pypdf import PdfReader

from knowledge_base import KonwledgeBaseService
import streamlit as st
#网页标题
st.title("知识库更新服务")

#创建文件上传
upload_file=st.file_uploader("请上传txt文件（支持TXT,PDF,Word）",
                             type=["txt", "pdf", "docx"],
                             accept_multiple_files=False #False表示只允许上传一个文件
                             )

#session_state是一个字典
if "service" not in st.session_state:
    st.session_state["service"]=KonwledgeBaseService()


# ===================== 改造点2：通用文件文本提取函数 =====================
def extract_file_content(uploaded_file):
    """根据文件类型，自动提取文本内容"""
    file_extension = uploaded_file.name.split(".")[-1].lower()

    # 1. 处理 TXT 文件
    if file_extension == "txt":
        return uploaded_file.getvalue().decode("utf-8")

    # 2. 处理 PDF 文件
    elif file_extension == "pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    # 3. 处理 Word(docx) 文件
    elif file_extension == "docx":
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    else:
        return "不支持的文件格式"


# ===================== 上传处理逻辑 =====================

if upload_file is not None:
    file_name = upload_file.name
    file_size = upload_file.size / 1024

    st.subheader(f"✅ 已上传：{file_name}")
    st.write(f"文件大小：{file_size:.2f} KB")

    with st.spinner("📤 正在解析文件并更新知识库..."):
        try:
            # 提取文本
            file_text = extract_file_content(upload_file)
            # 上传到知识库
            result = st.session_state["service"].upload_by_str(file_text, file_name)
            st.success("文件处理成功！")
            st.write(result)
        except Exception as e:
            st.error(f"处理失败：{str(e)}")

