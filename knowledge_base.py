"""
知识库
"""
import hashlib
import os.path
import config_data as config
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime


def check_md5(md5_str:str):
    #if进入表示文件不存在，那肯定没有处理过这个md5
    if not os.path.exists(config.md5_path):
        open(config.md5_path,"w",encoding="utf-8").close()
        return False
    else:
        for line in open(config.md5_path,"r",encoding="utf-8").readlines():
            line=line.strip()
            if line==md5_str:
                return True      #已处理过
        return False


def save_md5(md5_str:str):
    with open(config.md5_path,"a",encoding="utf-8") as f:
        f.write(md5_str+"\n")

def get_string_md5(input_str:str, encoding="utf-8"):
    """将传入的字符串转换为md5字符串"""

    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding)

    # 创建md5对象
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_str = md5_obj.hexdigest()

    return md5_str

class KonwledgeBaseService:
    def __init__(self):
        #如果文件夹不存在，则创建，如果存在则跳过
        os.makedirs(config.persist_directory,exist_ok=True)
        self.chroma=Chroma(
            collection_name=config.collection_name,  #数据库表名
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=config.persist_directory  #数据库本地存储文件夹
        )  #向量存储的实例Chroma向量库对象

        #文本分割器对象
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,            #分割之后文本段最大长度
            chunk_overlap=config.chunk_overlap,     #连续文本段之间的字符重叠数量
            separators=config.separators,            #自然段落划分的符号
            length_function=len                      #使用python自带的len函数做长度统计的依据
        )

    def upload_by_str(self,data,filename):
        """将传入的字符串，进行向量化，存入向量数据库中"""
        # 先得到传入字符串的md5值
        md5_hex=get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"
        if len(data) >config.max_split_char_number:
            #如果传入的字符串长度大于1000，则进行文本分割
            knowledge_chunks: list[str]=self.spliter.split_text(data)
        else:
            knowledge_chunks=[data]

        metadata={
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"小曹"
        }
        self.chroma.add_texts(

            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )
        self.chroma.persist()
        save_md5(md5_hex)
        return  "[成功]内容已经成功添加到向量库中"
if __name__=="__main__":
    service=KonwledgeBaseService()
    r=service.upload_by_str("周杰伦","testfile")
    print( r)
