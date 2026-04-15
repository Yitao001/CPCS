"""
为整个工程提供统一的绝对路径
"""
import os

def get_project_root() -> str:
    """
    获取工程所在根目录
    :return: 字符串根目录
    """
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    poject_root = os.path.dirname(current_dir)
    #字符串根目录
    return poject_root


def get_abs_path(relative_path: str) -> str:
    """
    :param relative_path: 相对路径
    :return: 绝对路径
    """
    return os.path.join(get_project_root(), relative_path)



if __name__ == '__main__':
    print(get_abs_path("path_tool.py"))