print("=== Python環境チェック ===")
print("環境の設定状況を確認します...\n")

# 使用中のPythonインタープリターを確認
import sys
import os

print(f"Pythonバージョン: {sys.version.split()[0]}")
print(f"実行ファイルパス: {sys.executable}")

# 仮想環境内かどうかを確認
if "venv" in sys.executable:
    print("\n✅ 仮想環境が正しく設定されています！")
    print("  プロジェクト専用の環境で開発できます。")
    
    # プロジェクト名を表示
    project_path = os.path.dirname(os.path.dirname(sys.executable))
    project_name = os.path.basename(project_path)
    print(f"  プロジェクト名: {project_name}")
else:
    print("\n❌ 仮想環境外で実行されています")
    print("  VS Code左下でPythonインタープリターを確認してください。")
    print("  正しいインタープリター: .\\venv\\Scripts\\python.exe")

print("\n=== チェック完了 ===")