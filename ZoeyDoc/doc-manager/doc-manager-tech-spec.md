# DocManager 技术规划文档

## 技术选型总览

### 为什么选Python

Python是本项目的首选开发语言，基于以下综合考量：

| 优势 | 具体说明 |
|-----|---------|
| **丰富的文件操作库** | `shutil`、`pathlib`、`os` 提供完善的跨平台文件操作能力 |
| **GUI生态成熟** | PyQt/PySide是跨平台GUI的黄金标准，生态完善 |
| **开发效率高** | 语法简洁，快速迭代，适合MVP开发 |
| **跨平台支持** | 一份代码可在Windows/macOS/Linux运行 |
| **团队熟悉度** | 大多数开发者熟悉Python，降低维护成本 |
| **调试便捷** | 解释型语言，调试周期短 |

### 其他语言的替代方案及适用场景

| 语言/框架 | 优点 | 缺点 | 适用场景 |
|----------|------|------|---------|
| **Electron (JS)** | UI美观、前端开发者友好、丰富的UI组件 | 包体大(>100MB)、内存占用高、文件操作需Node桥接 | 需要高度定制UI、团队熟悉前端 |
| **Tauri (Rust)** | 包体极小(<5MB)、性能优异、内存安全 | 学习曲线陡、GUI生态不如Qt成熟 | 对性能和包大小敏感的场景 |
| **Wails (Go)** | 轻量、性能好、Go语言并发优势 | 生态较小、GUI能力有限 | Go语言团队、后端集成需求 |
| **C# (WPF/MAUI)** | Windows原生体验、强大的IDE支持 | 跨平台支持弱(MAUI尚不成熟)、学习成本 | 纯Windows环境 |
| **Swift (SwiftUI)** | macOS原生体验、性能极佳 | 仅支持macOS/iOS | 纯macOS环境 |

**结论**：Python是当前阶段的最佳选择，未来如有性能或包大小需求，可考虑迁移到Tauri。

---

## 架构设计

### 整体架构图（文字描述）

```
┌─────────────────────────────────────────────────────────────┐
│                        表现层 (UI Layer)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 主窗口      │  │ 预览对话框   │  │ 设置/偏好设置        │ │
│  │ MainWindow  │  │ PreviewDlg  │  │ PreferencesDialog   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼───────────────────┼────────────┘
          │                │                   │
          └────────────────┴───────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (Service Layer)              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 重排服务    │  │ 文件服务    │  │ 撤销服务            │ │
│  │ Reorganizer │  │ FileService │  │ UndoService         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 扫描服务    │  │ 冲突检测    │  │ 配置服务            │ │
│  │ Scanner     │  │ ConflictDet │  │ ConfigService       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层 (Data Layer)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 文件系统    │  │ 配置存储    │  │ 操作日志            │ │
│  │ FileSystem  │  │ ConfigStore │  │ OperationLog        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 模块划分

| 模块名 | 职责 | 核心类 |
|-------|------|-------|
| **ui** | 界面展示与用户交互 | MainWindow, PreviewDialog, ProgressDialog |
| **services** | 业务逻辑实现 | Reorganizer, FileService, Scanner |
| **models** | 数据模型定义 | DirectoryNode, MoveOperation, ReorganizePlan |
| **utils** | 工具函数 | path_utils, file_utils, validators |
| **config** | 配置管理 | ConfigManager, Settings |
| **undo** | 撤销/重做机制 | UndoManager, Snapshot |

### 分层职责

1. **表现层**：负责界面渲染、用户输入、状态展示
   - 不直接操作文件系统
   - 通过Service层执行业务逻辑
   - 使用信号/槽机制与业务层通信

2. **业务逻辑层**：核心功能实现
   - 目录扫描与分析
   - 重排计划生成
   - 文件移动执行
   - 冲突检测与处理

3. **数据访问层**：数据持久化
   - 文件系统操作封装
   - 配置文件读写（JSON/YAML）
   - 操作日志记录（SQLite）

---

## 核心技术栈

### GUI框架对比与选型

| 框架 | 优点 | 缺点 | 适用场景 | 推荐度 |
|------|------|------|---------|-------|
| **PySide6** | 功能最全、文档完善、LGPL许可、官方维护 | 包体较大(~50MB)、学习曲线陡 | 复杂桌面应用 | ⭐⭐⭐⭐⭐ |
| **PyQt6** | 与PySide6几乎相同 | GPL/商业双许可，商用需注意 | 复杂桌面应用 | ⭐⭐⭐⭐ |
| **Tkinter** | 标准库、零依赖、简单 | 外观老旧、功能有限、无现代控件 | 简单工具 | ⭐⭐⭐ |
| **DearPyGui** | 高性能GPU渲染、现代外观 | 生态小、文档少、相对较新 | 数据可视化 | ⭐⭐⭐ |
| **Flet** | Flutter风格、热重载 | 功能有限、生态早期 | 快速原型 | ⭐⭐ |

**选型决策**：使用 **PySide6**
- 功能完善，满足所有需求
- 官方支持，长期维护有保障
- LGPL许可，商业使用友好

### 文件系统操作库

| 库 | 用途 | 说明 |
|---|------|------|
| **pathlib** | 路径操作 | Python 3标准库，面向对象的路径处理 |
| **shutil** | 文件移动/复制 | Python标准库，支持元数据保留 |
| **os** | 底层文件操作 | 标准库，处理权限等特殊需求 |
| **send2trash** | 安全删除 | 移动到回收站而非永久删除 |
| **psutil** | 磁盘空间检测 | 跨平台的系统和进程工具 |

### 配置管理

| 库 | 用途 | 说明 |
|---|------|------|
| **pydantic** | 配置模型验证 | 类型安全、自动验证 |
| **PyYAML** | YAML配置读写 | 人类可读的配置格式 |

### 日志系统

| 库 | 用途 | 说明 |
|---|------|------|
| **loguru** | 现代日志库 | 替代logging，更易用、功能更强大 |
| **标准logging** | 备用方案 | Python内置，无需额外依赖 |

---

## 目录结构

```
doc-manager/
├── src/
│   └── doc_manager/
│       ├── __init__.py
│       ├── __main__.py              # 程序入口
│       ├── app.py                   # 应用主类
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py          # 配置模型
│       │   └── manager.py           # 配置管理器
│       ├── models/
│       │   ├── __init__.py
│       │   ├── directory.py         # 目录节点模型
│       │   ├── operation.py         # 操作记录模型
│       │   └── plan.py              # 重排计划模型
│       ├── services/
│       │   ├── __init__.py
│       │   ├── scanner.py           # 目录扫描服务
│       │   ├── reorganizer.py       # 重排逻辑服务
│       │   ├── file_service.py      # 文件操作服务
│       │   ├── conflict_detector.py # 冲突检测服务
│       │   └── undo_service.py      # 撤销服务
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py       # 主窗口
│       │   ├── preview_dialog.py    # 预览对话框
│       │   ├── progress_dialog.py   # 进度对话框
│       │   ├── widgets/             # 自定义控件
│       │   └── styles/              # 样式文件
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── path_utils.py        # 路径工具
│       │   ├── file_utils.py        # 文件工具
│       │   └── validators.py        # 验证器
│       └── undo/
│           ├── __init__.py
│           ├── snapshot.py          # 快照管理
│           └── manager.py           # 撤销管理器
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   ├── test_reorganizer.py
│   ├── test_file_service.py
│   └── fixtures/                    # 测试数据
├── docs/
│   ├── user-guide.md
│   └── api-reference.md
├── scripts/
│   ├── build.py                     # 打包脚本
│   └── install_deps.py              # 依赖安装
├── resources/
│   ├── icons/
│   ├── styles/
│   └── translations/                # 国际化
├── config/
│   └── default.yaml                 # 默认配置
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

---

## 核心算法设计

### 目录树遍历算法

```python
class DirectoryScanner:
    """
    四级目录扫描器
    采用迭代式BFS遍历，避免递归深度过大
    """
    
    def scan(self, root_path: Path, max_depth: int = 4) -> DirectoryNode:
        """
        扫描目录结构
        
        Args:
            root_path: 根目录路径
            max_depth: 最大扫描深度
            
        Returns:
            DirectoryNode: 目录树结构
        """
        # 使用队列实现BFS
        # 记录每个节点的深度
        # 超过max_depth的目录标记为leaf，不再展开
        pass
    
    def get_level3_directories(self, root: DirectoryNode) -> Dict[str, List[Path]]:
        """
        提取所有第三级目录，按名称分组
        
        Returns:
            Dict[目录名, 路径列表]
            例如: {'文档': [Path('/A/文档'), Path('/B/文档')]}
        """
        pass
```

**复杂度分析**：
- 时间复杂度：O(n)，n为目录和文件总数
- 空间复杂度：O(m)，m为第四级目录数量（最大内存占用）

### 重排规则引擎

```python
class ReorganizeRule:
    """重排规则基类"""
    
    def extract_key(self, path: Path, level: int) -> str:
        """从路径提取分类键（如第三级目录名）"""
        pass
    
    def generate_target(self, source: Path, key: str) -> Path:
        """生成目标路径"""
        pass


class Level3ReorganizeRule(ReorganizeRule):
    """
    基于第三级目录的重排规则
    
    规则：源路径 /L1/L2/L3/L4/... -> 目标路径 /output_dir/L3/L2/L4/...
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def apply(self, structure: DirectoryNode) -> ReorganizePlan:
        """
        应用规则生成重排计划
        
        算法：
        1. 收集所有 L2 -> L3 的映射
        2. 对每个唯一的 L3，创建新的 L2 集合
        3. 生成移动操作列表
        """
        operations = []
        
        for l2_node in structure.children:  # Level 2
            l2_name = l2_node.name
            for l3_node in l2_node.children:  # Level 3
                l3_name = l3_node.name
                
                # 新路径：output_dir / L3名称 / L2名称 / L3下的内容
                target_base = self.output_dir / l3_name / l2_name
                
                for item in l3_node.children:
                    operations.append(MoveOperation(
                        source=item.path,
                        target=target_base / item.name
                    ))
        
        return ReorganizePlan(operations)
```

### 冲突检测与处理

```python
class ConflictDetector:
    """冲突检测器"""
    
    def detect(self, plan: ReorganizePlan) -> List[Conflict]:
        """
        检测重排计划中的冲突
        
        检测类型：
        1. 目标文件已存在（FileExists）
        2. 目标文件夹已存在（FolderExists）
        3. 循环引用（CircularReference）
        4. 权限问题（PermissionDenied）
        5. 磁盘空间不足（InsufficientSpace）
        """
        conflicts = []
        
        # 使用集合检测重复目标
        target_set = set()
        
        for op in plan.operations:
            # 检查目标是否重复
            if op.target in target_set:
                conflicts.append(Conflict(
                    type=ConflictType.DUPLICATE_TARGET,
                    operation=op
                ))
            target_set.add(op.target)
            
            # 检查目标是否存在
            if op.target.exists():
                if op.target.is_file():
                    conflicts.append(Conflict(
                        type=ConflictType.FILE_EXISTS,
                        operation=op
                    ))
                else:
                    conflicts.append(Conflict(
                        type=ConflictType.FOLDER_EXISTS,
                        operation=op
                    ))
            
            # 检查循环引用
            if self._is_circular(op.source, op.target):
                conflicts.append(Conflict(
                    type=ConflictType.CIRCULAR_REFERENCE,
                    operation=op
                ))
        
        return conflicts
    
    def resolve(self, conflicts: List[Conflict], 
                strategy: ResolutionStrategy) -> ReorganizePlan:
        """根据策略自动解决冲突"""
        pass


class ResolutionStrategy(Enum):
    """冲突解决策略"""
    SKIP = "skip"              # 跳过冲突项
    OVERWRITE = "overwrite"    # 覆盖
    RENAME = "rename"          # 自动重命名（加序号/时间戳）
    MERGE = "merge"            # 合并文件夹
    PROMPT = "prompt"          # 询问用户
```

---

## API设计

### 核心类API

```python
# ============ Scanner API ============

class DirectoryScanner:
    def scan(self, path: Path, max_depth: int = 4) -> DirectoryNode
    def scan_async(self, path: Path, callback: Callable) -> ScanTask


# ============ Reorganizer API ============

class Reorganizer:
    def __init__(self, rule: ReorganizeRule)
    
    def analyze(self, source: Path) -> ReorganizePlan
    def preview(self, plan: ReorganizePlan) -> str  # 返回可视化预览文本
    def execute(self, plan: ReorganizePlan, 
                progress_callback: Callable[[int, int], None]) -> ExecuteResult


# ============ FileService API ============

class FileService:
    @staticmethod
    def move(source: Path, target: Path, 
             preserve_metadata: bool = True) -> bool
    
    @staticmethod
    def copy(source: Path, target: Path) -> bool
    
    @staticmethod
    def verify_integrity(source: Path, target: Path) -> bool
    
    @staticmethod
    def get_disk_space(path: Path) -> Tuple[int, int]  # (used, free)


# ============ UndoService API ============

class UndoService:
    def create_snapshot(self, plan: ReorganizePlan) -> Snapshot
    def can_undo(self) -> bool
    def undo(self, snapshot_id: str) -> bool
    def get_history(self) -> List[OperationRecord]
    

# ============ ConflictDetector API ============

class ConflictDetector:
    def detect(self, plan: ReorganizePlan) -> List[Conflict]
    def resolve_auto(self, conflicts: List[Conflict], 
                     strategy: ResolutionStrategy) -> ReorganizePlan
```

### GUI层API（信号/槽）

```python
# MainWindow 提供的信号
class MainWindow(QMainWindow):
    # 用户选择了源目录
    source_selected = Signal(Path)
    
    # 用户点击分析按钮
    analyze_requested = Signal(Path)
    
    # 用户确认执行
    execute_requested = Signal(ReorganizePlan)
    
    # 用户请求撤销
    undo_requested = Signal()

# Service层提供的信号（用于更新UI）
class Reorganizer(QObject):
    # 分析进度
    analysis_progress = Signal(int, int)  # current, total
    
    # 执行进度
    execution_progress = Signal(int, int, str)  # current, total, current_file
    
    # 发现冲突
    conflict_detected = Signal(List[Conflict])
    
    # 执行完成
    execution_completed = Signal(ExecuteResult)
    
    # 发生错误
    error_occurred = Signal(str, str)  # error_code, message
```

---

## 开发环境搭建

### 系统要求

| 组件 | 最低要求 | 推荐 |
|-----|---------|------|
| Python | 3.9 | 3.11+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 100MB | 1GB+ |

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/doc-manager.git
cd doc-manager

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行程序
python -m doc_manager
```

### 依赖清单（requirements.txt）

```
# GUI框架
pyside6>=6.5.0

# 配置管理
pydantic>=2.0.0
pyyaml>=6.0

# 日志
loguru>=0.7.0

# 工具库
send2trash>=1.8.0
psutil>=5.9.0

# 开发依赖（requirements-dev.txt）
pytest>=7.0.0
pytest-qt>=4.2.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
```

---

## 测试策略

### 测试金字塔

```
       /\
      /  \      E2E测试（1-2个核心流程）
     /----\     
    /      \    集成测试（模块间交互）
   /--------\   
  /          \  单元测试（核心算法、工具函数）
 /____________\
```

### 单元测试

| 测试模块 | 测试重点 | 覆盖率目标 |
|---------|---------|-----------|
| test_scanner.py | 目录扫描、深度控制、边界条件 | 90% |
| test_reorganizer.py | 规则应用、计划生成 | 90% |
| test_conflict_detector.py | 各类冲突检测 | 90% |
| test_file_service.py | 移动、复制、校验 | 85% |
| test_undo_service.py | 快照创建、撤销恢复 | 85% |

### 集成测试

```python
# 测试场景1：完整重排流程
def test_full_reorganize_flow():
    # 创建测试目录结构
    # 执行分析
    # 验证计划正确性
    # 执行重排
    # 验证结果
    # 执行撤销
    # 验证恢复原状

# 测试场景2：冲突处理
def test_conflict_resolution():
    # 创建冲突场景
    # 验证冲突检测
    # 应用解决策略
    # 验证结果
```

### E2E测试（使用pytest-qt）

```python
def test_main_workflow(qtbot, tmp_path):
    """测试主工作流程"""
    # 创建主窗口
    window = MainWindow()
    qtbot.addWidget(window)
    
    # 模拟用户操作：选择目录 -> 分析 -> 预览 -> 确认
    qtbot.mouseClick(window.btn_select_source, Qt.LeftButton)
    # ... 更多操作
    
    # 验证结果
    assert window.status == OperationStatus.COMPLETED
```

### 测试数据管理

```
tests/fixtures/
├── sample_structure_1/      # 标准四级结构
├── sample_structure_2/      # 缺失层级结构
├── sample_structure_3/      # 包含冲突的结构
├── large_structure/         # 性能测试数据
└── special_chars/           # 特殊字符文件名
```

### CI/CD集成

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python: ['3.9', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=doc_manager --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 附录

### 关键技术决策记录（ADR）

#### ADR-001: 使用PySide6而非PyQt6
**决策**：使用PySide6  
**原因**：LGPL许可对商业使用更友好，官方维护  
**日期**：2024-03-11

#### ADR-002: 使用loguru替代标准logging
**决策**：使用loguru  
**原因**：API更简洁，自动支持结构化日志  
**日期**：2024-03-11

#### ADR-003: 快照存储使用JSON而非SQLite
**决策**：使用JSON文件存储快照  
**原因**：人类可读，便于调试；数据量不大  
**日期**：2024-03-11

### 参考资源

- [PySide6官方文档](https://doc.qt.io/qtforpython-6/)
- [Python pathlib指南](https://docs.python.org/3/library/pathlib.html)
- [shutil最佳实践](https://docs.python.org/3/library/shutil.html)
