import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import tempfile

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FactoryPatcherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Android Factory Image Patcher (DCHA Mode Bypass)")
        self.geometry("620x620")

        self.label_img = ctk.CTkLabel(self, text="factory.imgのパス:")
        self.label_img.pack(pady=(15, 5), padx=30)

        self.frame_img = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_img.pack(padx=30)

        self.entry_img = ctk.CTkEntry(self.frame_img, width=420)
        self.entry_img.pack(side="left", padx=(0, 10))

        self.btn_browse_img = ctk.CTkButton(
            self.frame_img, text="参照...", width=70, command=self.select_img
        )
        self.btn_browse_img.pack(side="left")

        self.btn_run = ctk.CTkButton(
            self,
            text="factory.img パッチを適用",
            fg_color="green",
            hover_color="darkgreen",
            width=500,
            command=self.run_factory_patch,
        )
        self.btn_run.pack(pady=20)

        self.text_log = ctk.CTkTextbox(self, width=560, height=130)
        self.text_log.pack(padx=30, pady=(0, 15))

        warning_text = (
            "【重要なお知らせと免責事項】\n"
            "1. 本ツールは端末のファームウェアパーティションを改変する高度なツールです。\n"
            "2. 誤った操作や不具合により、デバイスが起動しなくなる等のリスクがあります。\n"
            "3. 本ツールの使用によるいかなるデータの損失、機器の破損についても、\n"
            "   作者は一切の責任を負いません。自己責任でご利用ください。\n"
            "4. ZorinOS等の対応環境にて、root権限（sudo）が利用できる状態で行ってください。"
        )

        self.text_warning = ctk.CTkTextbox(
            self, width=560, height=110, text_color="red"
        )
        self.text_warning.pack(padx=30, pady=(0, 15))

        self.text_warning.insert("0.0", warning_text)
        self.text_warning.configure(state="disabled")

    def select_img(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.img"), ("All Files", "*.*")]
        )
        if file_path:
            self.entry_img.delete(0, tk.END)
            self.entry_img.insert(0, file_path)

    def log(self, message):
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)

    def run_factory_patch(self):
        img_path = self.entry_img.get()

        if not img_path:
            messagebox.showerror("エラー", "factory.imgを選択してください。")
            return

        if not os.path.exists(img_path):
            messagebox.showerror("エラー", f"指定されたファイルが存在しません:\n{img_path}")
            return

        mount_point = tempfile.mkdtemp(prefix="factory_mount_")
        self.log(f"=== [factory.img パッチ処理] 開始 ===")
        self.log(f"一時マウント先を作成: {mount_point}")

        try:
            self.log("factory.imgをマウント中...")
            subprocess.run(
                ["sudo", "mount", "-o", "loop,rw", img_path, mount_point],
                check=True
            )

            target_file1 = os.path.join(mount_point, "count_dcha_completed")
            if os.path.exists(target_file1):
                self.log("count_dcha_completed を削除中...")
                subprocess.run(["sudo", "rm", "-f", target_file1], check=True)
            else:
                self.log("count_dcha_completed は存在しないためスキップします。")

            target_file2 = os.path.join(mount_point, "ignore_dcha_completed")
            self.log("ignore_dcha_completed を作成中...")
            subprocess.run(["sudo", "touch", target_file2], check=True)

            target_file3 = os.path.join(mount_point, "dcha_hash")
            self.log("dcha_hash にSHA-256ハッシュを書き込み中...")
            hash_cmd = f"sudo sh -c \"echo -n '' | sha256sum | cut -c-64 > {target_file3}\""
            subprocess.run(hash_cmd, shell=True, check=True)

            self.log("dcha_hash に読み込み権限 (o+r) を付与中...")
            subprocess.run(["sudo", "chmod", "o+r", target_file3], check=True)

            subprocess.run(["sudo", "sync"], check=True)

            self.log("パッチ処理が正常に完了しました！")
            messagebox.showinfo("成功", "factory.img のパッチ適用が完了しました。")

        except subprocess.CalledProcessError as e:
            self.log(f"[コマンドエラー]: {e}")
            messagebox.showerror("エラー", f"処理中にコマンドエラーが発生しました:\n{e}")
        except Exception as e:
            self.log(f"[エラー発生]: {e}")
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました:\n{e}")

        finally:
            self.log("アンマウント処理を実行中...")
            try:
                subprocess.run(["sudo", "umount", mount_point], check=True)
                self.log("アンマウント完了。")
            except Exception as ex:
                self.log(f"アンマウント時のエラー: {ex}")

            try:
                os.rmdir(mount_point)
            except Exception:
                pass

if __name__ == "__main__":
    app = FactoryPatcherApp()
    app.mainloop()
