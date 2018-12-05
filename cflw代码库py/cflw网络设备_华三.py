import re
import ipaddress
import enum
import time
import cflw网络连接 as 连接
import cflw网络设备 as 设备
import cflw字符串 as 字符串
from 网络设备.华三_常量 import *
import 网络设备.华三_用户 as 用户
import 网络设备.华三_登陆 as 登陆
import 网络设备.华三_接口 as 接口
import 网络设备.华三_时间范围 as 时间范围
import 网络设备.华为_网络时间协议 as 网络时间协议
#===============================================================================
# 工厂
#===============================================================================
class E型号(enum.IntEnum):
	s2126 = 22126
	s3100 = 23100
	s3600 = 23600
	s3928 = 23928
	s5500 = 25500
	s6500 = 26500
	s6503 = 26503
	s7500 = 27500
	s7503 = 27503
	s7506 = 27506
	msr3600 = 33600
	sr8800 = 38800
def f创建设备(a连接, a型号 = 0, a版本 = 0):
	return C设备(a连接, a型号, a版本)
#===============================================================================
# 设备
#===============================================================================
ca错误文本与异常类 = [
	("% Unrecognized command found at '^' position.", 设备.X命令),
	("% Ambiguous command found at '^' position.", 设备.X命令)
]
class C设备(设备.I设备):
	def __init__(self, a连接, a型号, a版本):
		设备.I设备.__init__(self)
		self.fs自动换页("  ---- More ----")
		if isinstance(a连接, 连接.I连接):
			self.m连接 = a连接
			self.m连接.fs编码("gb2312")
		else:
			raise TypeError("a连接 必须是 I连接 类型")
		self.m型号 = a型号
		self.m版本 = a版本
	def f退出(self):
		self.f执行命令("quit")
	def f输入_结束符(self):
		self.f输入(c结束符 + "\r")
	def f模式_用户(self):
		self.f刷新()
		self.f输入_结束符()
		self.f输入_回车()
		v用户模式 = C用户视图(self)
		if not self.ma模式:
			self.ma模式.append(v用户模式)
		return v用户模式
	def f执行显示命令(self, a命令, a自动换页 = False):
		v命令 = str(a命令)
		v输出 = 设备.I设备.f执行显示命令(self, v命令, a自动换页)
		v输出 = 设备.C实用工具.f去头尾行(v输出)
		# if v输出.count(c换行符) < 10:
		# 	self.f检测命令异常(self, v输出)
		return v输出
	def f显示_当前模式配置(self):
		v输出 = self.f执行显示命令("display this", a自动换页 = True)
		v输出 = 设备.C实用工具.f去头尾行(v输出)
		return v输出
#===============================================================================
# 设备
#===============================================================================
class C用户视图(设备.I用户模式):
	c模式名 = "用户视图"
	def __init__(self, a设备):
		设备.I用户模式.__init__(self, a设备)
	#模式
	def f模式_全局配置(self):
		return C系统视图(self)
	#显示设备状态
	def f显示_时间(self):
		v命令 = 设备.C命令("display clock")
		v输出 = self.m设备.f执行显示命令(v命令)
		#过滤时区
		v空格位置 = 字符串.f全部搜索(v输出, " ")
		v行结束 = v输出.find(c换行符)
		if v行结束 > 0:	#如果有换行符,截取到行结束
			v输出 = v输出[0:v空格位置[0]] + v输出[v空格位置[1]:v行结束]
		else:	#如果没有换行符,截取到字符串结束
			v输出 = v输出[0:v空格位置[0]] + v输出[v空格位置[1]:]	#12:06:32 Wed 04/26/2000
		v时间 = time.strptime(v输出, "%H:%M:%S %a %m/%d/%Y")
		return v时间
	def f显示_版本(self):
		raise NotImplementedError()
	def f显示_当前配置(self):
		v输出 = self.f执行命令("display current-configuration", a自动换页 = True)
		v输出 = 设备.C实用工具.f去头尾行(v输出)
		return C配置信息(v输出)
	def f显示_设备名称(self):
		v输出 = self.f执行命令("display current-configuration | include sysname", a等待 = 5)
		return C输出分析.f从配置取设备名称(v输出)
	def f显示_设备版本(self):
		v输出 = self.f执行命令("display version", a自动换页 = True)
		v输出 = 设备.C实用工具.f去头尾行(v输出, a转列表 = True)
		v字典 = dict()
		v字典["版本号"] = v输出[1][26:29]
		v字典["发行号"] = v输出[1][40:43]
		v字典["版权"] = v输出[2]
		v第四行分段 = v输出[3].split(" ")
		v字典["平台"] = v第四行分段[0] + " " + v第四行分段[1]
		v字典["更新时间"] = 设备.C实用工具.f时间(v第四行分段[4], v第四行分段[6], v第四行分段[8], v第四行分段[10])
		return v字典
	def f显示_cpu使用率(self):
		"返回字典，键=槽位，值=5分钟使用率"
		v输出 = self.f执行命令("display cpu-usage", a自动换页 = True)
		v输出 = 设备.C实用工具.f去头尾行(v输出, a转列表 = True)
		print(v输出)
		v字典 = dict()
		i = 0
		while i < len(v输出):
			v槽位 = int(C实用工具.f取数字(v输出[i])[0])
			v使用率 = int(C实用工具.f取数字(v输出[i+3])[0])
			v字典[v槽位] = v使用率
			i += 5
		return v字典
	def f显示_内存使用率(self):
		v输出 = self.f执行命令("display memory")
		v输出 = 设备.C实用工具.f去头尾行(v输出, a转列表 = True)
		return 设备.C实用工具.f取数字(v输出[3])[0]
	def f显示_温度(self):
		v输出 = self.f执行命令("display environment", a自动换页 = True)
		v输出 = 设备.C实用工具.f去头尾行(v输出, p尾行 = 2, a转列表 = True)
		v输出 = v输出[3:]
		v字典 = dict()
		for v in v输出:
			v槽位 = int(v[1:5])
			v温度 = int(v[17:27])
			v字典[v槽位] = v温度
		return v字典
	def f显示_运行时间(self):
		raise NotImplementedError()
	def f显示_开机日期(self):
		raise NotImplementedError()
	def f显示_序列号(self):
		raise NotImplementedError()
	def f显示_出厂日期(self):
		raise NotImplementedError()
	#显示程序状态
	def f显示_路由表(self):
		v输出 = self.f执行命令("display ip routing-table", a自动换页 = True)
		v输出 = 设备.C实用工具.f去头尾行(v输出, a转列表 = True)
	def f显示_默认路由(self):
		v输出 = self.f执行命令("display ip routing-table 0.0.0.0")
		v输出 = 设备.C实用工具.f去头尾行(v输出, a转列表 = True)
		v输出 = v输出[5]
		return (ipaddress.IPv4Network("0.0.0.0/0"), v输出[20:25], int(v输出[27:30]), int(v输出[32:42]), ipaddress.IPv4Address(v输出[45:61]), v输出[61:70])
	def f显示_链路层发现协议(self):
		v输出 = self.f执行命令("display lldp neighbor-information", a自动换页 = True)
	#动作
	def f登陆(self, a用户名, a密码):
		self.f执行命令(a用户名)
		v输出 = self.f执行命令(a密码)
		if '%' in v输出:
			raise RuntimeError(v输出)
	def f提升权限(self, a密码 = ""):
		v输出 = self.f执行命令("super")
		while "Password" in v输出:
			v输出 = self.f执行命令(a密码)
		if "Error" in v输出:
			raise RuntimeError(v输出)
		elif "User privilege level is" in v输出:
			v当前权限 = 设备.C实用工具.f取数字(v输出)[0]
			return (v当前权限, 3)
		else:
			raise RuntimeError("无法提升权限")
#===============================================================================
# 信息
#===============================================================================
class C设备主信息:	#display device maininfo
	def __init__(self, a输出):
		self.m输出 = a输出
	def fg型号名(self):
		pass
	def fg序列号(self):
		pass
	def fg生产日期(self):
		pass
	def fg供应商(self):
		pass
#===============================================================================
# 系统
#===============================================================================
class C系统视图(设备.I全局配置模式):
	def __init__(self, a):
		设备.I全局配置模式.__init__(self, a)
	def fg进入命令(self):
		return "system-view"
	def f模式_时间(self):
		raise NotImplementedError()
	def f模式_接口配置(self, a接口):
		v接口 = 接口.f创建接口(a接口)
		return 接口.C接口(self, v接口)
	def f模式_用户配置(self, a用户名):
		if self.m设备.m型号 == E型号.s2126:
			return 用户.C用户s2126(self, a用户名)
		if self.m设备.m版本 < 6:
			return 用户.C用户v5(self, a用户名)
		elif self.m设备.m版本 < 7.1:
			return 用户.C用户v7(self, a用户名)
		elif self.m设备.m版本:
			return 用户.C用户v7_1(self, a用户名)
	def f模式_登陆配置(self, a方式, a范围 = None):	#console,vty之类的
		return 登陆.C登陆(self, a方式, a范围)
	def f模式_时间范围(self, a名称):
		return 时间范围.C时间范围(self, a名称)
	def f模式_虚拟局域网(self, a序号):	#vlan
		raise NotImplementedError()
	#设备配置
	def fs设备名(self, a名称):
		v命令 = 设备.C命令("sysname")
		v命令 += a名称
		self.f执行当前模式命令(a名称)
#===============================================================================
# 地址池
#===============================================================================
class C网络地址池(设备.I网络协议地址池, 设备.C同级模式):
	def __init__(self, a, a名称):
		设备.I网络协议地址池.__init__(self, a, a名称)
	def fs地址范围(self, a开始, a结束 = None):
		v命令 = self.fg命令前缀()
		v命令 += a开始
		if a结束:
			v命令 += a结束
		self.f切换到当前模式()
		self.m设备.f执行命令(v命令)
	def fs默认网关(self, p网关):
		v命令 = self.fg命令前缀()
		v命令.f添加("gateway", p网关)
		self.f切换到当前模式()
		self.m设备.f执行命令(v命令)
	def fg命令前缀(self):
		return 设备.C命令("ip pool " + self.m名称)
#===============================================================================
# snmp
#===============================================================================
class C简单网络管理协议(设备.I简单网络管理协议, 设备.C同级模式):
	def __init__(self, a):
		设备.I简单网络管理协议.__init__(self, a)
#===============================================================================
# 工具
#===============================================================================
class C配置信息:
	def __init__(self, a配置):
		self.m配置 = a配置.replace('\r', '')
	def __str__(self):
		return self.m配置
	def fg设备名称(self):
		return C输出分析.f从配置取设备名称(self.m配置)
class C输出分析:
	def f从配置取设备名称(a配置):
		v指定行 = a配置.find(" sysname ")
		v结束 = a配置.find('\n', v指定行)
		if v结束 == -1:
			return a配置[v指定行 + 9 :]
		else:
			return a配置[v指定行 + 9 : v结束]