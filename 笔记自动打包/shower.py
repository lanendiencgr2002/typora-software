import os
import time
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog
import glob
import zipfile
import re

md文件路劲 = ""
图片路劲 = ""
图片路劲md_assets = ""
md压缩包名字 = ""
打包后的路劲 = ""
md文件压缩包名字 = ""
md图片1压缩包名字 = ""
md图片2压缩包名字 = ""

class Stats:
    def __init__(self):
        self.ui = QUiLoader().load('./ui/界面.ui')
        self.参数初始化()
        self.ui.pushButton.clicked.connect(lambda:self.打开文件夹("md文件路劲"))
        self.ui.pushButton_2.clicked.connect(lambda:self.打开文件夹("图片路劲"))
        self.ui.pushButton_3.clicked.connect(lambda:self.打开文件夹("图片路劲md_assets"))
        self.ui.pushButton_8.clicked.connect(lambda:self.打开文件夹("打包后的路劲"))
        self.ui.pushButton_5.clicked.connect(self.保存路劲)
        self.ui.pushButton_4.clicked.connect(lambda:self.压缩md文件("直接"))
        self.ui.pushButton_6.clicked.connect(lambda:self.压缩图片1("直接"))
        self.ui.pushButton_7.clicked.connect(lambda:self.压缩图片2("直接"))
        self.ui.pushButton_9.clicked.connect(self.一键打包)
        self.ui.pushButton_11.clicked.connect(self.去图片冗余文件)
        self.ui.pushButton_14.clicked.connect(self.转md中所有图片路劲为绝对)
        self.ui.pushButton_16.clicked.connect(self.转文件夹中md中所有图片路劲为绝对)
        self.ui.pushButton_17.clicked.connect(self.转文件夹中md中所有图片路劲为相对)
        self.ui.pushButton_18.clicked.connect(self.转md中所有图片路劲为相对)
        self.ui.pushButton_12.clicked.connect(self.去文件夹内md冗余图片)
        self.ui.pushButton_19.clicked.connect(self.检查文件夹内md文件的图片完整性)
        self.ui.pushButton_20.clicked.connect(self.换名字)
    def 换名字(self):
        md文件路劲 = QFileDialog.getOpenFileName()[0]
        md文件目录= os.path.dirname(md文件路劲)
        md文件名=os.path.basename(md文件路劲)
        print(md文件名)
        if md文件路劲:
            新名字, ok = QInputDialog.getText(None, '输入新名字不用加.md', '请输入新的文件夹名称:')
            if ok and 新名字:
                新文件路劲 = os.path.join(md文件目录, 新名字 + ".md")
                with open(md文件路劲, 'r', encoding='utf-8') as 文件: md文件内容 = 文件.read()
                所有图片路劲=self.返回图片们文件路劲(md文件内容)
                获取其中一个路劲=os.path.dirname(所有图片路劲[0])
                # 检查是否绝对路劲
                if os.path.isabs(获取其中一个路劲):
                    print('发生错误,图片路劲是绝对路劲，不可转')
                    return
                # 转为绝对路劲以获取图片们的文件夹绝对目录
                # 必须同md文件目录下
                文件夹绝对目录=os.path.join(md文件目录,md文件名[:-3]+'.assets')
                新文件夹绝对目录=os.path.join(md文件目录, 新名字 + '.assets')
                # java maven.assets 把这个换为要改的

                # 改文件名
                os.rename(md文件路劲, 新文件路劲)
                # 改图片文件夹
                os.rename(文件夹绝对目录, 新文件夹绝对目录)
                # 改文件里图片的路劲
                md新文件内容=md文件内容.replace(md文件名[:-3]+'.assets',新名字+'.assets')
                # 重新写进文件
                with open(新文件路劲, 'w', encoding='utf-8') as 文件: 文件.write(md新文件内容)
                print('更改名字成功')


    def 检查文件夹内md文件的图片完整性(self):
        文件夹路劲 = QFileDialog.getExistingDirectory(caption="选定md文件们所在文件夹")
        if 文件夹路劲:
            md文件列表 = [os.path.join(文件夹路劲, 文件) for 文件 in os.listdir(文件夹路劲) if 文件.endswith(".md")]
            不完整的md个数=0
            for md文件路劲 in md文件列表:
                with open(md文件路劲, 'r', encoding='utf-8') as 文件: 文件内容 = 文件.read()
                所有图片们路劲 = self.返回图片们文件路劲(文件内容)
                for 路劲 in 所有图片们路劲:
                    if not os.path.exists(路劲):
                        路劲=os.path.join( os.path.dirname(md文件路劲), 路劲)
                    有效路径 = os.path.normpath(路劲)
                    if not os.path.exists(有效路径):
                        不完整的md个数+=1
                        print(f"{md文件路劲}中的{有效路径}图片不存在！")
            if 不完整的md个数:
                QMessageBox.information(self.ui, "成功检查", f"有{不完整的md个数}个不完整！！")
            else:
                QMessageBox.information(self.ui, "成功检查", "所有md文件中的图片都完整！")


    def 去文件夹内md冗余图片(self):
        # 提取md文件中所有图片
        # 检查默认assets文件夹是否存在，如果存在，判断有没有多余的图片（当前图片路劲不在 所有图片列表中）
        文件夹路劲 = QFileDialog.getExistingDirectory(caption="选定md文件们所在文件夹")
        if 文件夹路劲:
            md文件列表 = [os.path.join(文件夹路劲, 文件) for 文件 in os.listdir(文件夹路劲) if 文件.endswith(".md")]
            for 文件路劲 in md文件列表:
                文件路劲=os.path.normpath(文件路劲)
                with open(文件路劲, 'r', encoding='utf-8') as 文件:
                    文件内容 = 文件.read()
                所有图片们路劲 =self.返回图片们文件路劲(文件内容)
                if any('.assets' in i for i in 所有图片们路劲):
                    # 获取assets文件中所有图片
                    md文件名=os.path.splitext(os.path.basename(文件路劲))[0]
                    assets文件夹路劲=os.path.join(os.path.dirname(文件路劲),f'{md文件名}.assets')
                    assets文件夹中所有图片=os.listdir(assets文件夹路劲)
                    for i in assets文件夹中所有图片:
                        文件名和类型 = os.path.basename(i)
                        if any(文件名和类型 in i for i in 所有图片们路劲):continue
                        else:
                            print('当前是冗余文件',os.path.join(assets文件夹路劲,文件名和类型))
                            os.remove(os.path.join(assets文件夹路劲,文件名和类型))
                # if len(所有图片们路劲) == 0:
                #     continue
                # # 一个图片文件夹路劲
                # 某一个图片所在文件夹路劲 = os.path.dirname(所有图片们路劲[0])
                # # 可能是相对路径，转为绝对路径
                # if not os.path.isabs(某一个图片所在文件夹路劲):
                #     某一个图片所在文件夹路劲 = os.path.join(os.path.dirname(文件路劲), 某一个图片所在文件夹路劲)
                # # 把全部路劲转为全部（图片名字）
                # 所有图片们名字 = [self.返回一个图片所有的名字(图片的路劲) for 图片的路劲 in 所有图片们路劲]
                # 路劲内所有图片 = os.listdir(某一个图片所在文件夹路劲)
                # # 删除不在md中的图片
                # 删除图片的个数 = 0
                # try:
                #     for 文件名 in 路劲内所有图片:
                #         文件完整路劲 = os.path.join(某一个图片所在文件夹路劲, 文件名)
                #         if 文件名 not in 所有图片们名字 and 文件名.endswith('.png'):
                #             删除图片的个数 += 1
                #             os.remove(文件完整路劲)
                #     print(f"{文件路劲},已成功删除{删除图片的个数}冗余文件！")
                #     记录成功去除冗余的文件列表[os.path.basename(文件路劲)]=删除图片的个数
                # except:
                #     pass
                    # QMessageBox.information(self.ui, "去冗余文件失败", "删除冗余文件失败！")
                #############
            # # 记录成功去除冗余的文件列表按照删除的个数排序
            # 记录成功去除冗余的文件列表=sorted(记录成功去除冗余的文件列表.items(), key=lambda x: x[1], reverse=True)
            # 输出格式=""
            # for k,v in 记录成功去除冗余的文件列表:
            #     输出格式 += f"删除了{v:^3}个       {k:}\n"
            # QMessageBox.information(self.ui, f"去冗余文件成功{len(md文件列表)}", f"{输出格式}")
    def 转md中所有图片路劲为绝对(self):QMessageBox.information(self.ui, "还没开发此功能","还没开发此功能")
    def 转文件夹中md中所有图片路劲为绝对(self):QMessageBox.information(self.ui, "还没开发此功能","还没开发此功能")
    def 转md中所有图片路劲为相对(self):
        选定md文件路劲 = QFileDialog.getOpenFileName()[0]
        选定md文件名=os.path.basename(选定md文件路劲)
        if 选定md文件路劲:
            选定文件夹 = QFileDialog.getExistingDirectory(caption="选择assets所在文件夹")
            if 选定文件夹:
                with open(选定md文件路劲, 'r', encoding='utf-8') as 文件: md文件内容 = 文件.read()
                所有图片路劲 = self.返回图片们文件路劲(md文件内容)
                for 每个图片路劲 in 所有图片路劲:
                    图片名字 = os.path.basename(每个图片路劲)
                    try:
                        所在路劲=选定文件夹 + "/" + os.path.basename(选定md文件路劲)[:-3] + ".assets"
                        图片名字 in os.listdir(选定文件夹 + "/" + os.path.basename(选定md文件路劲)[:-3] + ".assets")
                    except: continue
                    # 如果图片在相应的assets文件夹中
                    if 图片名字 in os.listdir(选定文件夹 + "/" + os.path.basename(选定md文件路劲)[:-3] + ".assets"):
                        md文件所在文件夹=os.path.dirname(选定md文件路劲)
                        相对路劲 = os.path.relpath(选定文件夹, md文件所在文件夹).replace("\\", "/")
                        当前文件名字 = os.path.basename(选定md文件路劲)[:-3]
                        新路劲 = f"{相对路劲}/{当前文件名字}.assets/{图片名字}"
                        文件内容 = 文件内容.replace(每个图片路劲, 新路劲)
                        # print(f"已替换{md文件}中的{图片的路劲}为{新路劲}")
                # 写回修改后的文件内容
                with open(选定md文件路劲, 'w', encoding='utf-8') as 文件:
                    文件.write(文件内容)
                print(f"更新文件: {选定md文件路劲}")

        pass

        # 选定文件夹1 = QFileDialog.getExistingDirectory(caption="选定md文件们所在文件夹")
        # if 选定文件夹1:
        #     选定文件夹2 = QFileDialog.getExistingDirectory(caption="选定assets文件们所在文件夹")
        #     if 选定文件夹2:
        #         # 读取文件夹所有的md文件
        #         md文件列表 = [os.path.join(选定文件夹1, 文件) for 文件 in os.listdir(选定文件夹1) if
        #                       文件.endswith(".md")]
        #         for md文件 in md文件列表:
        #             # 读取文件的所有图片路劲
        #             with open(md文件, 'r', encoding='utf-8') as 文件:
        #                 文件内容 = 文件.read()
        #             所有图片文件路劲 = self.返回图片们文件路劲(文件内容)
        #             # 把全部路劲转为相对路劲
        #             for 图片的路劲 in 所有图片文件路劲:
        #                 # 获取图片名
        #                 图片名字 = os.path.basename(图片的路劲)
        #                 try:
        #                     图片名字 in os.listdir(选定文件夹2 + "/" + os.path.basename(md文件)[:-3] + ".assets")
        #                 except:
        #                     # 如果不存在图片，处理下一个图片路劲
        #                     continue
        #                 # 如果图片在相应的assets文件夹中
        #                 if 图片名字 in os.listdir(选定文件夹2 + "/" + os.path.basename(md文件)[:-3] + ".assets"):
        #                     相对路劲 = os.path.relpath(选定文件夹2, 选定文件夹1).replace("\\", "/")
        #                     当前文件名字 = os.path.basename(md文件)[:-3]
        #                     新路劲 = f"{相对路劲}/{当前文件名字}.assets/{图片名字}"
        #                     文件内容 = 文件内容.replace(图片的路劲, 新路劲)
        #                     # print(f"已替换{md文件}中的{图片的路劲}为{新路劲}")
        #             # 写回修改后的文件内容
        #             with open(md文件, 'w', encoding='utf-8') as 文件:
        #                 文件.write(文件内容)
        #
        #             print(f"更新文件: {md文件}")
        #
        #         pass
        #
        # pass
    def 返回图片们文件路劲(self,文件内容)->list[str]:
        '''
        提取typora所有文件里的图片路劲
        :param 文件内容:
        :return: 所有图片文件路劲 组成的一个列表
        '''
        # ![image-20240406193917757](java maven.assets/image-20240406193917757.png)
        匹配文件中所有图片路劲 = r"\!\[.*\]\((.*)\)"
        # 返回
        所有图片文件路劲 = re.findall(匹配文件中所有图片路劲, 文件内容)
        匹配文件中所有图片路劲2=r"<img src=\"(.*?)\""
        所有图片文件路劲2 = re.findall(匹配文件中所有图片路劲2, 文件内容)
        所有路径 = 所有图片文件路劲 + 所有图片文件路劲2

        # 过滤掉http和https开头的路径
        过滤后的路径 = [路径 for 路径 in 所有路径 if not 路径.lower().startswith(('http://', 'https://'))]
        # 给所有路劲normal
        过滤后的路径=[os.path.normpath(路径) for 路径 in 所有路径 ]

        return 过滤后的路径
    def 返回一个图片所有的名字(self,图片的路劲:str)->str:
        '''
        返回路劲中文件名
        :param 图片的路劲:
        :return: 文件名
        '''
        return os.path.basename(图片的路劲)

    def 转文件夹中md中所有图片路劲为相对(self):
        选定文件夹1 = QFileDialog.getExistingDirectory(caption="选定md文件们所在文件夹")
        if 选定文件夹1:
            选定文件夹2 = QFileDialog.getExistingDirectory(caption="选定assets文件们所在文件夹")
            if 选定文件夹2:
                # 读取文件夹所有的md文件
                md文件列表 = [os.path.join(选定文件夹1, 文件) for 文件 in os.listdir(选定文件夹1) if
                              文件.endswith(".md")]
                处理md文件后的列表= {}
                for md文件 in md文件列表:
                    md文件名字=os.path.basename(md文件)
                    处理md文件后的列表[md文件名字]=0
                    是否要处理 = False
                    # 读取文件的所有图片路劲
                    with open(md文件, 'r', encoding='utf-8') as 文件:
                        文件内容 = 文件.read()
                    所有图片文件路劲=self.返回图片们文件路劲(文件内容)
                    # 把全部路劲转为相对路劲
                    for 图片的路劲 in 所有图片文件路劲:
                        # 获取图片名
                        图片名字 = os.path.basename(图片的路劲)
                        try:
                            图片名字 in os.listdir(选定文件夹2+"/"+os.path.basename(md文件)[:-3]+".assets")
                        except:
                            #如果不存在图片，处理下一个图片路劲
                            continue
                        #如果图片在相应的assets文件夹中
                        if 图片名字 in os.listdir(选定文件夹2+"/"+os.path.basename(md文件)[:-3]+".assets"):
                            相对路劲 = os.path.relpath(选定文件夹2,选定文件夹1).replace("\\","/")
                            当前文件名字 = os.path.basename(md文件)[:-3]
                            新路劲= f"{相对路劲}/{当前文件名字}.assets/{图片名字}"
                            文件内容 = 文件内容.replace(图片的路劲, 新路劲)
                            if 图片的路劲==新路劲:
                                continue
                            是否要处理=True
                            处理md文件后的列表[md文件名字]+=1
                            # print(f"已替换{md文件}中的{图片的路劲}为{新路劲}")
                    # 写回修改后的文件内容
                    if 是否要处理:
                        with open(md文件, 'w', encoding='utf-8') as 文件:
                            文件.write(文件内容)
                        print(f"更新文件: {md文件}")
                #记录处理了多少个文件
                处理md文件后的列表=sorted(处理md文件后的列表.items(), key=lambda x: x[1], reverse=True)
                消息的文本=""
                for k,v in 处理md文件后的列表:
                    消息的文本+= f"处理了{v:^5}个   文件名：{k:}\n"
                QMessageBox.information(self.ui, f"成功处理{len(处理md文件后的列表)}个文件", f"{消息的文本}")

                pass

        pass
    def 去图片冗余文件(self):
        文件路劲 = QFileDialog.getOpenFileName()[0]
        if 文件路劲:
            # 读取文件的所有图片路劲
            with open(文件路劲, 'r', encoding='utf-8') as 文件: 文件内容 = 文件.read()
            所有图片们路劲=self.返回图片们文件路劲(文件内容)
            print(len(所有图片们路劲))
            for 图片的路劲 in 所有图片们路劲:
                print(图片的路劲)
            if len(所有图片们路劲)==0:
                QMessageBox.information(self.ui, "去冗余文件失败", "没有找到任何图片！")
                return
            print(所有图片们路劲[0])
            # 一个图片文件夹路劲
            某一个图片所在文件夹路劲=os.path.dirname(所有图片们路劲[0])
            # 可能是相对路径，转为绝对路径
            if not os.path.isabs(某一个图片所在文件夹路劲):
                某一个图片所在文件夹路劲=os.path.join(os.path.dirname(文件路劲),某一个图片所在文件夹路劲)
            # 把全部路劲转为全部（图片名字）
            所有图片们名字=[self.返回一个图片所有的名字(图片的路劲) for 图片的路劲 in 所有图片们路劲]
            路劲内所有图片=os.listdir(某一个图片所在文件夹路劲)
            # 删除不在md中的图片
            选择 = QMessageBox.question(
                self.ui,
                '是否确认删除',
                f'路劲文件总共{len(路劲内所有图片)} 需求图片总共{len(所有图片们名字)}')
            if 选择 == QMessageBox.No: return
            删除图片的个数=0
            if 选择 == QMessageBox.Yes:
                try:
                    for 文件名 in 路劲内所有图片:
                        文件完整路劲 = os.path.join(某一个图片所在文件夹路劲, 文件名)
                        if 文件名 not in 所有图片们名字 and 文件名.endswith('.png'):
                            删除图片的个数+=1
                            os.remove(文件完整路劲)
                    QMessageBox.information(self.ui, "去冗余文件成功",
                                            f"已成功删除{删除图片的个数}冗余文件！")
                except:
                    QMessageBox.information(self.ui, "去冗余文件失败", "删除冗余文件失败！")
    def 一键打包(self):
        开始时间=time.time()
        try:
            self.压缩md文件(),self.压缩图片1(),self.压缩图片2()
            QMessageBox.information(self.ui, "一键打包成功", f"一键打包成功！ 花了{int(time.time()-开始时间)}秒")
        except:
            QMessageBox.information(self.ui, "一键打包失败", f"一键打包失败！ 花了{int(time.time()-开始时间)}秒")
    def 压缩图片2(self,直接="不直接"):
        global 图片路劲md_assets, 打包后的路劲, md图片2压缩包名字
        所有文件夹 = [d for d in os.listdir(图片路劲md_assets) if os.path.isdir(os.path.join(图片路劲md_assets, d)) and '.assets' in d]
        文件夹路径列表 = [os.path.join(图片路劲md_assets, 文件夹) for 文件夹 in 所有文件夹]
        zip文件名 = os.path.join(打包后的路劲, f"{md图片2压缩包名字}.zip")
        try:
            with zipfile.ZipFile(zip文件名, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for 文件夹路径 in 文件夹路径列表:
                    for 文件 in glob.glob(os.path.join(文件夹路径, "*.png")):
                        # 为了保持文件的目录结构，我们使用相对路径
                        相对路径 = os.path.relpath(文件, start=文件夹路径)
                        zipf.write(文件, arcname=os.path.join(os.path.basename(文件夹路径), 相对路径))
            if(直接=="直接"):QMessageBox.information(self.ui, "压缩成功", "所有PNG图片已成功压缩！")
        except Exception as e:
            if(直接=="直接"):QMessageBox.information(self.ui, "压缩失败", f"压缩PNG图片失败！原因: {e}")
    def 压缩图片1(self,直接="不直接"):
        global 图片路劲,打包后的路劲,md图片1压缩包名字
        zip文件名 = os.path.join(打包后的路劲, f"{md图片1压缩包名字}.zip")  # 定义zip文件的名称和路径
        try:
            with zipfile.ZipFile(zip文件名, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for 文件 in glob.glob(os.path.join(图片路劲, "*.png")):  # 搜索所有的.png文件
                    zipf.write(文件, os.path.basename(文件))  # 将文件添加到zip
            if(直接=="直接"):QMessageBox.information(self.ui, "压缩成功", "所有PNG图片已成功压缩！")
        except:
            if(直接=="直接"):QMessageBox.information(self.ui, "压缩失败", "压缩PNG图片失败！")
        pass
    def 压缩md文件(self,直接="不直接"):
        try:
            global md文件路劲,打包后的路劲,md文件压缩包名字
            zip文件名 = os.path.join(打包后的路劲, f"{md文件压缩包名字}.zip")  # 定义zip文件的名称和路径
            with zipfile.ZipFile(zip文件名, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for 文件 in glob.glob(os.path.join(md文件路劲, "*.md")):  # 搜索所有的.md文件
                    zipf.write(文件, os.path.basename(文件))  # 将文件添加到zip文件中
            if(直接=="直接"):QMessageBox.information(self.ui, "压缩成功", "所有MD文件已成功压缩！")
        except:
            if (直接 == "直接"):QMessageBox.information(self.ui, "压缩失败", "所有MD文件压缩失败！")

    def 保存路劲(self):
        global_vars = [
            "md文件路劲", "图片路劲", "图片路劲md_assets",
            "md压缩包名字", "打包后的路劲",
            "md文件压缩包名字", "md图片1压缩包名字", "md图片2压缩包名字"
        ]
        text_edits = [
            self.ui.textEdit, self.ui.textEdit_2, self.ui.textEdit_3,
            self.ui.textEdit_4, self.ui.textEdit_7,
            self.ui.textEdit_4, self.ui.textEdit_5, self.ui.textEdit_6
        ]

        with open("记忆路劲.txt", "w", encoding="utf-8") as file:
            for var, text_edit in zip(global_vars, text_edits):
                value = text_edit.toPlainText()
                file.write(f"{var}: {value}\n")
                globals()[var] = value
            QMessageBox.information(self.ui, "保存成功", "路劲信息已成功保存！")
        self.参数初始化()

    def 参数初始化(self):
        global_vars = [
            "md文件路劲", "图片路劲", "图片路劲md_assets",
            "md压缩包名字", "打包后的路劲",
            "md文件压缩包名字", "md图片1压缩包名字", "md图片2压缩包名字"
        ]
        text_edits = [
            self.ui.textEdit, self.ui.textEdit_2, self.ui.textEdit_3,
            self.ui.textEdit_4, self.ui.textEdit_7,
            self.ui.textEdit_4, self.ui.textEdit_5, self.ui.textEdit_6
        ]
        with open("记忆路劲.txt", "r", encoding="utf-8") as file:
            for i, line in enumerate(file):
                value = line.strip().split(": ")[1]
                globals()[global_vars[i]] = value
                text_edits[i].setText(value)

    def 打开文件夹(self, 模式):
        file_paths = {
            "md文件路劲": (self.ui.textEdit, "md文件路劲"),
            "图片路劲": (self.ui.textEdit_2, "图片路劲"),
            "图片路劲md_assets": (self.ui.textEdit_3, "图片路劲md_assets"),
            "打包后的路劲": (self.ui.textEdit_7, "打包后的路劲"),
        }
        if 模式 in file_paths:
            text_edit, global_var_name = file_paths[模式]
            file_path = QFileDialog.getExistingDirectory()
            if file_path:
                text_edit.setText(file_path)
                globals()[global_var_name] = file_path

if __name__ == '__main__':
    app = QApplication([])
    stats = Stats()
    stats.ui.show()
    app.exec_()