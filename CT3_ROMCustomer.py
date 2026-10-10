import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import customtkinter as ctk
from PIL import Image, ImageOps

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RomPatcherApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Android Ultimate System Image Patcher")
    self.geometry("640x830")
    
    self.label_img = ctk.CTkLabel(self, text="system.imgのパス:")
    self.label_img.pack(pady=(15, 5), padx=30)

    self.frame_img = ctk.CTkFrame(self, fg_color="transparent")
    self.frame_img.pack(padx=30)

    self.entry_img = ctk.CTkEntry(self.frame_img, width=340)
    self.entry_img.pack(side="left", padx=(0, 10))

    self.btn_browse_img = ctk.CTkButton(
        self.frame_img, text="参照...", width=70, command=self.select_img
    )
    self.btn_browse_img.pack(side="left", padx=(0, 5))

    self.btn_umount = ctk.CTkButton(
        self.frame_img, text="アンマウント", width=70, fg_color="darkred", hover_color="firebrick",
        command=self.manual_unmount
    )
    self.btn_umount.pack(side="left")

    self.tabview = ctk.CTkTabview(self, width=580, height=360)
    self.tabview.pack(padx=30, pady=10)

    self.tab_app_add = self.tabview.add("アプリ追加")
    self.tab_app_rem = self.tabview.add("アプリ削除")
    self.tab_gapps = self.tabview.add("GApps追加")
    self.tab_bootanim = self.tabview.add("起動アニメ")
    self.tab_audio = self.tabview.add("音声(アラーム/通知/着信)")

    self.label_app = ctk.CTkLabel(self.tab_app_add, text="追加するアプリフォルダのパス:")
    self.label_app.pack(pady=(10, 5))

    self.frame_add_input = ctk.CTkFrame(self.tab_app_add, fg_color="transparent")
    self.frame_add_input.pack(pady=5)

    self.entry_app = ctk.CTkEntry(self.frame_add_input, width=420)
    self.entry_app.pack(side="left", padx=(0, 10))

    self.btn_browse_app = ctk.CTkButton(
        self.frame_add_input, text="参照...", width=70, command=self.select_app_dir
    )
    self.btn_browse_app.pack(side="left")

    self.label_dest = ctk.CTkLabel(self.tab_app_add, text="配置先ディレクトリ:")
    self.label_dest.pack(pady=(10, 5))

    self.dest_var = ctk.StringVar(value="priv-app")
    self.segment_dest = ctk.CTkSegmentedButton(
        self.tab_app_add, values=["priv-app", "app"], variable=self.dest_var, width=420
    )
    self.segment_dest.pack(pady=5)

    self.btn_run_add = ctk.CTkButton(
        self.tab_app_add,
        text="アプリを追加して再パック",
        fg_color="green",
        hover_color="darkgreen",
        command=self.run_add_patch,
    )
    self.btn_run_add.pack(pady=15)

    self.label_rem_dest = ctk.CTkLabel(self.tab_app_rem, text="検索・削除対象ディレクトリ:")
    self.label_rem_dest.pack(pady=(10, 5))

    self.rem_dest_var = ctk.StringVar(value="priv-app")
    self.segment_rem_dest = ctk.CTkSegmentedButton(
        self.tab_app_rem,
        values=["priv-app", "app"],
        variable=self.rem_dest_var,
        command=self.on_rem_dest_changed,
        width=420,
    )
    self.segment_rem_dest.pack(pady=5)

    self.frame_rem_select = ctk.CTkFrame(self.tab_app_rem, fg_color="transparent")
    self.frame_rem_select.pack(pady=10)

    self.btn_fetch_list = ctk.CTkButton(
        self.frame_rem_select, text="一覧取得", width=90, command=self.fetch_app_list
    )
    self.btn_fetch_list.pack(side="left", padx=(0, 10))

    self.app_list_var = ctk.StringVar(value="（先に一覧を取得）")
    self.option_apps = ctk.CTkOptionMenu(
        self.frame_rem_select, values=["（先に一覧を取得）"], variable=self.app_list_var, width=320
    )
    self.option_apps.pack(side="left")

    self.btn_run_rem = ctk.CTkButton(
        self.tab_app_rem,
        text="選択したアプリを削除",
        fg_color="darkred",
        hover_color="firebrick",
        command=self.run_remove_patch,
    )
    self.btn_run_rem.pack(pady=15)

    self.label_gapps = ctk.CTkLabel(self.tab_gapps, text="GAppsのZIPファイルパス:")
    self.label_gapps.pack(pady=(15, 5))

    self.frame_gapps = ctk.CTkFrame(self.tab_gapps, fg_color="transparent")
    self.frame_gapps.pack(padx=30)

    self.entry_gapps = ctk.CTkEntry(self.frame_gapps, width=420)
    self.entry_gapps.pack(side="left", padx=(0, 10))

    self.btn_browse_gapps = ctk.CTkButton(
        self.frame_gapps, text="参照...", width=70, command=self.select_gapps_zip
    )
    self.btn_browse_gapps.pack(side="left")

    self.btn_run_gapps = ctk.CTkButton(
        self.tab_gapps,
        text="GAppsを自動展開して適用する",
        fg_color="green",
        hover_color="darkgreen",
        command=self.run_gapps_patch,
        height=40,
    )
    self.btn_run_gapps.pack(pady=25)

    self.label_anim = ctk.CTkLabel(self.tab_bootanim, text="起動ロゴ画像 (1280x800推奨) または フォルダ:")
    self.label_anim.pack(pady=(10, 5))

    self.frame_anim = ctk.CTkFrame(self.tab_bootanim, fg_color="transparent")
    self.frame_anim.pack(pady=5)

    self.entry_anim = ctk.CTkEntry(self.frame_anim, width=420)
    self.entry_anim.pack(side="left", padx=(0, 10))

    self.btn_browse_anim = ctk.CTkButton(
        self.frame_anim, text="参照...", width=70, command=self.select_anim_source
    )
    self.btn_browse_anim.pack(side="left")

    self.btn_run_anim = ctk.CTkButton(
        self.tab_bootanim,
        text="bootanimation.zip を生成して適用",
        fg_color="green",
        hover_color="darkgreen",
        command=self.run_bootanim_patch,
    )
    self.btn_run_anim.pack(pady=25)

    self.label_audio_cat = ctk.CTkLabel(self.tab_audio, text="対象カテゴリ選択:")
    self.label_audio_cat.pack(pady=(5, 2))

    self.audio_cat_var = ctk.StringVar(value="alarms")
    self.segment_audio_cat = ctk.CTkSegmentedButton(
        self.tab_audio,
        values=["alarms", "notifications", "ringtones"],
        variable=self.audio_cat_var,
        width=420,
    )
    self.segment_audio_cat.pack(pady=2)

    self.label_audio_file = ctk.CTkLabel(self.tab_audio, text="追加する音声ファイル (mp3/ogg等):")
    self.label_audio_file.pack(pady=(5, 2))

    self.frame_audio_input = ctk.CTkFrame(self.tab_audio, fg_color="transparent")
    self.frame_audio_input.pack(pady=2)

    self.entry_audio = ctk.CTkEntry(self.frame_audio_input, width=420)
    self.entry_audio.pack(side="left", padx=(0, 10))

    self.btn_browse_audio = ctk.CTkButton(
        self.frame_audio_input, text="参照...", width=70, command=self.select_audio_file
    )
    self.btn_browse_audio.pack(side="left")

    self.frame_audio_btns = ctk.CTkFrame(self.tab_audio, fg_color="transparent")
    self.frame_audio_btns.pack(pady=10)

    self.btn_run_audio_add = ctk.CTkButton(
        self.frame_audio_btns,
        text="OGG変換して追加",
        fg_color="green",
        hover_color="darkgreen",
        width=200,
        command=self.run_audio_add_patch,
    )
    self.btn_run_audio_add.pack(side="left", padx=10)

    self.btn_fetch_audio = ctk.CTkButton(
        self.frame_audio_btns,
        text="一覧取得して削除",
        fg_color="darkred",
        hover_color="firebrick",
        width=200,
        command=self.run_audio_remove_dialog,
    )
    self.btn_fetch_audio.pack(side="left", padx=10)

    self.text_log = ctk.CTkTextbox(self, width=580, height=90)
    self.text_log.pack(padx=30, pady=(0, 10))

    warning_text = (
        "【重要なお知らせと免責事項】\n"
        "1. 本ツールはAndroidシステムのパーティション書き換えを行う高度なツールです。\n"
        "2. 誤った操作や不具合による機器の破損について、作者は一切責任を負いません。\n"
        "3. ZorinOS等の対応環境にてroot権限（sudo）を利用して実行してください。"
    )
    self.text_warning = ctk.CTkTextbox(self, width=580, height=75, text_color="red")
    self.text_warning.pack(padx=30, pady=(0, 10))
    self.text_warning.insert("0.0", warning_text)
    self.text_warning.configure(state="disabled")

  def select_img(self):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.img"), ("All Files", "*.*")])
    if file_path:
      self.entry_img.delete(0, tk.END)
      self.entry_img.insert(0, file_path)

  def select_app_dir(self):
    dir_path = filedialog.askdirectory()
    if dir_path:
      self.entry_app.delete(0, tk.END)
      self.entry_app.insert(0, dir_path)

  def select_gapps_zip(self):
    file_path = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")])
    if file_path:
      self.entry_gapps.delete(0, tk.END)
      self.entry_gapps.insert(0, file_path)

  def select_anim_source(self):
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")])
    if not path:
      path = filedialog.askdirectory()
    if path:
      self.entry_anim.delete(0, tk.END)
      self.entry_anim.insert(0, path)

  def select_audio_file(self):
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.ogg;*.wav;*.m4a"), ("All Files", "*.*")])
    if file_path:
      self.entry_audio.delete(0, tk.END)
      self.entry_audio.insert(0, file_path)

  def log(self, message):
    self.text_log.insert(tk.END, message + "\n")
    self.text_log.see(tk.END)

  def manual_unmount(self):
    """手動で一般的なマウントポイントや残りやすい領域のアンマウントを試みる"""
    self.log("=== [手動アンマウント] 実行中 ===")
    targets = ["/home/pc/sys"]

    success_count = 0
    for target in targets:
      if os.path.exists(target):
        try:
          res = subprocess.run(["sudo", "umount", target], capture_output=True, text=True)
          if res.returncode == 0:
            self.log(f"アンマウント成功: {target}")
            success_count += 1
          else:
            self.log(f"すでにアンマウントされているか対象外です: {target}")
        except Exception as e:
          self.log(f"エラー ({target}): {e}")

    messagebox.showinfo("完了", "手動アンマウント処理を試行しました。")

  def mount_image(self, img_path, mount_point):
    self.log(f"マウント先を作成中: {mount_point}")
    subprocess.run(["sudo", "mkdir", "-p", mount_point], check=True)
    self.log("system.imgをマウント中...")
    subprocess.run(["sudo", "mount", "-o", "loop,rw", img_path, mount_point], check=True)

    mount_check = subprocess.run(["findmnt", "-n", "-o", "OPTIONS", mount_point], capture_output=True, text=True)
    if "ro" in mount_check.stdout:
      raise Exception("エラー: system.imgが読み込み専用 (ro) でマウントされました！")

  def check_and_install_dependencies(self):
    self.log("システム依存ツール（lzip）の有無を確認中...")
    check = subprocess.run(["which", "lzip"], capture_output=True, text=True)
    if check.returncode != 0:
      self.log("警告: 'lzip' が見つかりません。自動インストールを試みます...")
      try:
        subprocess.run(["sudo", "apt", "update"], capture_output=True, text=True)
        install_res = subprocess.run(["sudo", "apt", "install", "-y", "lzip"], capture_output=True, text=True)
        if install_res.returncode == 0:
          self.log("'lzip' のインストールに成功しました！")
        else:
          raise Exception(f"インストール失敗: {install_res.stderr}")
      except Exception as e:
        raise Exception(f"依存ツールの自動インストールに失敗しました:\n{e}\n手動で 'sudo apt install lzip' を実行してください。")
    else:
      self.log("依存ツール（lzip）は正常に導入されています。")

  def on_rem_dest_changed(self, selected_value):
    img_path = self.entry_img.get()
    if img_path and os.path.exists(img_path):
      self.fetch_app_list()

  def fetch_app_list(self):
    img_path = self.entry_img.get()
    selected_dest = self.rem_dest_var.get()
    if not img_path:
      messagebox.showerror("エラー", "先にsystem.imgを選択してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    try:
      self.mount_image(img_path, mount_point)
      target_dir = f"{mount_point}/{selected_dest}"
      if not os.path.exists(target_dir):
        self.option_apps.configure(values=["（見つかりません）"])
        return
      items = os.listdir(target_dir)
      folders = sorted([item for item in items if os.path.isdir(os.path.join(target_dir, item))])
      if folders:
        self.option_apps.configure(values=folders)
        self.app_list_var.set(folders[0])
      else:
        self.option_apps.configure(values=["（アプリなし）"])
    except Exception as e:
      messagebox.showerror("エラー", f"一覧取得失敗:\n{e}")
    finally:
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except:
        pass

  def run_add_patch(self):
    img_path, app_dir, selected_dest = self.entry_img.get(), self.entry_app.get(), self.dest_var.get()
    if not img_path or not app_dir:
      messagebox.showerror("エラー", "イメージパスとアプリフォルダを指定してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    self.log("=== [アプリ追加] 開始 ===")
    try:
      self.mount_image(img_path, mount_point)
      target_base = f"{mount_point}/{selected_dest}"
      subprocess.run(["sudo", "mkdir", "-p", target_base], check=True)
      subprocess.run(["sudo", "cp", "-r", app_dir, target_base], check=True)
      folder_name = os.path.basename(os.path.normpath(app_dir))
      target_path = f"{target_base}/{folder_name}"

      subprocess.run(["sudo", "chown", "-R", "0:0", target_path], check=True)
      subprocess.run(["sudo", "find", target_path, "-type", "d", "-exec", "chmod", "755", "{}", "+"], check=True)
      subprocess.run(["sudo", "find", target_path, "-type", "f", "-exec", "chmod", "644", "{}", "+"], check=True)
      subprocess.run(["sudo", "chcon", "-R", "u:object_r:system_file:s0", target_path], check=True)
      subprocess.run(["sudo", "sync"], check=True)

      messagebox.showinfo("成功", "アプリの追加が完了しました。")
    except Exception as e:
      messagebox.showerror("エラー", f"処理失敗:\n{e}")
    finally:
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except:
        pass

  def run_remove_patch(self):
    img_path, app_name, selected_dest = self.entry_img.get(), self.app_list_var.get(), self.rem_dest_var.get()
    if not img_path or app_name.startswith("（"):
      messagebox.showerror("エラー", "削除するアプリが選択されていません。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    self.log(f"=== [アプリ削除] 開始 ({app_name}) ===")
    success = False
    try:
      self.mount_image(img_path, mount_point)
      target_path = f"{mount_point}/{selected_dest}/{app_name}"
      subprocess.run(["sudo", "rm", "-rf", target_path], check=True)
      subprocess.run(["sudo", "sync"], check=True)
      messagebox.showinfo("成功", f"アプリ '{app_name}' を削除しました。")
      success = True
    except Exception as e:
      messagebox.showerror("エラー", f"処理失敗:\n{e}")
    finally:
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except:
        pass
    if success:
      self.fetch_app_list()

  def run_gapps_patch(self):
    img_path = self.entry_img.get()
    gapps_zip = self.entry_gapps.get()

    if not img_path:
      messagebox.showerror("エラー", "system.imgを選択してください。")
      return
    if not gapps_zip:
      messagebox.showerror("エラー", "GAppsのZIPファイルを選択してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    self.log("=== [GApps自動適用] 処理を開始します ===")

    try:
      self.check_and_install_dependencies()
      self.mount_image(img_path, mount_point)

      self.log("GAppsのZIPファイルを一時解凍中...")
      with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(gapps_zip, "r") as zf:
          zf.extractall(temp_dir)

        target_dirs = ["Core", "GApps"]
        found_folders = []
        for root, dirs, files in os.walk(temp_dir):
          for d in dirs:
            if d in target_dirs:
              found_folders.append(os.path.join(root, d))

        if not found_folders:
          raise Exception("エラー: ZIP内に 'Core' または 'GApps' フォルダが見つかりませんでした。")

        extracted_count = 0
        for sub_path in found_folders:
          for file_name in os.listdir(sub_path):
            if file_name.endswith(".tar.lz"):
              tarlz_path = os.path.join(sub_path, file_name)
              extract_sub = os.path.join(temp_dir, "extracted_" + file_name)
              os.makedirs(extract_sub, exist_ok=True)

              cmd = f"lzip -d -c '{tarlz_path}' | tar -xf - -C '{extract_sub}'"
              res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
              if res.returncode != 0:
                continue

              merged_any = False
              for root_ex, dirs_ex, files_ex in os.walk(extract_sub):
                if os.path.basename(root_ex) == "system":
                  cp_res = subprocess.run(["sudo", "cp", "-r", f"{root_ex}/.", mount_point], capture_output=True, text=True)
                  if cp_res.returncode == 0:
                    merged_any = True
                elif os.path.basename(root_ex) in ["app", "priv-app", "etc", "framework", "lib", "lib64"]:
                  dest_sub_path = os.path.join(mount_point, os.path.basename(root_ex))
                  os.makedirs(dest_sub_path, exist_ok=True)
                  cp_res = subprocess.run(["sudo", "cp", "-r", f"{root_ex}/.", dest_sub_path], capture_output=True, text=True)
                  if cp_res.returncode == 0:
                    merged_any = True

              if merged_any:
                extracted_count += 1
                self.log(f"  -> 統合成功: {file_name}")

        self.log(f"合計 {extracted_count} 個のパッケージを展開・統合しました。")

      self.log("システム領域全体の権限とSELinuxコンテキストを再設定中...")
      for folder in ["app", "priv-app", "etc", "framework", "lib", "lib64"]:
        target_f = os.path.join(mount_point, folder)
        if os.path.exists(target_f):
          subprocess.run(["sudo", "chown", "-R", "0:0", target_f], check=False)
          subprocess.run(["sudo", "find", target_f, "-type", "d", "-exec", "chmod", "755", "{}", "+"], check=False)
          subprocess.run(["sudo", "find", target_f, "-type", "f", "-exec", "chmod", "644", "{}", "+"], check=False)
          subprocess.run(["sudo", "chcon", "-R", "u:object_r:system_file:s0", target_f], check=False)

      self.log("変更をディスクに同期中 (sync)...")
      subprocess.run(["sudo", "sync"], check=True)

      messagebox.showinfo("成功", "GAppsの自動展開と適用が正常に完了しました。")

    except Exception as e:
      self.log(f"[エラー発生]: {e}")
      messagebox.showerror("エラー", f"処理に失敗しました:\n{e}")

    finally:
      self.log("アンマウント処理を実行中...")
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
        self.log("アンマウント完了。")
      except Exception as ex:
        self.log(f"アンマウント時のエラー: {ex}")

  def run_bootanim_patch(self):
    img_path, source_path = self.entry_img.get(), self.entry_anim.get()
    if not img_path or not source_path:
      messagebox.showerror("エラー", "イメージパスとロゴ画像/フォルダを指定してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    temp_zip = tempfile.mktemp(suffix=".zip")
    self.log("=== [起動アニメーション変更] 開始 ===")
    try:
      with tempfile.TemporaryDirectory() as tmp_dir:
        part_dir = os.path.join(tmp_dir, "part1")
        os.makedirs(part_dir, exist_ok=True)
        with open(os.path.join(tmp_dir, "desc.txt"), "w", encoding="ascii") as f:
          f.write("1280 800 30\np 0 0 part1\n")

        if os.path.isfile(source_path):
          img = Image.open(source_path)
          img_resized = ImageOps.fit(img, (1280, 800), Image.Resampling.LANCZOS)
          img_resized.save(os.path.join(part_dir, "00001.png"))
        elif os.path.isdir(source_path):
          files = sorted([f for f in os.listdir(source_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
          for i, file in enumerate(files):
            img = Image.open(os.path.join(source_path, file))
            img_resized = ImageOps.fit(img, (1280, 800), Image.Resampling.LANCZOS)
            img_resized.save(os.path.join(part_dir, f"{i+1:05d}.png"))

        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_STORED) as zf:
          zf.write(os.path.join(tmp_dir, "desc.txt"), "desc.txt")
          for root, _, filenames in os.walk(part_dir):
            for filename in filenames:
              abs_path = os.path.join(root, filename)
              zf.write(abs_path, os.path.relpath(abs_path, tmp_dir))

      self.mount_image(img_path, mount_point)
      target_media_dir = f"{mount_point}/system/media"
      if not os.path.exists(target_media_dir):
        target_media_dir = f"{mount_point}/media"
      subprocess.run(["sudo", "mkdir", "-p", target_media_dir], check=True)
      target_zip_path = os.path.join(target_media_dir, "bootanimation.zip")

      subprocess.run(["sudo", "cp", temp_zip, target_zip_path], check=True)
      subprocess.run(["sudo", "chown", "0:0", target_zip_path], check=True)
      subprocess.run(["sudo", "chmod", "644", target_zip_path], check=True)
      subprocess.run(["sudo", "chcon", "u:object_r:system_file:s0", target_zip_path], check=True)
      subprocess.run(["sudo", "sync"], check=True)

      messagebox.showinfo("成功", "起動アニメーションの変更が完了しました。")
    except Exception as e:
      messagebox.showerror("エラー", f"処理失敗:\n{e}")
    finally:
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except:
        pass
      if os.path.exists(temp_zip):
        os.remove(temp_zip)

  def run_audio_add_patch(self):
    img_path = self.entry_img.get()
    audio_path = self.entry_audio.get()
    category = self.audio_cat_var.get()

    if not img_path or not audio_path:
      messagebox.showerror("エラー", "イメージパスと音声ファイルを選択してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    self.log(f"=== [音声追加: {category}] 開始 ===")
    try:
      base_name = os.path.splitext(os.path.basename(audio_path))[0]
      output_ogg_name = f"{base_name}.ogg"
      temp_ogg = tempfile.mktemp(suffix=".ogg")

      cmd_ffmpeg = ["ffmpeg", "-y", "-i", audio_path, "-acodec", "libvorbis", temp_ogg]
      res = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)
      if res.returncode != 0:
        raise Exception(f"FFmpeg変換失敗:\n{res.stderr}")

      self.mount_image(img_path, mount_point)
      target_dir = f"{mount_point}/system/media/audio/{category}"
      if not os.path.exists(target_dir):
        target_dir = f"{mount_point}/media/audio/{category}"

      subprocess.run(["sudo", "mkdir", "-p", target_dir], check=True)
      target_file_path = os.path.join(target_dir, output_ogg_name)

      subprocess.run(["sudo", "cp", temp_ogg, target_file_path], check=True)
      subprocess.run(["sudo", "chown", "0:0", target_file_path], check=True)
      subprocess.run(["sudo", "chmod", "644", target_file_path], check=True)
      subprocess.run(["sudo", "chcon", "u:object_r:system_file:s0", target_file_path], check=True)
      subprocess.run(["sudo", "sync"], check=True)

      messagebox.showinfo("成功", f"'{output_ogg_name}' を {category} に追加しました。")
    except Exception as e:
      messagebox.showerror("エラー", f"処理失敗:\n{e}")
    finally:
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except:
        pass
      if os.path.exists(temp_ogg):
        os.remove(temp_ogg)

  def run_audio_remove_dialog(self):
    img_path = self.entry_img.get()
    category = self.audio_cat_var.get()
    if not img_path:
      messagebox.showerror("エラー", "先にsystem.imgを選択してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    try:
      self.mount_image(img_path, mount_point)
      target_dir = f"{mount_point}/system/media/audio/{category}"
      if not os.path.exists(target_dir):
        target_dir = f"{mount_point}/media/audio/{category}"

      if not os.path.exists(target_dir):
        messagebox.showwarning("警告", f"ディレクトリが存在しません: {category}")
        return

      files = sorted([f for f in os.listdir(target_dir) if f.endswith('.ogg')])
      if not files:
        messagebox.showinfo("情報", "削除可能なoggファイルが見つかりません。")
        return

      top = ctk.CTkToplevel(self)
      top.title(f"{category} の削除")
      top.geometry("380x200")

      ctk.CTkLabel(top, text=f"削除する {category} のファイルを選択:").pack(pady=15)
      selected_file_var = ctk.StringVar(value=files[0])
      menu = ctk.CTkOptionMenu(top, values=files, variable=selected_file_var, width=320)
      menu.pack(pady=10)

      def execute_removal():
        target_file = os.path.join(target_dir, selected_file_var.get())
        try:
          subprocess.run(["sudo", "rm", "-f", target_file], check=True)
          subprocess.run(["sudo", "sync"], check=True)
          messagebox.showinfo("成功", f"'{selected_file_var.get()}' を削除しました。")
          top.destroy()
        except Exception as e:
          messagebox.showerror("エラー", f"削除失敗:\n{e}")

      ctk.CTkButton(top, text="削除を実行", fg_color="darkred", hover_color="firebrick", command=execute_removal).pack(pady=15)

    except Exception as e:
      messagebox.showerror("エラー", f"一覧取得失敗:\n{e}")
    finally:
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
      except:
        pass

if __name__ == "__main__":
  app = RomPatcherApp()
  app.mainloop()
