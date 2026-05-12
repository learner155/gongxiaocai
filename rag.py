from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda

from file_history_store import FileChatMessageHistory
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatTongyi


def get_history(session_id):
    return FileChatMessageHistory(session_id,storage_path="./chat_history")

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt




class RagService(object):
    def __init__(self):
        self.vector_service=VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template=ChatPromptTemplate.from_messages(
            [
                ("system", "你是兰州理工大学财务处的ai助手，千万不可以编造参考资料以外的内容回答"
                           "以我提供的已知参考资料为主，"
                           "简洁和专业的回答用户问题。参考资料:{context}。"),
                ("system", "并且我提供用户的对话历史记录，如下："),
                MessagesPlaceholder("history"),
                ("user", "请回答用户提问：{input}")
            ]
        )

        self.chat_model = ChatTongyi(
    model=config.chat_model_name,
    dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
)

        self.chain=self.__get_chain()



    def __get_chain(self):
        """获取最终的执行链"""
        retriever=self.vector_service.get_retriever()

        def format_document(docs: list[Document]):
            if not docs:
                return "未查询到相关财务政策，请打开财务处官网：https://cwc.lut.edu.cn/danye_x.jsp?urltype=tree.TreeTempUrl&wbtreeid=1056寻找咨询电话，或前往行政楼现场咨询。"
            fomatted_str=""
            for doc in docs:
                fomatted_str+=f"文档片段:{doc.page_content}\n 文档原数据：{doc.metadata}"
            return fomatted_str

        def tmp1(value: dict) -> str:
            return value["input"]

        def tmp2(value) :

            new_value={}
            new_value["input"]=value["input"]["input"]
            new_value["context"]=value["context"]
            new_value["history"]=value["input"]["history"]
            return new_value
        chain={
            "input":RunnablePassthrough(),
            "context":RunnableLambda(tmp1) |retriever| format_document
        } |RunnableLambda(tmp2)| self.prompt_template |print_prompt| self.chat_model | StrOutputParser()

        conversation_chain=RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        return conversation_chain


if __name__=="__main__":
    #配置会话的session_id
    session_config = {
        "configurable": {"session_id": "user1"}
    }

    res=RagService().chain.invoke({"input":"我的体重110斤，尺码推荐"},session_config)
    print(res)
