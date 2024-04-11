import tkinter as tk
from tkinter import ttk, filedialog
from pytube import YouTube
import threading
import os
import subprocess

def get_video_title(url):
    yt = YouTube(url)
    return yt.title

def download_video():
    url = url_entry.get()
    save_path = save_path_entry.get()
    filename = filename_entry.get()
    resolution = resolution_var.get()

    try:
        yt = YouTube(url)
        if resolution == "En Yüksek Çözünürlük":
            stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.filter(res=resolution).first()

        # Dosya adını oluştur
        if not save_path:
            save_path = filedialog.askdirectory()
        
        if not filename:
            filename = get_video_title(url)
        
        # Dosya adını oluştur
        filepath = os.path.join(save_path, f"{filename}.mp4")

        progress_bar["value"] = 0

        # İndirme işlemi için bir thread başlat
        download_thread = threading.Thread(target=download, args=(stream, filepath))
        download_thread.start()
    except Exception as e:
        status_label.config(text=f"Hata oluştu: {e}", fg="red")

def download(stream, filepath):
    try:
        # Videoyu indir
        stream.download(output_path=os.path.dirname(filepath), filename=os.path.basename(filepath), 
                        filename_prefix="downloading_")

        # Ses akışını indir
        audio_stream = stream.audio_only
        audio_filepath = filepath.replace(".mp4", "_audio.mp4")
        audio_stream.download(output_path=os.path.dirname(audio_filepath), filename=os.path.basename(audio_filepath), 
                              filename_prefix="downloading_")

        # Ses ve videoyu birleştir
        merge_files(filepath, audio_filepath)

        # İndirme işlemi başarıyla tamamlandığında dosyayı sil
        os.remove(audio_filepath)

        status_label.config(text="İndirme başarıyla tamamlandı!", fg="green")
        progress_bar.stop()
        progress_bar["value"] = 100
    except Exception as e:
        status_label.config(text=f"Hata oluştu: {e}", fg="red")

def merge_files(video_filepath, audio_filepath):
    # FFmpeg'i kullanarak sesi videoya ekleyin
    subprocess.run(['ffmpeg', '-i', video_filepath, '-i', audio_filepath, '-c', 'copy', video_filepath.replace("_audio", "")])

# Ana Tkinter penceresi oluştur
root = tk.Tk()
root.title("YouTube Video İndirici")

# URL giriş kutusu ve etiket
url_label = tk.Label(root, text="YouTube Video URL'si:")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
url_entry = tk.Entry(root, width=40)
url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="we")

# Kaydetme yolu giriş kutusu ve etiket
save_path_label = tk.Label(root, text="Kayıt Yolu:")
save_path_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
save_path_entry = tk.Entry(root, width=30)
save_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
browse_button = tk.Button(root, text="Gözat", command=lambda: save_path_entry.insert(tk.END, filedialog.askdirectory()))
browse_button.grid(row=1, column=2, padx=5, pady=5)

# Dosya adı giriş kutusu ve etiket
filename_label = tk.Label(root, text="Dosya Adı:")
filename_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
filename_entry = tk.Entry(root, width=30)
filename_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

# Dosya adını otomatik al butonu
auto_filename_button = tk.Button(root, text="Otomatik Ad Al", command=lambda: filename_entry.insert(tk.END, get_video_title(url_entry.get())))
auto_filename_button.grid(row=2, column=2, padx=5, pady=5)

# Çözünürlük seçim etiket ve dropdown menü
resolution_label = tk.Label(root, text="Çözünürlük:")
resolution_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
resolutions = ["En Yüksek Çözünürlük", "360p", "480p", "720p", "1080p"]
resolution_var = tk.StringVar(root)
resolution_var.set(resolutions[0])  # Başlangıçta en yüksek çözünürlüğü seç
resolution_menu = tk.OptionMenu(root, resolution_var, *resolutions)
resolution_menu.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="we")

# İndirme butonu
download_button = tk.Button(root, text="İndir", command=download_video)
download_button.grid(row=4, column=1, columnspan=2, pady=10)

# İlerleme çubuğu
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", maximum=100)
progress_bar.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="we")

# Durum etiketi
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=6, column=0, columnspan=3)

root.mainloop()
