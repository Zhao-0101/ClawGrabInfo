#!/usr/bin/env python3
"""
DocManager 快速原型
展示核心功能：四级目录扫描和智能重排

使用方法:
    python prototype.py

功能:
    1. 扫描指定目录的四级结构
    2. 根据第三级目录名重排第二级目录
    3. 预览重排结果
    4. 执行重排操作（可选）
    5. 撤销操作（可选）
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict


# ============== 数据模型 ==============

@dataclass
class MoveOperation:
    """文件移动操作"""
    source: str
    target: str
    item_type: str  # 'file' 或 'directory'
    
    def __repr__(self):
        return f"Move({self.item_type}): {self.source} -> {self.target}"


@dataclass
class ReorganizePlan:
    """重排计划"""
    source_root: str
    target_root: str
    operations: List[MoveOperation]
    timestamp: str
    
    def summary(self) -> str:
        """计划摘要"""
        files = sum(1 for op in self.operations if op.item_type == 'file')
        dirs = sum(1 for op in self.operations if op.item_type == 'directory')
        return f"总计: {files} 个文件, {dirs} 个目录"


@dataclass
class Snapshot:
    """操作快照（用于撤销）"""
    snapshot_id: str
    timestamp: str
    operations: List[MoveOperation]
    metadata_path: str


# ============== 核心服务 ==============

class DirectoryScanner:
    """目录扫描器"""
    
    def scan(self, root_path: str, max_depth: int = 4) -> Dict:
        """
        扫描目录结构，返回树形数据
        
        Returns:
            {
                'name': 目录名,
                'path': 完整路径,
                'level': 层级,
                'children': [子节点...]
            }
        """
        root = Path(root_path)
        if not root.exists():
            raise FileNotFoundError(f"目录不存在: {root_path}")
        
        def build_tree(path: Path, current_level: int) -> Dict:
            node = {
                'name': path.name,
                'path': str(path),
                'level': current_level,
                'children': []
            }
            
            if current_level < max_depth and path.is_dir():
                try:
                    for item in sorted(path.iterdir()):
                        if item.name.startswith('.'):
                            continue
                        node['children'].append(build_tree(item, current_level + 1))
                except PermissionError:
                    pass
            
            return node
        
        return build_tree(root, 1)
    
    def get_level3_map(self, tree: Dict) -> Dict[str, List[str]]:
        """
        提取第三级目录映射
        
        Returns:
            {第三级目录名: [第二级目录路径列表]}
        """
        level3_map = defaultdict(list)
        
        # 遍历 Level 2
        for level2_node in tree.get('children', []):
            level2_path = level2_node['path']
            
            # 获取 Level 3
            for level3_node in level2_node.get('children', []):
                level3_name = level3_node['name']
                level3_map[level3_name].append(level2_path)
        
        return dict(level3_map)
    
    def print_tree(self, tree: Dict, indent: int = 0):
        """打印目录树"""
        prefix = "  " * (tree['level'] - 1)
        print(f"{prefix}{tree['name']}/")
        for child in tree.get('children', []):
            self.print_tree(child, indent + 1)


class Reorganizer:
    """重排引擎"""
    
    def __init__(self, source_root: str, target_root: str):
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)
        self.scanner = DirectoryScanner()
    
    def analyze(self) -> ReorganizePlan:
        """
        分析目录结构，生成重排计划
        """
        tree = self.scanner.scan(str(self.source_root))
        level3_map = self.scanner.get_level3_map(tree)
        
        operations = []
        
        # 遍历 Level 2
        for level2_node in tree.get('children', []):
            level2_name = level2_node['name']
            
            # 遍历 Level 3
            for level3_node in level2_node.get('children', []):
                level3_name = level3_node['name']
                
                # 新路径：target_root / Level3名称 / Level2名称
                target_base = self.target_root / level3_name / level2_name
                
                # 添加 Level 3 目录本身的移动操作
                operations.append(MoveOperation(
                    source=level3_node['path'],
                    target=str(target_base),
                    item_type='directory'
                ))
                
                # 添加 Level 4 及以下的所有内容
                self._collect_children_operations(
                    level3_node, target_base, operations
                )
        
        return ReorganizePlan(
            source_root=str(self.source_root),
            target_root=str(self.target_root),
            operations=operations,
            timestamp=datetime.now().isoformat()
        )
    
    def _collect_children_operations(self, node: Dict, target_base: Path, 
                                      operations: List[MoveOperation]):
        """递归收集子节点的移动操作"""
        for child in node.get('children', []):
            source_path = child['path']
            target_path = target_base / child['name']
            
            if Path(source_path).is_dir():
                operations.append(MoveOperation(
                    source=source_path,
                    target=str(target_path),
                    item_type='directory'
                ))
                # 递归处理子目录
                self._collect_children_operations(child, target_path, operations)
            else:
                operations.append(MoveOperation(
                    source=source_path,
                    target=str(target_path),
                    item_type='file'
                ))
    
    def preview(self, plan: ReorganizePlan) -> str:
        """生成预览文本"""
        lines = [
            "=" * 60,
            "重排计划预览",
            "=" * 60,
            f"源目录: {plan.source_root}",
            f"目标目录: {plan.target_root}",
            f"生成时间: {plan.timestamp}",
            f"{plan.summary()}",
            "-" * 60,
            "目录映射:",
        ]
        
        # 按第三级分组展示
        level3_groups = defaultdict(list)
        for op in plan.operations:
            if op.item_type == 'directory':
                parts = Path(op.target).parts
                if len(parts) >= 2:
                    level3_name = parts[-2] if '按类型' in str(Path(op.target).parent) else parts[-1]
                    level3_groups[level3_name].append(op)
        
        for level3_name, ops in sorted(level3_groups.items()):
            lines.append(f"\n[{level3_name}]")
            for op in ops[:5]:  # 只显示前5个
                source_name = Path(op.source).name
                target_parent = Path(op.target).parent.name
                lines.append(f"  {target_parent}/{source_name}/")
            if len(ops) > 5:
                lines.append(f"  ... 还有 {len(ops) - 5} 个项目")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class FileService:
    """文件操作服务"""
    
    @staticmethod
    def ensure_dir(path: str):
        """确保目录存在"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def safe_move(source: str, target: str) -> bool:
        """安全移动文件/目录"""
        try:
            src_path = Path(source)
            tgt_path = Path(target)
            
            # 确保目标目录存在
            tgt_path.parent.mkdir(parents=True, exist_ok=True)
            
            if src_path.is_dir():
                # 如果是目录，使用 shutil.move
                shutil.move(str(src_path), str(tgt_path))
            else:
                # 如果是文件，直接移动
                shutil.move(str(src_path), str(tgt_path))
            return True
        except Exception as e:
            print(f"移动失败: {source} -> {target}")
            print(f"错误: {e}")
            return False
    
    @staticmethod
    def calculate_size(path: str) -> int:
        """计算目录大小（字节）"""
        total = 0
        p = Path(path)
        if p.is_file():
            return p.stat().st_size
        
        for item in p.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total


class UndoService:
    """撤销服务"""
    
    SNAPSHOT_DIR = ".docmanager_snapshots"
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.snapshot_dir = self.base_path / self.SNAPSHOT_DIR
        self.snapshot_dir.mkdir(exist_ok=True)
    
    def create_snapshot(self, plan: ReorganizePlan) -> Snapshot:
        """创建操作快照"""
        snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_path = self.snapshot_dir / f"{snapshot_id}.json"
        
        # 保存操作记录（反向操作用于撤销）
        reverse_operations = [
            {
                'source': op.target,  # 撤销时从目标移回源
                'target': op.source,
                'item_type': op.item_type
            }
            for op in plan.operations
        ]
        
        snapshot_data = {
            'snapshot_id': snapshot_id,
            'timestamp': plan.timestamp,
            'source_root': plan.source_root,
            'target_root': plan.target_root,
            'reverse_operations': reverse_operations
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
        
        return Snapshot(
            snapshot_id=snapshot_id,
            timestamp=plan.timestamp,
            operations=plan.operations,
            metadata_path=str(metadata_path)
        )
    
    def list_snapshots(self) -> List[Dict]:
        """列出所有可用的快照"""
        snapshots = []
        for f in self.snapshot_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                snapshots.append({
                    'id': data['snapshot_id'],
                    'timestamp': data['timestamp'],
                    'path': str(f)
                })
        return sorted(snapshots, key=lambda x: x['timestamp'], reverse=True)
    
    def undo(self, snapshot_id: str) -> bool:
        """执行撤销操作"""
        metadata_path = self.snapshot_dir / f"{snapshot_id}.json"
        
        if not metadata_path.exists():
            print(f"快照不存在: {snapshot_id}")
            return False
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n正在撤销操作: {snapshot_id}")
        print(f"共 {len(data['reverse_operations'])} 个操作需要恢复")
        
        success_count = 0
        for op in data['reverse_operations']:
            if FileService.safe_move(op['source'], op['target']):
                success_count += 1
        
        print(f"撤销完成: {success_count}/{len(data['reverse_operations'])} 成功")
        
        # 重命名快照表示已撤销
        undone_path = metadata_path.with_suffix('.undone')
        metadata_path.rename(undone_path)
        
        return True


# ============== 命令行界面 ==============

class CLI:
    """命令行界面"""
    
    def __init__(self):
        self.scanner = DirectoryScanner()
        self.current_plan: Optional[ReorganizePlan] = None
        self.undo_service: Optional[UndoService] = None
    
    def print_banner(self):
        """打印欢迎信息"""
        print("""
╔══════════════════════════════════════════════════════════╗
║            DocManager 文档管理程序 - 快速原型             ║
║                   版本: 0.1.0 (Prototype)                 ║
╚══════════════════════════════════════════════════════════╝
        """)
    
    def print_menu(self):
        """打印主菜单"""
        print("\n主菜单:")
        print("  [1] 扫描并显示目录结构")
        print("  [2] 生成重排计划")
        print("  [3] 预览重排计划")
        print("  [4] 执行重排操作")
        print("  [5] 撤销上次操作")
        print("  [6] 创建示例目录结构")
        print("  [0] 退出")
    
    def get_input(self, prompt: str, default: str = None) -> str:
        """获取用户输入"""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        value = input(full_prompt).strip()
        return value if value else default
    
    def cmd_scan(self):
        """扫描目录"""
        path = self.get_input("请输入要扫描的目录路径", ".")
        
        try:
            tree = self.scanner.scan(path)
            print("\n目录结构:")
            self.scanner.print_tree(tree)
            
            # 显示第三级目录统计
            level3_map = self.scanner.get_level3_map(tree)
            if level3_map:
                print("\n第三级目录统计:")
                for name, paths in sorted(level3_map.items()):
                    print(f"  [{name}]: {len(paths)} 个项目")
        except Exception as e:
            print(f"错误: {e}")
    
    def cmd_analyze(self):
        """生成重排计划"""
        source = self.get_input("请输入源目录路径", "./test_data")
        target = self.get_input("请输入目标目录路径", "./test_data/按类型")
        
        try:
            reorganizer = Reorganizer(source, target)
            self.current_plan = reorganizer.analyze()
            self.undo_service = UndoService(target)
            
            print(f"\n✓ 重排计划已生成")
            print(f"  {self.current_plan.summary()}")
        except Exception as e:
            print(f"错误: {e}")
    
    def cmd_preview(self):
        """预览计划"""
        if not self.current_plan:
            print("请先生成重排计划 (选项2)")
            return
        
        reorganizer = Reorganizer(
            self.current_plan.source_root,
            self.current_plan.target_root
        )
        print(reorganizer.preview(self.current_plan))
    
    def cmd_execute(self):
        """执行重排"""
        if not self.current_plan:
            print("请先生成重排计划 (选项2)")
            return
        
        print("\n⚠️  即将执行以下操作:")
        print(f"  源目录: {self.current_plan.source_root}")
        print(f"  目标目录: {self.current_plan.target_root}")
        print(f"  {self.current_plan.summary()}")
        
        confirm = self.get_input("\n确认执行? (yes/no)", "no")
        if confirm.lower() != "yes":
            print("已取消")
            return
        
        # 创建快照（用于撤销）
        snapshot = self.undo_service.create_snapshot(self.current_plan)
        print(f"\n✓ 已创建快照: {snapshot.snapshot_id}")
        
        # 执行移动操作
        print("\n开始执行移动操作...")
        success_count = 0
        total = len(self.current_plan.operations)
        
        for i, op in enumerate(self.current_plan.operations, 1):
            if i % 10 == 0 or i == total:
                print(f"  进度: {i}/{total}", end="\r")
            
            if FileService.safe_move(op.source, op.target):
                success_count += 1
        
        print(f"\n✓ 执行完成: {success_count}/{total} 成功")
    
    def cmd_undo(self):
        """撤销操作"""
        if not self.undo_service:
            print("没有可用的撤销服务")
            return
        
        snapshots = self.undo_service.list_snapshots()
        if not snapshots:
            print("没有可撤销的操作")
            return
        
        print("\n可撤销的操作:")
        for i, snap in enumerate(snapshots[:5], 1):
            print(f"  [{i}] {snap['id']} - {snap['timestamp']}")
        
        choice = self.get_input("请选择要撤销的操作编号 (1-5)", "1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(snapshots):
                self.undo_service.undo(snapshots[idx]['id'])
            else:
                print("无效选择")
        except ValueError:
            print("请输入数字")
    
    def cmd_create_sample(self):
        """创建示例目录结构"""
        base_path = self.get_input("请输入示例目录根路径", "./test_data")
        base = Path(base_path)
        
        # 创建示例结构
        structures = [
            "A项目/文档/2024/报告1.pdf",
            "A项目/文档/2024/报告2.pdf",
            "A项目/图片/素材/logo.png",
            "A项目/图片/成品/海报.jpg",
            "B项目/文档/2023/合同.docx",
            "B项目/文档/2023/备忘录.txt",
            "B项目/代码/前端/app.js",
            "B项目/代码/后端/server.py",
            "C项目/文档/2024/计划书.docx",
            "C项目/图片/参考/参考1.jpg",
            "C项目/图片/参考/参考2.jpg",
        ]
        
        print(f"\n创建示例结构到: {base}")
        for struct in structures:
            path = base / struct
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"示例文件内容: {struct}")
        
        print(f"✓ 已创建 {len(structures)} 个示例文件")
        print("\n原结构预览:")
        tree = self.scanner.scan(base)
        self.scanner.print_tree(tree)
    
    def run(self):
        """运行主循环"""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = self.get_input("请选择", "0")
            
            if choice == "1":
                self.cmd_scan()
            elif choice == "2":
                self.cmd_analyze()
            elif choice == "3":
                self.cmd_preview()
            elif choice == "4":
                self.cmd_execute()
            elif choice == "5":
                self.cmd_undo()
            elif choice == "6":
                self.cmd_create_sample()
            elif choice == "0":
                print("\n感谢使用，再见！")
                break
            else:
                print("无效选项，请重新选择")


# ============== 主入口 ==============

def main():
    """程序入口"""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
