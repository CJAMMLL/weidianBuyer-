# 微店商品自动抢购工具

一个基于 Python 的微店商品自动抢购助手，支持精确到微秒级别的定时抢购。

## 功能特点

- 精确到微秒级的定时抢购
- NTP 时间同步
- 自动化操作购物车
- 图形用户界面
- 实时日志显示

## 系统要求

- Python 3.9+
- Google Chrome 浏览器 (测试版本：133.0.6943.127)
- Windows 10/11
- ChromeDriver (测试版本：133.0.6943.127)

## 安装

1. 克隆仓库
```bash
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名
```

2. 安装依赖
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

3. ChromeDriver 配置
- 程序会自动下载对应版本的 ChromeDriver
- 如自动下载失败，请手动下载并放置在程序目录下
- 下载地址：https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/133.0.6943.127/win64/chromedriver-win64.zip
- 确保 chromedriver.exe 与程序在同一目录下

## 使用方法

1. 运行程序
```bash
python main.py  # 如果是源码运行
# 或者直接运行 weidianBuyer微店买手v1.0.exe  # 如果是打包版本
```

2. 在程序界面中：
   - 输入商品链接
   - 设置抢购时间
   - 点击"预约"按钮
   - 登录账号并添加商品到购物车
   - 等待自动抢购

## 重要说明

- 本程序在 Chrome 浏览器版本 133.0.6943.127 下完成测试
- ChromeDriver 版本必须与 Chrome 浏览器版本完全匹配
- 如果您的 Chrome 版本不是 133.0.6943.127：
  1. 建议将 Chrome 更新/降级到此版本
  2. 或下载与您的 Chrome 版本匹配的 ChromeDriver
- 无论是运行源码(main.py)还是打包后的程序(exe)，都必须确保 chromedriver.exe 在同一目录下
- 如果提示 ChromeDriver 版本不匹配，请下载对应版本并替换

## 注意事项

- 请确保已添加商品到购物车
- 请提前登录账号
- 建议提前几分钟启动程序
- 确保 ChromeDriver 版本与 Chrome 浏览器版本匹配

## 许可证

MIT License

## 免责声明

本程序仅供学习交流使用，请勿用于商业用途。使用本程序产生的任何后果由使用者自行承担。 