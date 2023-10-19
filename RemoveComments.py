bl_info = {
    "name" : "Remove Comments",
    "author" : "chenpaner", 
    "description" : "Remove .py Comments",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "3Dview > Nplane > Tool/Remove Comments",
    "warning" : "",
    "doc_url": "https://github.com/chenpaner", 
    "tracker_url": "", 
    "category" : "Development" 
}

import bpy
import re

class SNA_PT_RemoveCommentsPanel_367E1(bpy.types.Panel):
    bl_label = "Remove Comments"
    bl_idname = "SNA_PT_RemoveCommentsPanel_367E1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "remove_comments_filepath")
        row = layout.row()
        row.operator("script.remove_comments_operator_tail", text="Remove End Comments")
        row = layout.row()
        row.operator("script.remove_comments_operator_lines", text="Remove Entire Comment")

        row = layout.row()
        row.prop(context.scene, "remove_keyword_line")
        row.operator("script.remove_sn_lines_operator", text="Remove keyword Lines")
        row = layout.row()
        row.operator("script.remove_blank_lines_operator", text="Remove Blank Lines")

        row = layout.row()
        row.operator("script.remove_comments_operator_all", text="Remove All Comments")

        row = layout.row()
        row.operator("script.remove_duplicate_lines_operator", text="Remove Duplicate Lines")

class RemoveCommentsOperatorTail(bpy.types.Operator):##仅仅删除每行尾部的注释
    bl_idname = "script.remove_comments_operator_tail"
    bl_label = "Remove Comments from Line End"
    bl_description = "Remove Comments from Line End\n仅删除每行尾部的注释"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        if filepath:
            try:
                with open(filepath, "r") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    lines[i] = re.sub(r'(?<=\S)\s*#.*$', '', line.rstrip('\n'))

                    if lines[i]:  # 如果删除注释后仍然有内容
                        self.report({'INFO'}, lines[i])  # 打印删除后的内容
                with open(filepath, "w") as f:
                    f.writelines('\n'.join(lines))
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
                with open(filepath, "r") as f:
                    content = f.read()
                deleted_lines = re.findall(r'^\s*#.*\n', content, flags=re.MULTILINE)
                content = re.sub(r'^\s*#.*\n', '', content, flags=re.MULTILINE)
                with open(filepath, "w") as f:
                    f.write(content)
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
    bl_description = "Remove lines containing ''\n删除包含...的行"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        keyword = context.scene.remove_keyword_line
        if filepath:
                with open(filepath, "r") as f:
                    lines = f.readlines()
                deleted_lines = [line for line in lines if str(keyword, "utf-8") in line]
                lines = [line for line in lines if str(keyword, "utf-8") not in line]
                with open(filepath, "w") as f:
                    f.writelines(lines)
                for deleted_line in deleted_lines:
                    self.report({'INFO'}, deleted_line.strip())

                deleted_lines_count = len(deleted_lines)
                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines containing '{keyword}' from {filepath}")
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
                with open(filepath, "r") as f:
                    content = f.read()
                content = re.sub(r'\n\s*\n', '\n', content)
                with open(filepath, "w") as f:
                    f.write(content)
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
                with open(filepath, "r") as f:
                    content = f.read()
                deleted_lines = re.findall(r'#.*', content)
                content = re.sub(r'#.*', '', content)
                with open(filepath, "w") as f:
                    f.write(content)
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
    bl_description = "Remove completely duplicate lines\n删除完全重复的行保留第一个重复行"

    def execute(self, context):
        filepath = context.scene.remove_comments_filepath
        if filepath:
            try:
                with open(filepath, "r") as f:#, encoding="utf-8"
                    lines = f.readlines()
                unique_lines = []  # 存储不重复的行
                seen_lines = set()  # 存储已经看过的行

                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line not in seen_lines:
                        seen_lines.add(stripped_line)
                        unique_lines.append(line)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(unique_lines)
                deleted_lines_count = len(lines) - len(unique_lines)
                self.report({'INFO'}, f"Deleted {deleted_lines_count} lines with the same content from {filepath}")


            except Exception as e:
                self.report({'ERROR'}, "Error removing lines: " + str(e))
        else:
            self.report({'ERROR'}, "No file selected")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SNA_PT_RemoveCommentsPanel_367E1)
    bpy.utils.register_class(RemoveCommentsOperatorTail)
    bpy.utils.register_class(RemoveCommentsOperatorLines)
    bpy.utils.register_class(RemoveSNLinesOperator)
    bpy.utils.register_class(RemoveBlankLinesOperator)
    bpy.utils.register_class(RemoveCommentsOperatorAll)
    bpy.utils.register_class(RemoveDuplicateLinesOperator)
    bpy.types.Scene.remove_comments_filepath = bpy.props.StringProperty(
        subtype='FILE_PATH',
        description="Python File",
    )
    bpy.types.Scene.remove_keyword_line = bpy.props.StringProperty(
        name='', description='keyword', default='', subtype='BYTE_STRING')

def unregister():
    bpy.utils.unregister_class(SNA_PT_RemoveCommentsPanel_367E1)
    bpy.utils.unregister_class(RemoveCommentsOperatorTail)
    bpy.utils.unregister_class(RemoveCommentsOperatorLines)
    bpy.utils.unregister_class(RemoveSNLinesOperator)
    bpy.utils.unregister_class(RemoveBlankLinesOperator)
    bpy.utils.unregister_class(RemoveCommentsOperatorAll)
    bpy.utils.unregister_class(RemoveDuplicateLinesOperator)
    del bpy.types.Scene.remove_comments_filepath
    del bpy.types.Scene.remove_keyword_line

if __name__ == "__main__":
    register()
