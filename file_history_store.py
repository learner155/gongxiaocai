import os,json
from typing import Sequence

from langchain_community.chat_models import ChatTongyi
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory


#message_to_dict：单个对象（BaseMessage类实例）-> 字典
#messages_from_dict：[字典，字典...] -> [消息,消息....]
#AImessage、HumanMessage、SystemMessage都是BaseMessage的子类

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id=session_id
        self.storage_path=storage_path
        #完整的文件路径
        self.file_path=os.path.join(self.storage_path,self.session_id)
        #确保文件夹是否存在
        os.makedirs(self.storage_path,exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)  # Existing messages
        all_messages.extend(messages)  # Add new messages

    #将数据同步写入到本地文件中
    #类对象写入文件->一堆二进制
    #为了方便，可以将BaseMessage类实例转换成字典，然后写入文件（借助json模块以json字符串写入文件）
    #官方message_to_dict: 单个消息对象（BaseMessage类实例） -> 字典

        # new_messages=[]
        # for message in all_messages:
        #     d=message_to_dict(message)
        #     new_messages.append(d)

        new_messages=[message_to_dict( message) for message in all_messages]

        #将数据写入文件
        with open(self.file_path,"w") as f:
            json.dump(new_messages,f)

    #获取消息
    @property#通过装饰器将messages变成成员属性
    def messages(self) -> list[BaseMessage]:
       # 当前文件内： list[字典]
        try:
            with open(self.file_path,"r",encoding="utf-8")as  f:
                messages_data=json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)



model=ChatTongyi(model="qwen3-max")
prompt=ChatPromptTemplate.from_messages([
    ("system","你需要根据会话历史来回答问题。用户输入：{input}对话历史："),
    MessagesPlaceholder('chat_history'),
    ("human","请给出回应，并且回答我的问题")
])

chain=prompt | model | StrOutputParser()

history_data={}

def get_history(session_id):
    return FileChatMessageHistory(session_id,storage_path="./chat_history")

conversation=RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

if __name__=="__main__":

    #配置当前会话的session_id
    session_config={
        "configurable":{"session_id":"user1"}
                    }
    # print(conversation.invoke({"input":"我有一只小狗"},session_config))
    # print(conversation.invoke({"input":"我有一只袋鼠"},session_config))
    print(conversation.invoke({"input":"那我一共有几个宠物呢？"},session_config))