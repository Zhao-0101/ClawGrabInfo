# DocManager - 智能文档管理程序

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DocManager是一款智能文档管理桌面程序，通过分析四级目录结构中的第三级文件夹命名，自动重组文件架构，帮助用户按业务类型而非项目名称管理文档。

## 🎯 核心功能

- **四级目录扫描**: 自动识别项目/类型/内容的三级结构
- **智能重排**: 根据第三级目录名（如"文档"、"图片"）重组第二级目录
- **预览确认**: 执行前可视化展示重排结果
- **撤销支持**: 一键恢复原结构，操作无忧

## 📦 项目结构

```
doc-manager/
├── doc-manager-mvp.md          # MVP产品文档
├── doc-manager-tech-spec.md    # 技术规划文档
├── implementation-roadmap.md   # 实现路线图
├── prototype.py                # 快速原型代码
└── README.md                   # 本文件
```

## 🚀 快速开始

### 原型体验

```bash
# 克隆仓库
git clone https://github.com/yourusername/doc-manager.git
cd doc-manager

# 运行原型
python prototype.py
```

### 原型功能

原型提供交互式命令行界面：

1. **扫描并显示目录结构** - 分析四级目录
2. **生成重排计划** - 创建智能重排方案
3. **预览重排计划** - 可视化展示结果
4. **执行重排操作** - 应用重排方案
5. **撤销上次操作** - 恢复原结构
6. **创建示例目录结构** - 快速生成测试数据

## 📋 文档索引

| 文档 | 说明 |
|-----|------|
| [MVP产品文档](doc-manager-mvp.md) | 产品需求、用户故事、功能规格 |
| [技术规划文档](doc-manager-tech-spec.md) | 技术选型、架构设计、API设计 |
| [实现路线图](implementation-roadmap.md) | 4周开发计划、里程碑 |

## 🛠️ 技术栈

- **语言**: Python 3.9+
- **GUI框架**: PySide6
- **配置管理**: Pydantic + PyYAML
- **日志系统**: Loguru

## 📅 路线图

| 阶段 | 时间 | 目标 |
|-----|------|------|
| MVP | 4周 | 核心功能可用 |
| 阶段1 | 2-3月 | 增强易用性 |
| 阶段2 | 6月 | 企业级功能 |

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**注意**: 本项目当前处于MVP设计阶段，代码为原型演示用途。
