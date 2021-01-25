class DefaultConfig:
    def __init__(self):
        # major 路径，在 wsl 下调用
        self.major_path = '/mnt/d/major/bin'
        # c# 编译器路径
        self.csc_path = 'D:/Program Files (x86)/Microsoft Visual Studio/Shared/Packages/Microsoft.Net.Compilers.2.6.1/tools'
        # java 路径，目前临时用的 java->c# 转换器要求 jre7
        self.java_path = 'C:/Program Files/Java/jre7/bin'
        # pex 路径
        self.pex_path = 'C:/Program Files (x86)/Microsoft Pex/bin'


def load_config():
    return DefaultConfig()