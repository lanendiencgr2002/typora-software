# 定义替换函数
def replace_string_in_file(file_path, search_string, replace_string):
    # 打开文件
    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    # 替换字符串
    contents = contents.replace(search_string, replace_string)
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(contents)

# 使用函数
file_path = '替换测试的文本.txt'  # 替换为你的文件名
search_string = 'eee'  # 替换为要搜索的旧字符串
replace_string = 'xxx'  # 替换为要替换的新字符串

# 调用函数执行替换
replace_string_in_file(file_path, search_string, replace_string)
