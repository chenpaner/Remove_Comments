bl_info = {
    "name" : "Remove Comments py删除注释,清空控制台",
    "author" : "chenpaner", 
    "description" : "Remove .py Comments,Clear System Console",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "3Dview > Nplane > Tool/删除注释",
    "warning" : "",
    "doc_url": "https://github.com/chenpaner", 
    "tracker_url": "", 
    "category" : "Development" 
}

import bpy
import re
import os
from datetime import datetime
import ast

class SimplePoExtractor(bpy.types.Operator):#
    bl_idname = "wm.simple_po_extractor"
    bl_label = "PO字典提取器"
    bl_description = "提取单词后自动保存在上面文件夹里的PY文件里"

    def execute(self, context):
        # 获取目录路径
        po_directory = context.scene.po_directory_dirpath

        # 检查目录是否存在
        if not os.path.exists(po_directory):
            self.report({'ERROR'}, "无效的目录")
            return {'CANCELLED'}

        # 获取当前时间
        current_time = datetime.now()
        # 将时间格式化为字符串，例如：2023-12-20_15-30-45
        formatted_time = current_time.strftime("%m-%d_%H-%M-%S")

        # 获取目录的名称（使用os.path.split获取路径的上一级目录，再使用os.path.basename获取文件夹名）
        _, directory_name = os.path.split(os.path.dirname(po_directory))
        #self.report({'INFO'}, f"路径: {po_directory}")#路径: C:\Users\CP\Desktop\devTools-master - 副本\
        #self.report({'INFO'}, f"文件: {directory_name}")#文件: devTools-master - 副本
        # 递归遍历目录中的每个文件
        for root, dirs, files in os.walk(po_directory):
            for filename in files:
                if filename.endswith(".py"):
                    file_path = os.path.join(root, filename)

                    # 在处理每个Python文件时报告文件名
                    #self.report({'INFO'}, f"找到Python文件: {os.path.basename(file_path)}")

                    # 从Python文件中提取文本
                    extracted_text = self.extract_text(file_path)#提取等号后明确文本信息，缺少三个```操作符说明```的提取
                    extracted_item = self.extract_items(file_path)#尝试提取items里每项的第2/3个文本

                    # 在PO目录中创建一个与目录名相关的新Python文件
                    new_file_name = f"{formatted_time}_{directory_name}_po.py"
                    new_file_path = os.path.join(po_directory, new_file_name)

                    # 将提取的文本写入新文件
                    with open(new_file_path, 'a', encoding='utf-8') as new_file:
                        new_file.write(extracted_text)
                        new_file.write(extracted_item)

        #自动将文件设置为下面操作的路径                
        context.scene.remove_comments_filepath = new_file_path

        self.report({'INFO'}, "提取完成")
        try:
            # 使用 DEV_OT_open_in_editor 打开新创建的 Python 文件
            bpy.ops.dev.open_in_editor(filepath=new_file_path, use_folder=False)
        except:
            self.report({'INFO'}, "在偏好设置里设置默认文本编辑器后才会自动打开该文件！")
            #print('在偏好设置里设置默认文本编辑器后才会自动打开该文件！')
            pass
 
        return {'FINISHED'}

    def extract_text(self, file_path):
        # 打开Python文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as py_file:
            content = py_file.read()

        # 使用正则表达式查找双引号之间的文本
        # 该示例假设可翻译的文本是双引号之间的任何字符串
                #pattern = re.compile(r'"([^"]*)"'):
                    # re.compile 是将正则表达式编译为正则对象的函数。
                    # r'"([^"]*)"' 是一个原始字符串（以 r 开头），表示一个正则表达式模式。
                    # " 匹配双引号。
                    # ([^"]*) 是一个捕获组，用于匹配除了双引号之外的任意字符零次或多次。[^"] 表示除了双引号之外的任意字符。* 表示零次或多次重复。

                # extracted_text = pattern.findall(content):
                    # pattern 是上一行中编译得到的正则对象。
                    # findall 方法用于在字符串中查找所有匹配正则表达式的子串，并返回一个包含所有匹配项的列表。
                    # content 是包含 Python 文件内容的字符串。
                    # 因此，extracted_text 将包含所有被双引号包围的文本的列表。

        # 使用正则表达式查找匹配指定条件的字符串
        #pattern = re.compile(r'(bl_label|bl_description|name|description|text)\s*=\s*[\'"]([^\'"]*)[\'"]')
        #pattern = re.compile(r'(bl_label|bl_description|name|description|text)\s*=\s*(?P<quote>[\'"])(.*?)(?<!\\)(?P=quote)')
        pattern = re.compile(r'\b(bl_label|bl_description|name|description|text)\s*=\s*([\'"])(.*?)(?<!\\)\2')

        matches = pattern.findall(content)

        # 将匹配到的字符串格式化返回
        #quote 代表匹配到的字符串中的引号字符，即 ' 或 "
        extracted_text = ''
        for key, quote, value in matches:
            if value:#通过上面的内容筛选后不是空的，避免有的写text=""会导致空的字典
                if key == 'bl_label':
                    extracted_text += f'#位置{os.path.basename(file_path)}\n#原文{key} = {quote}{value}{quote}\nmsgctxt "Operator"\nmsgid "{value}"\nmsgstr ""\n\n'
                else:
                    extracted_text += f'#位置{os.path.basename(file_path)}\n#原文{key} = {quote}{value}{quote}\nmsgid "{value}"\nmsgstr ""\n\n'
        #self.report({'INFO'}, f"文件: {extracted_text}")
        return extracted_text

    def extract_items(self, file_path):
        # 打开Python文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as py_file:
            content = py_file.read()

        # 获取显示文本和描述
        extracted_item = ''

        # 使用正则表达式查找以items=开头的列表或元组
        pattern = re.compile(r'items\s*=\s*(\[.*?\]|\(.*?\))', re.DOTALL)
        matches = pattern.findall(content)

        # 处理匹配结果，去除每个圆括号内的换行符
        cleaned_matches = [match.replace('\n', ' ') for match in matches]
        #self.report({'INFO'}, f"py文件列表: {cleaned_matches}")###------以每个py文件为单位获取的列表，但列表里只有一项，整个文本都作为一整项
        # 确保 cleaned_matches 列表非空
        if cleaned_matches:
            # 获取第一个元素
            string_representation = cleaned_matches[0]
            
            # 使用 ast.literal_eval() 将字符串转换为实际的 Python 数据结构
            try:
                python_data_structure = ast.literal_eval(string_representation)
                #self.report({'INFO'}, f"转换后的 Python 数据结构: {python_data_structure}")
                #self.report({'INFO'}, f"转换后的11111111数据结构: {python_data_structure[0]}")
                #self.report({'INFO'}, f"转换后的22222222数据结构: {python_data_structure[1]}")
                for item_match in python_data_structure:
                    # self.report({'INFO'}, f"item_match00: {item_match}")
                    # self.report({'INFO'}, f"display_text: {item_match[1]}")
                    # self.report({'INFO'}, f"description_text: {item_match[2]}")

                    display_text=item_match[1]
                    description_text=item_match[2]
                    # 输出显示文本的PO格式
                    if display_text is not None:
                        extracted_item += f'#所在位置{os.path.basename(file_path)}\nmsgid "{display_text}"\nmsgstr ""\n\n'

                    # 输出描述文本的PO格式
                    if description_text is not None:
                        extracted_item += f'#所在位置{os.path.basename(file_path)}\nmsgid "{description_text}"\nmsgstr ""\n\n'
            except (SyntaxError, ValueError) as e:
                self.report({'ERROR'}, f"转换失败: {e}")
        # else:
        #     self.report({'INFO'}, "cleaned_matches 列表为空。")

        return extracted_item

class SNA_PT_RemoveCommentsPanel_367E1(bpy.types.Panel):
    bl_label = "删除注释"
    bl_idname = "SNA_PT_RemoveCommentsPanel_367E1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.label(text="PY文件处理")
        row = layout.box()
        row.prop(context.scene, "remove_comments_filepath")
        #row = layout.row()
        row.operator("script.remove_comments_operator_tail", text="仅删行尾注释")
        #row = layout.row()
        row.operator("script.remove_comments_operator_lines", text="删除整行注释")
        row.operator("script.remove_comments_operator_all", text="删除所有注释")
        row.operator("script.remove_blank_lines_operator", text="删除空行")
        row1 = row.row()
        row1.prop(context.scene, "remove_keyword_line", text="")
        row1.operator("script.remove_sn_lines_operator", text="删除包含特定字符的行")
        
        row = row.row()
        row.prop(context.scene, "custom_conditions", text="")
        row.operator("script.remove_duplicate_lines_operator", text="删除重复行")

        layout = self.layout
        layout.label(text="批量替换节点组端口里某个名词！")
        row2 = layout.box()
        #row = layout.row()
        #row2.label(text="批量替换节点组端口里某个名词！")
        row2.label(text="注意将Bl语言切换为英文检查名字！")
        row = row2.row()
        row.prop(context.scene, "replace_keyword_groupnode", text="")#, text="替换"
        row.label(text="",icon="CON_ARMATURE")
        row.prop(context.scene, "substitute_keyword_groupnode", text="")#, text="为"
        row = row2.row()
        row.operator("script.replace_keyword_groupnod_operator", text="替换端口名里关键字")
        row = row2.row()
        row.operator("script.replaceed_keyword_groupnod_operator", text="替换端口名")

        layout = self.layout
        layout.label(text="PO字典提取")
        row = layout.box()
        row.prop(context.scene, "po_directory_dirpath")
        #row = layout.row()
        row.operator("wm.simple_po_extractor")

class RemoveCommentsOperatorTail(bpy.types.Operator):##仅仅删除每行尾部的注释
    bl_idname = "script.remove_comments_operator_tail"
    bl_label = "Remove Comments from Line End"
    bl_description = "Remove Comments from Line End\n仅删除每行尾部的注释"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        if filepath:
            try:
                # 打开文件以读取内容
                with open(filepath, "r") as f:
                    lines = f.readlines()

                #deleted_lines_count = 0

                for i, line in enumerate(lines):
                    lines[i] = re.sub(r'(?<=\S)\s*#.*$', '', line.rstrip('\n'))

                    if lines[i]:  # 如果删除注释后仍然有内容
                        self.report({'INFO'}, lines[i])  # 打印删除后的内容
                        #deleted_lines_count += 1

                # 写回文件
                with open(filepath, "w") as f:
                    f.writelines('\n'.join(lines))

                # self.report({'INFO'}, f"Deleted {deleted_lines_count} lines of comments from {filepath}")
                self.report({'INFO'}, f"Deleted Comments from Line End from {filepath}")

            except Exception as e:
                self.report({'ERROR'}, "Error removing comments: " + str(e))
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}

class RemoveCommentsOperatorLines(bpy.types.Operator):##删除整行都是注释的行
    bl_idname = "script.remove_comments_operator_lines"
    bl_label = "Remove Entire Comment Lines"
    bl_description = "Remove Comments from Line End\n删除整行都是注释的行"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        if filepath:
            try:
                # 打开文件以读取内容
                with open(filepath, "r") as f:
                    content = f.read()

                # 查找匹配整行注释的内容
                deleted_lines = re.findall(r'^\s*#.*\n', content, flags=re.MULTILINE)

                # 使用正则表达式找出整行都是注释的行然后回写
                content = re.sub(r'^\s*#.*\n', '', content, flags=re.MULTILINE)

                # 写回文件
                with open(filepath, "w") as f:
                    f.write(content)

                # 打印删除的每一行内容
                for deleted_line in deleted_lines:
                    self.report({'INFO'}, deleted_line.strip())
                    
                deleted_lines_count = len(deleted_lines)
                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines of comments from {filepath}")

            except Exception as e:
                self.report({'ERROR'}, "Error removing comments: " + str(e))
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}

class RemoveSNLinesOperator(bpy.types.Operator):#删除包含 'SN_' 的行
    bl_idname = "script.remove_sn_lines_operator"
    bl_label = "Remove Lines Containing 'SN_'"
    bl_description = "Remove lines containing 'SN_'\n删除包含 'SN_' 的行"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        keyword = context.scene.remove_keyword_line
        if filepath:
            # try:
                # 打开文件以读取内容
                with open(filepath, "r") as f:
                    lines = f.readlines()

                # # 检查每一行，如果包含'SN_'，则将添加到deleted_lines列表
                deleted_lines = [line for line in lines if str(keyword, "utf-8") in line]

                # 检查每一行，找出不包含'SN_'的行将它放入lines再回写
                lines = [line for line in lines if str(keyword, "utf-8") not in line]

                # 写回文件
                with open(filepath, "w") as f:
                    f.writelines(lines)

                 # 打印删除的每一行内容
                for deleted_line in deleted_lines:
                    self.report({'INFO'}, deleted_line.strip())

                deleted_lines_count = len(deleted_lines)
                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines containing '{keyword}' from {filepath}")

            # except Exception as e:
            #     self.report({'ERROR'}, "Error removing lines: " + str(e)
            #     )
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}

class RemoveBlankLinesOperator(bpy.types.Operator):#删除所有空白行
    bl_idname = "script.remove_blank_lines_operator"
    bl_label = "Remove Blank Lines"
    bl_description = "Remove all blank lines from the file"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        if filepath:
            try:
                # 打开文件以读取内容
                with open(filepath, "r") as f:
                    content = f.read()

                # 使用正则表达式删除所有空白行
                content = re.sub(r'\n\s*\n', '\n', content)

                # 写回文件
                with open(filepath, "w") as f:
                    f.write(content)

                # 统计删除的空白行数
                deleted_lines_count = content.count('\n') - content.count('\n\n')

                self.report({'INFO'}, f"Deleted {deleted_lines_count} blank lines from {filepath}")

            except Exception as e:
                self.report({'ERROR'}, "Error removing blank lines: " + str(e))
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}

class RemoveCommentsOperatorAll(bpy.types.Operator):##删除所有注释
    bl_idname = "script.remove_comments_operator_all"
    bl_label = "Remove All Comments"
    bl_description = "Remove All Comments\n删除所有注释"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        if filepath:
            try:
                # 打开文件以读取内容
                with open(filepath, "r") as f:
                    content = f.read()

                # 使用正则表达式删除所有注释
                deleted_lines = re.findall(r'#.*', content)
                content = re.sub(r'#.*', '', content)

                # 写回文件
                with open(filepath, "w") as f:
                    f.write(content)

                # 打印删除的每一行内容
                for deleted_line in deleted_lines:
                    self.report({'INFO'}, deleted_line.strip())
                    
                deleted_lines_count = len(deleted_lines)
                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines of comments from {filepath}")

            except Exception as e:
                self.report({'ERROR'}, "Error removing comments: " + str(e))
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}

class RemoveDuplicateLinesOperator(bpy.types.Operator):##删除完全重复的行
    bl_idname = "script.remove_duplicate_lines_operator"
    bl_label = "Remove Duplicate Lines"
    bl_description = "Remove completely duplicate lines\n删除完全重复的行(排除以关键字开头的行),保留第一个重复行"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        # 获取用户输入的自定义条件字符串
        custom_conditions = context.scene.custom_conditions.split(";")
        if filepath:
            try:
                # 打开文件以读取内容
                with open(filepath, "r") as f:#, encoding="utf-8"
                    lines = f.readlines()

            #保留第一个重复行
                unique_lines = []  # 存储不重复的行
                seen_lines = set()  # 存储已经看过的行

                for line in lines:
                    # 删除行两端的空白字符以防止不同的行被认为是不同的
                    stripped_line = line.strip()

                    # 添加条件：如果某行以 custom_conditions 中的任何一个元素开头，或者是空白行就跳过这行
                    if not stripped_line or any(stripped_line.startswith(condition) for condition in custom_conditions):
                        unique_lines.append(line)

                    # 添加条件：如果某行以 custom_conditions 中的任何一个元素开头，就跳过这行
                    elif not any(stripped_line.startswith(condition) for condition in custom_conditions):
                        if stripped_line not in seen_lines:#逐行扫描后没有出现出现在已看过的里面就是保留
                            seen_lines.add(stripped_line)
                            unique_lines.append(line)

                # 写回文件
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(unique_lines)

                # 打印删除的每一行内容
                deleted_lines_count = len(lines) - len(unique_lines)
                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines with the same content from {filepath}")


          # ##保留最后一个重复行
            #     unique_lines = []  # 存储不重复的行

            #     for line in reversed(lines):
            #         # 如果行不在unique_lines中，将其添加到unique_lines
            #         if line not in unique_lines:
            #             unique_lines.insert(0, line)

            #     # 写回文件
            #     with open(filepath, "w", encoding="utf-8") as f:
            #         f.writelines(unique_lines)

            #     # 打印删除的每一行内容
            #     deleted_lines_count = len(lines) - len(unique_lines)
            #     self.report({'INFO'}, f"Deleted {deleted_lines_count} lines with the same content from {filepath}")

            except Exception as e:
                self.report({'ERROR'}, "Error removing lines: " + str(e))
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}

class ReplaceKeywordGroupnodOperator(bpy.types.Operator):#替换节点组端口包含关键字的名字
    bl_idname = "script.replace_keyword_groupnod_operator"
    bl_label = "replace_keyword_groupnod"
    bl_description = "替换所有节点组端口名里某个关键字"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        rekeyword = context.scene.replace_keyword_groupnode
        sukeyword = context.scene.substitute_keyword_groupnode
        #遍历整个blender里所有节点组，将所有节点组的输入和输出端口名字是rekeyword的全部替换为sukeyword，并最后打印多少个节点组符合条件被修改了
            # try:
        # 获取当前场景中的所有节点组
        all_node_groups = bpy.data.node_groups
        # deleted_lines_count = len(all_node_groups)
        # self.report({'INFO'}, f"发现{deleted_lines_count}个节点组")
        # self.report({'INFO'}, f"{rekeyword}")
        # 记录修改的节点组数量
        input_socket_count = 0
        output_socket_count = 0
        plane_socket_count = 0

        # 遍历所有节点组
        for node_group in all_node_groups:
            if bpy.app.version >= (4, 0, 0):
                for item in node_group.interface.items_tree:
                    if item.item_type == 'SOCKET':
                        if item.in_out == 'INPUT':
                            if rekeyword in item.name :
                                item.name = item.name.replace(rekeyword, sukeyword)
                                input_socket_count += 1
                        elif item.in_out == 'OUTPUT':
                            if rekeyword in item.name :
                                item.name = item.name.replace(rekeyword, sukeyword)
                                output_socket_count += 1
                    elif item.item_type == 'PANEL':
                        if rekeyword in item.name :
                            item.name = item.name.replace(rekeyword, sukeyword)
                            plane_socket_count += 1
            else:                
                # 遍历节点组的输入端口
                for input_socket in node_group.inputs:
                    if rekeyword in input_socket.name:
                        input_socket.name = input_socket.name.replace(rekeyword, sukeyword)
                        input_socket_count += 1

                # 遍历节点组的输出端口
                for output_socket in node_group.outputs:
                    if rekeyword in output_socket.name:
                        output_socket.name = output_socket.name.replace(rekeyword, sukeyword)
                        output_socket_count += 1

        if bpy.app.version >= (4, 0, 0):
            self.report({'INFO'}, f'完全替换{plane_socket_count}个面板.')

        # 打印修改的节点组数量
        self.report({'INFO'}, f'修改 {input_socket_count}个输入端口.')   
        self.report({'INFO'}, f'修改 {output_socket_count}个输出端口.')       

        return {'FINISHED'}

class ReplaceedKeywordGroupnodOperator(bpy.types.Operator):#替换节点组端口等于关键字的名字
    bl_idname = "script.replaceed_keyword_groupnod_operator"
    bl_label = "replace_keyword_groupnod"
    bl_description = "替换所有节点组端口完全等于关键字的名字"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        rekeyword = context.scene.replace_keyword_groupnode
        sukeyword = context.scene.substitute_keyword_groupnode
        #遍历整个blender里所有节点组，将所有节点组的输入和输出端口名字是rekeyword的全部替换为sukeyword，并最后打印多少个节点组符合条件被修改了
            # try:
        # 获取当前场景中的所有节点组
        all_node_groups = bpy.data.node_groups
        # deleted_lines_count = len(all_node_groups)
        # self.report({'INFO'}, f"发现{deleted_lines_count}个节点组")
        # self.report({'INFO'}, f"{rekeyword}")
        # 记录修改的节点组数量
        input_socket_count = 0
        output_socket_count = 0
        plane_socket_count = 0

        # 遍历所有节点组
        for node_group in all_node_groups:
            if bpy.app.version >= (4, 0, 0):
                for item in node_group.interface.items_tree:
                    if item.item_type == 'SOCKET':
                        if item.in_out == 'INPUT':
                            if item.name ==rekeyword:
                                item.name = sukeyword
                                input_socket_count += 1
                        elif item.in_out == 'OUTPUT':
                            if item.name ==rekeyword:
                                item.name = sukeyword
                                output_socket_count += 1
                    elif item.item_type == 'PANEL':
                        if item.name ==rekeyword:
                            item.name = sukeyword
                            plane_socket_count += 1
                        
            else:
                # 遍历节点组的输入端口
                for input_socket in node_group.inputs:
                    if input_socket.name ==rekeyword:
                        input_socket.name = sukeyword
                        input_socket_count += 1

                # 遍历节点组的输出端口
                for output_socket in node_group.outputs:
                    if output_socket.name==rekeyword:
                        output_socket.name = sukeyword
                        output_socket_count += 1

            

        if bpy.app.version >= (4, 0, 0):
            self.report({'INFO'}, f'完全替换{plane_socket_count}个面板.')    
        # 打印修改的节点组数量
        self.report({'INFO'}, f'完全替换{input_socket_count}个输入端口.')   
        self.report({'INFO'}, f'完全替换{output_socket_count}个输出端口.')       

        return {'FINISHED'}

class SNA_OT_ClearConsole(bpy.types.Operator):#清空控制台
    bl_idname = "sna.cpclear_console"
    bl_label = "Clear System Console"
    bl_description = "清空控制台."
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        if os.name == "nt":
            os.system("cls") 
        else:
            os.system("clear") 
        return {"FINISHED"}

def sna_add_to_topbar_mt_window_20E90(self, context):#添加到窗口栏
    if not (False):
        layout = self.layout
        op = layout.operator('sn.clear_console', text='清空控制台', icon_value=21, emboss=True, depress=False)

classes = (
    SimplePoExtractor,
    SNA_PT_RemoveCommentsPanel_367E1,
    RemoveCommentsOperatorTail,
    RemoveCommentsOperatorLines,
    RemoveSNLinesOperator,
    RemoveBlankLinesOperator,
    RemoveCommentsOperatorAll,
    RemoveDuplicateLinesOperator,
    ReplaceKeywordGroupnodOperator,
    ReplaceedKeywordGroupnodOperator,
    SNA_OT_ClearConsole,#清空控制台
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remove_comments_filepath = bpy.props.StringProperty(
        name='文件路径:',
        subtype='FILE_PATH',
        description="Python File",
    )

    bpy.types.Scene.po_directory_dirpath = bpy.props.StringProperty(
        name="插件文件夹", 
        description="自动提取文件夹里所有文本制作为po字典", 
        subtype='DIR_PATH'
    )

    bpy.types.Scene.remove_keyword_line = bpy.props.StringProperty(
        name='关键词', description='仅删除包含这个关键词的行', default='', subtype='BYTE_STRING')

    bpy.types.Scene.custom_conditions = bpy.props.StringProperty(
        name="排除开头关键字",
        description="排除以关键字开头的行，多个关键字以英文输入 ; 区分",
        default="#位置;msgstr",

    )


    #批量替换节点组端口里某个名词
    bpy.types.Scene.replace_keyword_groupnode = bpy.props.StringProperty(
        name='replace keyword', description='keyword', default='replace keyword')#, subtype='BYTE_STRING')
    bpy.types.Scene.substitute_keyword_groupnode = bpy.props.StringProperty(
        name='substitute keyword', description='keyword', default='substitute keyword')#, subtype='BYTE_STRING')

    bpy.types.TOPBAR_MT_window.append(sna_add_to_topbar_mt_window_20E90)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.remove_comments_filepath
    del bpy.types.Scene.po_directory_dirpath
    del bpy.types.Scene.remove_keyword_line
    del bpy.types.Scene.custom_conditions

    del bpy.types.Scene.replace_keyword_groupnode
    del bpy.types.Scene.substitute_keyword_groupnode

    bpy.types.TOPBAR_MT_window.remove(sna_add_to_topbar_mt_window_20E90)

if __name__ == "__main__":
    register()
