# [PWS Cup 2025](https://www.iwsec.org/pws/2025/cup25.html)

## How to use
上から順に実行すること。
- リポジトリのクローン
    ```
    git clone git@github.com:nannan-na/pwscup2025.git
    ```
- venv仮想環境の作成
    ```
    cd pwscup2025
    python -m venv venv
    ```
    - ルートディレクトリ以下にディレクトリvenvが作成される
    - ここには仮想環境のシステムファイルが置かれるので、自作のファイルは置かない
- 仮想環境の起動
    ```
    venv/scripts/activate
    ```
- 必要なパッケージ一覧のインストール
    ```
    pip install -r requirements.txt
    ```
    - 数分かかる可能性あり
- venv環境の停止
    ```
    deactivate
    ```
- venv環境の削除
    - ローカルディレクトリの容量を削減したい場合、venvディレクトリを削除すればよい