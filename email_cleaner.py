import os
import re
import shutil
import logging
import argparse
import configparser
from pathlib import Path
from typing import List, Optional, Tuple


class EmailCleanerConfig:
    """設定管理クラス"""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """設定ファイルを読み込み、存在しない場合はデフォルト設定を作成"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """デフォルト設定ファイルを作成"""
        self.config['paths'] = {
            'input_dir': 'input',
            'output_dir': 'output'
        }
        self.config['processing'] = {
            'encoding': 'utf-8',
            'backup_original': 'true'
        }
        self.config['keywords'] = {
            'list': '記、件名、宛先、差出人'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
        logging.info(f"デフォルト設定ファイル '{self.config_file}' を作成しました")
    
    def get_input_dir(self) -> str:
        return self.config.get('paths', 'input_dir', fallback='input')
    
    def get_output_dir(self) -> str:
        return self.config.get('paths', 'output_dir', fallback='output')
    
    def get_encoding(self) -> str:
        return self.config.get('processing', 'encoding', fallback='utf-8')
    
    def get_keywords(self) -> List[str]:
        keywords_str = self.config.get('keywords', 'list', fallback='')
        return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    
    def should_backup(self) -> bool:
        return self.config.getboolean('processing', 'backup_original', fallback=True)


class EmailCleaner:
    """メール引用テキスト整形クラス"""
    
    def __init__(self, config: EmailCleanerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processed_count = 0
        self.error_count = 0
    
    def clean_quoted_email(self, text: str) -> str:
        """
        引用テキストを整形する
        
        Args:
            text: 整形対象のテキスト
            
        Returns:
            整形されたテキスト
        """
        if not text.strip():
            return ""
        
        try:
            lines = text.splitlines()
            
            # 「>」付きの行だけを対象に整形対象として抽出
            quoted_lines = [line for line in lines if re.match(r'^\s*>+', line)]
            
            if not quoted_lines:
                self.logger.warning("引用行（>で始まる行）が見つかりませんでした")
                return text.strip()
            
            # 引用行から引用記号を除去
            cleaned_lines = []
            for line in quoted_lines:
                cleaned_line = re.sub(r'^\s*>+\s?', '', line).strip()
                if cleaned_line:  # 空行は除外
                    cleaned_lines.append(cleaned_line)
            
            if not cleaned_lines:
                return ""
            
            # 行を連結して、句点（。＋空白）で改行（ただし閉じ括弧直前は除外）
            joined_text = ' '.join(cleaned_lines)
            
            # より包括的な閉じ括弧の処理
            joined_text = re.sub(r'。[\s　]*(?=[^」』）】}\]\)>"\'])', '。\n', joined_text)
            
            # 半角・全角スペースを改行に置き換える
            joined_text = re.sub(r'[\s　]+', '\n', joined_text)

            # キーワードの前に空行を入れる
            keywords = self.config.get_keywords()
            for kw in keywords:
                if kw in joined_text:
                    joined_text = joined_text.replace(kw, f"\n\n{kw}")
            
            # 複数の連続する空行を2行に制限
            joined_text = re.sub(r'\n{3,}', '\n\n', joined_text)
            
            return joined_text.strip()
            
        except Exception as e:
            self.logger.error(f"テキスト整形中にエラーが発生しました: {e}")
            return text  # エラー時は元のテキストを返す
    
    def create_directories(self) -> bool:
        """
        必要なディレクトリを作成する
        
        Returns:
            作成成功時True、失敗時False
        """
        try:
            input_dir = Path(self.config.get_input_dir())
            output_dir = Path(self.config.get_output_dir())
            
            input_dir.mkdir(exist_ok=True)
            output_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"ディレクトリを確認/作成しました: {input_dir}, {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"ディレクトリ作成中にエラーが発生しました: {e}")
            return False
    
    def find_text_files(self) -> List[str]:
        """
        入力ディレクトリからテキストファイルを検索する
        
        Returns:
            テキストファイル名のリスト
        """
        try:
            input_dir = Path(self.config.get_input_dir())
            txt_files = [f.name for f in input_dir.iterdir() 
                        if f.is_file() and f.suffix.lower() == '.txt']
            
            self.logger.info(f"{len(txt_files)}個のテキストファイルが見つかりました")
            return txt_files
            
        except Exception as e:
            self.logger.error(f"ファイル検索中にエラーが発生しました: {e}")
            return []
    
    def process_single_file(self, filename: str) -> bool:
        """
        単一ファイルを処理する
        
        Args:
            filename: 処理対象のファイル名
            
        Returns:
            処理成功時True、失敗時False
        """
        input_path = Path(self.config.get_input_dir()) / filename
        output_path = Path(self.config.get_output_dir()) / filename
        encoding = self.config.get_encoding()
        
        try:
            # ファイル読み込み
            with open(input_path, "r", encoding=encoding) as infile:
                raw_text = infile.read()
            
            # テキスト整形
            cleaned_text = self.clean_quoted_email(raw_text)
            
            # ファイル書き込み
            with open(output_path, "w", encoding=encoding) as outfile:
                outfile.write(cleaned_text)
            
            self.logger.info(f"'{filename}' を処理して出力ディレクトリに保存しました")
            self.processed_count += 1
            return True
            
        except FileNotFoundError:
            self.logger.error(f"ファイルが見つかりません: {filename}")
        except PermissionError:
            self.logger.error(f"ファイルアクセス権限がありません: {filename}")
        except UnicodeDecodeError:
            self.logger.error(f"文字エンコーディングエラー: {filename} (エンコーディング: {encoding})")
        except Exception as e:
            self.logger.error(f"'{filename}' の処理中に予期しないエラーが発生しました: {e}")
        
        self.error_count += 1
        return False
    
    def backup_original_files(self, filenames: List[str]) -> bool:
        """
        元ファイルをバックアップする
        
        Args:
            filenames: バックアップ対象のファイル名リスト
            
        Returns:
            バックアップ成功時True、失敗時False
        """
        if not self.config.should_backup():
            return True
        
        try:
            backup_dir = Path(self.config.get_input_dir()) / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            for filename in filenames:
                src = Path(self.config.get_input_dir()) / filename
                dst = backup_dir / filename
                shutil.copy2(src, dst)
            
            self.logger.info(f"{len(filenames)}個のファイルをバックアップしました")
            return True
            
        except Exception as e:
            self.logger.error(f"バックアップ中にエラーが発生しました: {e}")
            return False
    
    def confirm_deletion(self) -> bool:
        """
        ファイル削除の確認を取る
        
        Returns:
            削除実行時True、キャンセル時False
        """
        try:
            answer = input("\nすべてのファイルを処理しました。入力ディレクトリのファイルを削除しますか？ (y/n): ").strip().lower()
            return answer in ['y', 'yes', 'はい']
        except (EOFError, KeyboardInterrupt):
            print("\n処理をキャンセルしました")
            return False
    
    def delete_original_files(self, filenames: List[str]) -> bool:
        """
        元ファイルを削除する
        
        Args:
            filenames: 削除対象のファイル名リスト
            
        Returns:
            削除成功時True、失敗時False
        """
        try:
            input_dir = Path(self.config.get_input_dir())
            deleted_count = 0
            
            for filename in filenames:
                file_path = input_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
            
            self.logger.info(f"{deleted_count}個のファイルを削除しました")
            return True
            
        except Exception as e:
            self.logger.error(f"ファイル削除中にエラーが発生しました: {e}")
            return False
    
    def process_all_files(self) -> Tuple[int, int]:
        """
        すべてのファイルを処理する
        
        Returns:
            (処理成功数, エラー数)のタプル
        """
        self.processed_count = 0
        self.error_count = 0
        
        # ディレクトリ作成
        if not self.create_directories():
            return self.processed_count, self.error_count
        
        # テキストファイル検索
        txt_files = self.find_text_files()
        if not txt_files:
            self.logger.warning("入力ディレクトリにテキストファイルが見つかりません")
            return self.processed_count, self.error_count
        
        # バックアップ作成
        if self.config.should_backup():
            self.backup_original_files(txt_files)
        
        # ファイル処理
        self.logger.info(f"{len(txt_files)}個のファイルの処理を開始します...")
        
        for i, filename in enumerate(txt_files, 1):
            self.logger.info(f"処理中 ({i}/{len(txt_files)}): {filename}")
            self.process_single_file(filename)
        
        # 処理結果報告
        self.logger.info(f"処理完了: 成功 {self.processed_count}件, エラー {self.error_count}件")
        
        # 削除確認と実行
        if self.processed_count > 0 and self.confirm_deletion():
            if self.delete_original_files(txt_files):
                self.logger.info("入力ディレクトリのファイルを削除しました")
            else:
                self.logger.warning("一部のファイル削除に失敗しました")
        else:
            self.logger.info("入力ディレクトリのファイルは削除されませんでした")
        
        return self.processed_count, self.error_count


def setup_logging(log_level: str = 'INFO'):
    """ログ設定を行う"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('email_cleaner.log', encoding='utf-8')
        ]
    )


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='メール引用テキスト整形プログラム',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                    # デフォルト設定で実行
  %(prog)s --config my.ini    # 指定した設定ファイルを使用
  %(prog)s --log-level DEBUG  # デバッグレベルでログ出力
        """
    )
    
    parser.add_argument(
        '--config', 
        default='config.ini',
        help='設定ファイルのパス (デフォルト: config.ini)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='ログレベル (デフォルト: INFO)'
    )
    
    args = parser.parse_args()
    
    try:
        # ログ設定
        setup_logging(args.log_level)
        logger = logging.getLogger(__name__)
        
        logger.info("メール引用テキスト整形プログラムを開始します")
        
        # 設定読み込み
        config = EmailCleanerConfig(args.config)
        
        # メイン処理実行
        cleaner = EmailCleaner(config)
        success_count, error_count = cleaner.process_all_files()
        
        # 最終結果
        if error_count == 0:
            logger.info("すべての処理が正常に完了しました")
            exit_code = 0
        else:
            logger.warning(f"処理中にエラーが発生しました (エラー数: {error_count})")
            exit_code = 1
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n処理が中断されました")
        return 130
    except Exception as e:
        logging.error(f"予期しないエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    exit(main())