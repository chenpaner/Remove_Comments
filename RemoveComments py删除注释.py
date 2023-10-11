bl_info = {
    "name" : "Remove Comments py删除注释",
    "author" : "chenpaner", 
    "description" : "Remove .py Comments",
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

class SNA_PT_RemoveCommentsPanel_367E1(bpy.types.Panel):
    bl_label = "删除注释"
    bl_idname = "SNA_PT_RemoveCommentsPanel_367E1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "remove_comments_filepath")
        row = layout.row()
        row.operator("script.remove_comments_operator_tail", text="仅删行尾注释")
        row = layout.row()
        row.operator("script.remove_comments_operator_lines", text="删除整行注释")
        row = layout.row()
        row.operator("script.remove_blank_lines_operator", text="删除空行")
        row = layout.row()
        row.operator("script.remove_comments_operator_all", text="删除所有注释")

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

                deleted_lines_count = 0

                for i, line in enumerate(lines):
                    lines[i] = re.sub(r'(?<=\S)\s*#.*$', '', line.rstrip('\n'))

                    if lines[i]:  # 如果删除注释后仍然有内容
                        self.report({'INFO'}, lines[i])  # 打印删除后的内容
                        deleted_lines_count += 1

                # 写回文件
                with open(filepath, "w") as f:
                    f.writelines('\n'.join(lines))

                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines of comments from {filepath}")

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

                # 使用正则表达式删除整行都是注释的行
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

class RemoveBlankLinesOperator(bpy.types.Operator):
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

def register():
    bpy.utils.register_class(SNA_PT_RemoveCommentsPanel_367E1)
    bpy.utils.register_class(RemoveCommentsOperatorTail)
    bpy.utils.register_class(RemoveCommentsOperatorLines)
    bpy.utils.register_class(RemoveBlankLinesOperator)
    bpy.utils.register_class(RemoveCommentsOperatorAll)
    bpy.types.Scene.remove_comments_filepath = bpy.props.StringProperty(
        subtype='FILE_PATH',
        description="Python File",
    )

def unregister():
    bpy.utils.unregister_class(SNA_PT_RemoveCommentsPanel_367E1)
    bpy.utils.unregister_class(RemoveCommentsOperatorTail)
    bpy.utils.unregister_class(RemoveCommentsOperatorLines)
    bpy.utils.unregister_class(RemoveBlankLinesOperator)
    bpy.utils.unregister_class(RemoveCommentsOperatorAll)
    del bpy.types.Scene.remove_comments_filepath

if __name__ == "__main__":
    register()
