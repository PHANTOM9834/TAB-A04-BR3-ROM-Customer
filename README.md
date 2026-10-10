# CT3ROMCustomer
チャレンジタッチ3 TAB-A04-BR3 のsystem.img、factory.imgを編集するための自動化GUIツールです。システムアプリの追加・削除 GAppsの追加 起動アニメーション変更 アラーム音、通知音、着信音の追加・削除 です。system.imgのマウント、編集、アンマウントまで全てGUIで行えます。
# Android System & Factory Image Patcher

Zorin OS等のLinux環境で、Androidの `system.img` や `factory.img` をマウントし、アプリの追加・削除、GAppsの自動統合、起動アニメーションの変更、音声の追加、およびDCHAモードのバイパス処理などをグラフィカルに行うためのPythonツールです。

## 動作環境
* Linux (Zorin OS / Ubuntu / Debian 系を推奨)
* Python 3.8 以上
* `sudo` 権限（イメージのマウント・ファイル操作に必要）

---

## 必要なシステムツールのインストール

あらかじめ、OS側に必要な外部コマンド（`lzip`, `ffmpeg`, `python3-tk`）をインストールしてください。

```bash
sudo apt update
sudo apt install -y python3-tk lzip ffmpeg
```

# 仮想環境（venv）の構築とライブラリのインストール
*リポジトリをクローンまたはダウンロードした後、プロジェクトフォルダ内で以下の手順を実行して仮想環境を構築します。

1. 仮想環境の作成
```bash
python3 -m venv venv
```
2. 仮想環境のアクティベート（有効化）
```bash
source venv/bin/activate
#ターミナルの表示が (venv) に変われば有効化完了です
```
3. 必要なPythonライブラリのインストール
```bash
pip install --upgrade pip
pip install customtkinter Pillow
```
# 使い方
* 仮想環境を有効化した状態で、それぞれのスクリプトを実行します。
* 実行時に `sudo` コマンドを使用するため端末アプリ側でパスワードを求められます。
システムイメージパッチャーの起動:
```bash
python3 CT3_ROMCustomer.py
```
ファクトリーイメージパッチャー（DCHAバイパス）の起動:
```bash
python3 factory_img_edit.py
```


注意: イメージファイル（.img）のループマウントやシステム領域への書き込みを行うため、実行時には管理者権限（sudo）を伴う操作が含まれます。対応環境にて自己責任でご利用ください。
