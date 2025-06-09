# Quote Format Cleaner / メール引用テキスト整形ツール

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


### 概要

メール引用テキスト整形ツールは、メールの引用テキスト（`>`で始まる行）を整形・クリーンアップするPythonツールです。引用記号を除去し、読みやすい形に整形し、スペースを改行に変換して見やすくします。

### 機能

- **引用記号除去**: メールの引用記号（`>`、`>>`など）を除去
- **テキスト整形**: 日本語テキストを適切な改行で整形
- **スペース変換**: 半角・全角スペースを改行に変換
- **キーワード処理**: 指定されたキーワードの前に空行を挿入(config.iniで編集可能)
- **バッチ処理**: 複数のテキストファイルを一括処理
- **エラーハンドリング**: 包括的なエラー処理とログ機能
- **設定可能**: 外部設定ファイルサポート
- **バックアップ**: 元ファイルのオプションバックアップ
- **コマンドラインインターフェース**: コマンドライン引数サポート

### 仕様
現段階では、半角・全角スペースを改行に置き換える処理を行うため、完璧にメールの文を整えることはできません。\
また、日本語テキスト以外では正常な動作を期待できないことをご承知おきください。

### 動作環境

- Python 3.7 以上
- 外部依存関係なし（標準ライブラリのみ使用）

### インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/1987Shiz321/QuoteFormatCleaner.git
cd quote-format-cleaner
```

2. 追加のインストールは不要（Python標準ライブラリのみ使用）

### クイックスタート

1. `input`ディレクトリを作成し、テキストファイルを配置
2. ツールを実行:
```bash
python email_cleaner.py
```
3. 処理されたファイルが`output`ディレクトリに保存される

### 使用方法

#### 基本的な使用方法
```bash
python email_cleaner.py
```

#### カスタム設定ファイルを使用
```bash
python email_cleaner.py --config custom_config.ini
```

#### デバッグログ付きで実行
```bash
python email_cleaner.py --log-level DEBUG
```

#### コマンドラインオプション
- `--config`: 設定ファイルのパスを指定（デフォルト: `config.ini`）
- `--log-level`: ログレベルを設定（`DEBUG`, `INFO`, `WARNING`, `ERROR`）

### 設定

ツールは設定ファイル（`config.ini`）を使用し、初回実行時に自動作成されます。以下の設定をカスタマイズできます：

```ini
[paths]
input_dir = input
output_dir = output

[processing]
encoding = utf-8
backup_original = true

[keywords]
list = 記、件名、宛先、差出人
```

#### 設定項目

- **`input_dir`**: 入力ディレクトリのパス
- **`output_dir`**: 出力ディレクトリのパス
- **`encoding`**: テキストファイルのエンコーディング（デフォルト: utf-8）
- **`backup_original`**: 元ファイルをバックアップするかどうか
- **`keywords.list`**: 前に空行を挿入するキーワードのカンマ区切りリスト

### 使用例

**入力テキスト:**
```
> これは引用されたメールです。
> 複数行にわたる　内容が　含まれています。
> 句点があります。次の文章が続きます。
```

**出力テキスト:**
```
これは引用されたメールです。
複数行にわたる
内容が
含まれています。
句点があります。
次の文章が続きます。
```

### ファイル構成

```
quote-format-cleaner/
├── email_cleaner.py      # メインスクリプト
├── config.ini            # 設定ファイル（自動生成）
├── email_cleaner.log     # ログファイル
├── input/                # 入力ディレクトリ
│   └── backup/          # バックアップディレクトリ（有効時）
├── output/              # 出力ディレクトリ
└── README.md            # このファイル
```

### ログ

ツールは`email_cleaner.log`に詳細なログを作成し、コンソールに進捗を表示します。`--log-level`パラメータでログレベルを調整できます。

### ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

### 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add some amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを開く

### トラブルシューティング

#### よくある問題

**Q: 「入力ディレクトリにテキストファイルが見つかりません」と表示される**
A: `input`ディレクトリに`.txt`ファイルが配置されていることを確認してください。

**Q: 文字化けが発生する**
A: `config.ini`の`encoding`設定を確認し、ファイルのエンコーディングと一致させてください。

**Q: 処理が途中で止まる**
A: ログファイル（`email_cleaner.log`）を確認し、エラーの詳細を確認してください。

#### サポート

問題が発生した場合は、以下の情報と共にIssueを作成してください：
- Python バージョン
- エラーメッセージ
- ログファイルの内容
- 問題が発生した入力ファイルの例（個人情報を除く）

---

## Changelog

### v1.0.0 (2024-06-09)
- Initial release
- Basic quote cleaning functionality
- Configuration file support
- Comprehensive error handling
- Logging functionality
- Backup feature