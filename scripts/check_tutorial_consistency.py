#!/usr/bin/env python3
"""
Course Consistency Checker for Build Your Own Coding Agent

This script checks that all tutorials follow the established patterns:
- Use Command pattern (ToolCommand, CommandHistory) after Tutorial 8
- Import from coding_agent package, don't duplicate code
- Maintain architectural consistency

Run this before committing new tutorials to catch issues early.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def get_tutorial_files(tutorials_dir: str) -> List[Path]:
    """Get all tutorial markdown files, sorted."""
    tutorials_path = Path(tutorials_dir)
    if not tutorials_path.exists():
        print(f"❌ Tutorials directory not found: {tutorials_dir}")
        sys.exit(1)
    
    files = list(tutorials_path.glob("day*.md"))
    return sorted(files)


def check_command_pattern_consistency(content: str, tutorial_num: int) -> List[str]:
    """
    Check that tutorials after T08 use Command pattern.
    
    Only Tutorials 9-13 (Day 1) and T73+ (File operations) need Command pattern.
    Tutorials 25-36 (LLM fundamentals) don't need it.
    """
    issues = []
    
    if tutorial_num < 8:
        return issues  # Tutorials 1-7 are before Command pattern
    
    # Skip conceptual tutorials about design patterns (11, 12)
    if tutorial_num in [11, 12]:
        return issues  # Interface design and DI are conceptual
    
    # Skip LLM fundamentals tutorials (25-36, 49-72) - they're conceptual
    if 25 <= tutorial_num <= 36 or 49 <= tutorial_num <= 72:
        return issues
    
    # Only check agent implementation tutorials that actually execute tools
    # Must have BOTH Agent class AND tool execution
    has_agent_class = "class Agent" in content
    has_tool_execution = "_handle_command" in content or "tool.execute(" in content
    is_implementation = "def run(" in content and "src/coding_agent" in content
    
    if not (has_agent_class and has_tool_execution and is_implementation):
        return issues  # Conceptual or incomplete tutorial, skip
    
    # Check for Command pattern imports
    has_toolcommand_import = (
        "from coding_agent.tools import" in content and 
        "ToolCommand" in content
    ) or "from coding_agent.tools.command import" in content
    
    # Check for duplicate CommandResult definition
    has_own_commandresult = re.search(
        r'@dataclass\s*\nclass CommandResult:',
        content
    ) is not None
    
    # Check for direct tool.execute() without ToolCommand wrapper
    has_direct_execute = re.search(
        r'result\s*=\s*tool\.execute\(',
        content
    ) is not None
    
    # Check for ToolCommand usage
    has_toolcommand_usage = "ToolCommand(" in content
    
    # Agent tutorials 8+ should import Command pattern
    if not has_toolcommand_import:
        issues.append(
            f"❌ T{tutorial_num}: Missing Command pattern imports. "
            f"Should import ToolCommand, CommandResult, CommandHistory from coding_agent.tools"
        )
    
    # Should NOT define own CommandResult (import from package) - except T8 which creates it
    if has_own_commandresult and tutorial_num != 8:
        issues.append(
            f"❌ T{tutorial_num}: Defines own CommandResult class. "
            f"Should import from coding_agent.tools.command instead"
        )
    
    # Should use ToolCommand wrapper, not direct execute
    if has_direct_execute and not has_toolcommand_usage:
        issues.append(
            f"❌ T{tutorial_num}: Uses direct tool.execute() without ToolCommand wrapper. "
            f"Should use: tool_cmd = ToolCommand(tool, args); result = tool_cmd.execute()"
        )
    
    return issues


def check_import_consistency(content: str, tutorial_num: int) -> List[str]:
    """Check that tutorials import from package, not duplicate code."""
    issues = []
    
    # Skip LLM fundamentals tutorials (25-36, 49-72) - they're conceptual
    if 25 <= tutorial_num <= 36 or 49 <= tutorial_num <= 72:
        return issues
    
    # After T08, agent tutorials should import from coding_agent package
    if tutorial_num >= 8:
        has_package_imports = "from coding_agent." in content
        has_agent_class = "class Agent" in content
        
        if has_agent_class and not has_package_imports:
            issues.append(
                f"⚠️  T{tutorial_num}: Agent class but no imports from coding_agent package. "
                f"Should import modules from the package structure"
            )
    
    return issues


def check_architecture_evolution(content: str, tutorial_num: int) -> List[str]:
    """Check that architectural evolution is documented."""
    issues = []
    
    if tutorial_num <= 8:
        return issues
    
    # Skip LLM fundamentals tutorials (25-36, 49-72)
    if 25 <= tutorial_num <= 36 or 49 <= tutorial_num <= 72:
        return issues
    
    # Only check agent architecture tutorials that actually execute tools
    # Skip conceptual examples that just show type hints or DI patterns
    has_tool_execution = (
        "_handle_command" in content or 
        ("tool.execute" in content and "def run" in content)
    )
    
    if not has_tool_execution:
        return issues  # Conceptual tutorial, skip Command pattern check
    
    # After T08, if introducing new patterns, should explain evolution
    has_evolution_note = (
        "evolution" in content.lower() or 
        "builds on" in content.lower() or
        "tutorial 8" in content.lower() or
        "from tutorial" in content.lower()
    )
    
    # If adding new capabilities beyond T08, should mention it
    introduces_new_pattern = (
        "DI container" in content or
        "dependency injection" in content.lower() or
        "validate_input" in content
    )
    
    if introduces_new_pattern and not has_evolution_note:
        issues.append(
            f"⚠️  T{tutorial_num}: Introduces new patterns but missing evolution note. "
            f"Add a section explaining how this builds on previous tutorials"
        )
    
    return issues


def extract_tutorial_number(filename: str) -> int:
    """Extract tutorial number from filename like 'day01-t08-...md'"""
    match = re.search(r't(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def check_tutorial(filepath: Path) -> Tuple[int, List[str]]:
    """Check a single tutorial file for consistency issues."""
    tutorial_num = extract_tutorial_number(filepath.name)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return tutorial_num, [f"❌ Error reading file: {e}"]
    
    issues = []
    issues.extend(check_command_pattern_consistency(content, tutorial_num))
    issues.extend(check_import_consistency(content, tutorial_num))
    issues.extend(check_architecture_evolution(content, tutorial_num))
    
    return tutorial_num, issues


def main():
    """Main entry point."""
    # Find tutorials directory
    script_dir = Path(__file__).parent
    workspace_dir = script_dir.parent
    
    # Try common locations
    possible_paths = [
        workspace_dir / "jarvis-learning" / "courses" / "build-coding-agent" / "tutorials",
        workspace_dir / "courses" / "build-coding-agent" / "tutorials",
        Path.home() / ".openclaw" / "workspace" / "jarvis-learning" / "courses" / "build-coding-agent" / "tutorials",
    ]
    
    tutorials_dir = None
    for path in possible_paths:
        if path.exists():
            tutorials_dir = path
            break
    
    if tutorials_dir is None:
        # Use argument if provided
        if len(sys.argv) > 1:
            tutorials_dir = Path(sys.argv[1])
        else:
            print("❌ Could not find tutorials directory")
            print("Usage: python check_tutorial_consistency.py <tutorials-dir>")
            sys.exit(1)
    
    print(f"📚 Checking tutorials in: {tutorials_dir}")
    print("=" * 70)
    
    tutorial_files = get_tutorial_files(tutorials_dir)
    
    if not tutorial_files:
        print("❌ No tutorial files found")
        sys.exit(1)
    
    all_passed = True
    total_issues = 0
    
    for filepath in tutorial_files:
        tutorial_num, issues = check_tutorial(filepath)
        
        if issues:
            all_passed = False
            total_issues += len(issues)
            print(f"\n📄 {filepath.name} (Tutorial {tutorial_num}):")
            for issue in issues:
                print(f"   {issue}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tutorials passed consistency checks!")
        sys.exit(0)
    else:
        print(f"❌ Found {total_issues} consistency issue(s)")
        print("\nPlease fix these issues to maintain course consistency.")
        sys.exit(1)


if __name__ == "__main__":
    main()
