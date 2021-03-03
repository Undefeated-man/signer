"""
    ###########################################################################
	#		                                                                  #
	#		project: signer                                                   #
	#		                                                                  #
	#		filename: signer.py                                               #
	#		                                                                  #
	#		programmer: Vincent Holmes                                        #
	#		                                                                  #
	#		description: 可以自动格式化出一个漂亮的文件头, 还可以缓存之前     #
	#                     使用过的模板, 可以选择签名为同一个project           #
	#                     下的不同文件.                                       #
	#		                                                                  #
	#		start_date: 2020-06-15                                            #
	#		                                                                  #
	#		last_update: 2021-03-03                                           #
	#		                                                                  #
	###########################################################################
"""


from os.path import exists
import os
import json
import time
import copy

LAN_DIC = {
    "python": ['"""'],
    "java": ["/*", "*/"],
    "php": ["/*", "*/"],
    "c": ["/*", "*/"],
    "c++": ["/*", "*/"],
    "javascript": ["/*", "*/"],
    "css": ["/*", "*/"],
    "shell": [":<<!", "!"],
    "html": ["<!--", "-->"],
    "r":[""]
}

TAIL = {
    "py": "python",
    "js": "javascript",
    "css": "css",
    "java": "java",
    "cpp": "c++",
    "php": "php",
    "sh": "shell",
    "c": "c",
    "html": "html",
    "r":"r"
}

DATA_DIC = {"project":"", "filename":"", "programmer":"", "description":"", "start_date":""}

SIGN_LST = ["project", "filename", "programmer", "description", "start_date", "last_update"]

####################################### 功能区 #################################

#检验是否全是中文字符
def isChinese(strs, type=0):
    """
    用于识别中文。

    Args:
        type: 默认是0，代表要全字段为中文才返回真
              type=1的时候，只要有存在中文就返回真
    """
    chinese = []
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            chinese.append(False)
        else:
            chinese.append(True)
    if type == 0:
        if not False in chinese:
            return True
        else:
            return False
    else:
        if True in chinese:
            return True
        else:
            return False


# 尝试通过文件名后缀自动识别并返回文件类型
def getlan(name):
    filetype = name.split('.')
    lan = TAIL.get(filetype[-1].lower(), "python")
    return lan


# 双重保障，确保信息正确修改后删文件改名，程序中途关闭也不会导致信息丢失
def exam(origin, target):
    """
    取倒数2~6行进行信息比对。

    Args:
        origin: 这是原文件名
        target: 这是签名后的文件名
    """
    try:
        with open(origin, "r", encoding="utf-8") as f:
            o_lines = f.read().split("\n")[-6:-1]

        with open(target, "r", encoding="utf-8") as f:
            t_lines = f.read().split("\n")[-6:-1]
    except:
        with open(origin, "r", encoding="gbk") as f:
            o_lines = f.read().split("\n")[-6:-1]

        with open(target, "r", encoding="utf-8") as f:
            t_lines = f.read().split("\n")[-6:-1]

    if o_lines == t_lines:
        os.remove(origin)
        try:
            os.rename(target, origin)
        except:
            print("找不到文件 或 存在相同文件名")
    else:
        print("信息验证异常, 请手动检查确认是否替换文件")

# 文件头签名处理
class Header:
    """

    这个类用于生成文件签名头。

    Args:
        sym: 这个是一个三元的元组，定义了文件头的格式
        cache: 这是读取到的缓存，是一个字典
        o_file: 原文件的文件名。
        lan: 选择注释的语言格式，默认是python。

    Bugs:
        一个汉字符号占格两个，但是检测不出来，有中文标点会对不齐
    """

    def __init__(self, sym, cache, o_file, lan="python"):
        self.sym = sym
        self.cache = cache
        self.block_cmt = LAN_DIC.get(lan.lower(), ['"""'])
        self.o_file = o_file
        self.project = -1       # 默认最后一个项目
        self.file = -1       # 默认最后一个文件名
        self.header = []     # 先把每一行初始化为列表元素，最后合并
        self.data = {}        # 用于储存选定的缓存模板信息
        self.final = ''


    def create_info(self):
        """
        计算并生成特定格式的文件签名头。
        """

        print("\n\n\t%s 现在签名的文件是：%s %s\n" % ("**"*15, self.o_file, "**"*15))
        input("\t\t按回车继续运行")

        # 每次用前初始化，确保万无一失
        self.header = []
        self.header.append(self.block_cmt[0])
        self.header.append("\n\t%s" % (self.sym[0]*75))

        # 选模板
        self.cache_pro()

        # 更新最后修改日期
        self.data["last_update"] = time.strftime("%Y-%m-%d", time.localtime())

        # 添加行
        for kw in SIGN_LST:
            self.header.append(self.cnt_col(''))
            self.header.append(self.cnt_col(kw))

        # 结尾封行
        self.header.append(self.cnt_col(''))
        self.header.append("\n\t%s\n" % (self.sym[0]*75))
        self.header.append("%s\n\n\n" % self.block_cmt[-1])

        # 合成字符串段落并进行信息比对
        self.header = "".join(self.header)
        try:
            with open(self.o_file, 'r', encoding="utf-8") as f:
                self.final = self.header + f.read()
        except:
            with open(self.o_file, 'r', encoding="gbk") as f:
                self.final = self.header + f.read()
        safe = self.data_exam()

        # 若数据安全，则保存
        if safe:
            return self.final
        else:
            return ''


    def cnt_col(self, kw):
        """
        确保生成每行字符长度不超过80个.

        Args:
            kw: 关键词，用于提取字典里的缓存信息

        Returns:
            返回一个列表元素(字符串)，作为一个信息点。
        """
        chinese = 0
        if len(str(kw))+len(self.data.get(kw, ''))+2 < 55 and not isChinese(self.data.get(kw, ''), type=1):     # 字符串正常长度
            for ch in [i for i in self.data.get(kw, '')]:
                if isChinese(ch):
                    chinese += 1
            n = 66 - len(str(kw)) - len(self.data.get(kw, '')) - chinese - 2
            if self.data.get(kw, '') == '':
                lines = "\n\t%s\t\t%s  %s%s%s" % (self.sym[1], str(kw.capitalize()), self.data.get(kw, ""), ' ' * n, self.sym[1])
            else:
                lines = "\n\t%s\t\t%s: %s%s%s" % (self.sym[1], str(kw.capitalize()), self.data.get(kw, ""), ' ' * n, self.sym[1])
        else:                           # 字符串过长，切成n段
            # 判断是中文还是英文
            if isChinese(self.data[kw], type=1):
                ch_num = 25
            else:
                ch_num = 50

            # 先算有几行
            nline = (len(self.data[kw])+2)//ch_num
            content = [i for i in self.data[kw]]
            for i in range(nline):
                content.insert(ch_num*(i+1), '//')
            content = "".join(content)
            content = content.split("//")   # 按行分隔成列表元素

            # 整理成一个元素
            for ch in [i for i in content[0]]:
                if isChinese(ch):
                    chinese += 1
            n = 66 - len(content[0]) - len(str(kw)) - chinese - 2
            lines = "\n\t%s\t\t%s: %s%s%s" % (self.sym[1], str(kw.capitalize()), content[0], ' ' * n, self.sym[1])
            for i in range(1, len(content)):
                chinese = 0
                for ch in [i for i in content[i]]:
                    if isChinese(ch):
                        chinese += 1
                n = 52 - len(content[i]) - chinese
                line = "\n\t%s%s%s%s%s" % (self.sym[1], ' '*21, content[i], ' ' * n, self.sym[1])
                lines = lines + line

        return lines


    def cache_pro(self):
        """
        操作缓存的数据：选模板、加新模板、删模板

        Returns:
            不返回值.
        """

        func = input("\n\t功能选择：\n\t\t1、查看已缓存的模板\n\t\t2、新建模板\n\t\t3、用最后一次使用的模板\n")
        # 非法输入处理
        while func not in ('1', '2', '3'):
            func = input("主人您点错辣，应该输入1~3的整数序号哦！")
        # 正确输入时的处理
        if func == '3':
            self.check_cache(type=1)
            self.data = self.cache["project"][self.project]["data"][self.file]
        elif func == '1':
            project_name = "\n\t\t\t\t".join([str(self.cache["project"].index(i)) \
            + '、' + i["project_name"] for i in self.cache["project"]])

            print("\n%s%s\n%s%s\n%s%s\n" % ('\t', '###'*20, '\t'*3, project_name, '\t', '###'*20))
            try:
                pro_num = input("请输入你要用的project序号：")
                pro_num = int(pro_num)

                filename = "这是用过的文件名：" + \
                "\n\t\t\t\t".join([str(self.cache["project"][pro_num]["data"].index(i)) \
                + '、' + i["filename"] for i in self.cache["project"][pro_num]["data"]])

                print("\n%s%s\n%s%s\n%s%s\n" % ('\t', '###'*20, '\t'*2, filename, '\t', '###'*20))
                try:
                    f_num = input("请输入你要用的文件序号(新文件输入n)：")
                    f_num = int(f_num)
                    self.data = self.cache["project"][pro_num]["data"][f_num]
                except:
                    self.data = self.cache["project"][pro_num]["data"][-1]
                    self.data["filename"] = self.o_file
            except:
                print("哎呀，主人请输入规定数字哦！")
        elif func == '2':
            data_dic = copy.deepcopy(DATA_DIC)
            self.cache["project"][self.project]["data"].append(data_dic)
            self.check_cache()
            self.data = self.cache["project"][-1]["data"][-1]


    def check_cache(self, type=0):      # 用于检查缓存的内容是否完整
        """
        type是0的时候创建新模板，否则检查既有字典
        """
        change = False
        check_dic = self.cache["project"][self.project]["data"]
        if type == 0:
            data_dic = {}
        else:
            data_dic = check_dic[self.file]
            data_dic["project"] = self.cache["project"][self.project]["project_name"]

        data_dic["filename"] = self.o_file
        for i in self.cache["check"]:
            if data_dic.get(i,'') == '':
                data_dic[i] = input("\n\t%s: "%(i))
                change = True
        if data_dic.get("start_date", "") == '':
            data_dic["start_date"] =\
            time.strftime("%Y-%m-%d", time.localtime())

        if self.cache["project"][self.project]["project_name"] == "":
            self.cache["project"][self.project]["project_name"] = data_dic["project"]
            check_dic[-1] = data_dic
        elif self.cache["project"][self.project]["project_name"] == data_dic["project"]:
            check_dic.append(data_dic)
        else:
            new_project = {"project_name":data_dic["project"], "data":[data_dic]}
            if type == 0:
                self.cache["project"].append(new_project)
        if change:
            print('\n\t这是现有的信息')
            print(self.cache)
            doSave = input("是否保存为新json(y/n)：")
            if doSave.lower() == 'y':
                with open("cache.json", "w+", encoding="utf-8") as f:
                    f.write(str(self.cache).replace("'", '"'))


    def data_exam(self):
        """
        用于确保数据安全。

        Returns:
            返回 True/False
        """
        try:
            with open(self.o_file, 'r', encoding="utf-8") as f:               # 取最后2~6行数据进行比对（防止最后一行空行）
                o_file = f.read().split('\n')[-1:-6]
        except:
            with open(self.o_file, 'r', encoding="gbk") as f:               # 取最后2~6行数据进行比对（防止最后一行空行）
                o_file = f.read().split('\n')[-1:-6]

        safe = []
        for i in o_file:
            safe.append(i in self.final)
        if False in safe:
            return False
        else:
            return True

####################################### 主函数 #################################
if __name__ == '__main__':
    print("\n\t\t%s\n\n\t\t%s\n\n\t\t%s\n" % ("**"*40, "欢迎来到文件头自动签名系统".center(70), "**"*40))

    # 检查是否存在模板文件，并定义框架格式
    if exists("init.int"):
        with open("init.int", "r", encoding='utf-8') as frame:
            f = frame.read()
            line = f.split("\n")
            sym1 = line[0][:][0]
            try:
                sym2 = line[1][:][0]
            except:
                sym2 = "#"
        sym = (sym1, sym2)
    else:
        sym = ("#", "#")

    # 读取缓存信息
    if exists("cache.json"):
        with open("cache.json", "r+", encoding='utf-8') as c:
            cache = json.load(c)

    autoRead = input("\n\t是否自动识别文件夹内文件(y/n)(直接输入文件名进行签名)：")
    if autoRead.lower() == 'y':
        # 读取正文内容, 方便比对数据
        file_lst = os.listdir(os.getcwd())      # 获取文件列表
        for i in ["init.ini", "cache.json", "signer.py"]:
            file_lst.remove(i)                  # 移除不必要数据

        for i in file_lst:
            lan = getlan(i)      # 自动检测语言类型，默认python
            h = Header(sym, cache, i, lan=lan)
            signed = h.create_info()
            if signed != '':
                try:
                    with open("signed_" + i, 'w+', encoding="utf-8") as f:
                        f.write(signed)
                except:
                    with open("signed_" + i, 'w+', encoding="gbk") as f:
                        f.write(signed)
                exam(i, "signed_" + i)
            else:
                print("Failed")

    else:
        if exists(autoRead):
            pass
        else:
            autoRead = input("主人，我没有找到你要签名的文件，能告诉我你要签名的是哪个文件吗(带文件后缀的哦)？")

        lan = getlan(autoRead)      # 自动检测语言类型，默认python
        h = Header(sym, cache, autoRead, lan=lan)        # 实例化我的类
        signed = h.create_info()
        # 确保不要把文件误删
        if signed != '':
            try:
                with open("signed_" + autoRead, 'w+', encoding="utf-8") as f:
                    f.write(signed)
            except:
                with open("signed_" + autoRead, 'w+', encoding="gbk") as f:
                    f.write(signed)
            exam(autoRead, "signed_" + autoRead)
        else:
            print("Failed")


    input("Finished!")         # 保存结果页面，方便看最后是否成功

