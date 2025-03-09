import os
import requests
import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk

#iftar vakitlerini almak için fonksiyon
def get_iftar_time(city):
    city = city.lower().replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o")
    url = f"https://api.collectapi.com/pray/all?data.city={city}"

    headers = {
        "content-type": "application/json",
        "authorization": "apikey your_api_key_here"  
    }

    try:
        response = requests.get(url, headers=headers)

        #debug
        print("API Status Code:", response.status_code)
        print("API Response:", response.text)

        
        data = response.json()

        
        if response.status_code != 200 or "result" not in data:
            label.config(text="API hatası! Lütfen tekrar deneyin.")
            return None

        #API'den iftar vakti olan "akşam" saatini çek
        for v in data["result"]:
            if v["vakit"] == "Akşam":  #iftar vakti = akşam namazı
                iftar_time_str = v["saat"]
                return datetime.strptime(iftar_time_str, "%H:%M").time()

        label.config(text="Şehir bulunamadı! Lütfen geçerli bir şehir seçin.")
        return None

    except Exception as e:
        print("Hata:", e)
        label.config(text="Bağlantı hatası! Lütfen tekrar deneyin.")
        return None

#geri sayım fonksiyonu
def update_timer():
    now = datetime.now()
    if iftar_vakti:
        iftar_time = datetime.combine(now.date(), iftar_vakti)
        remaining = iftar_time - now

        if remaining.total_seconds() > 0:
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            label.config(text=f"İftara: {hours} saat {minutes} dk {seconds} sn")
            root.after(1000, update_timer)
        else:
            label.config(text="İftar vakti geldi! Hayırlı iftarlar.")

#arkaplanı ayarlayan fonksiyon
def set_background():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))  
        background_path = os.path.join(script_dir, "background.png")  

        if not os.path.exists(background_path):
            print("Hata: background.png bulunamadı!")
            root.configure(bg="#1E3A8A") 
            return

        image = Image.open(background_path)
        image = image.resize((700, 500))  
        bg_image = ImageTk.PhotoImage(image)

        bg_label = tk.Label(root, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_image  

    except Exception as e:
        print("Hata:", e)
        root.configure(bg="#1E3A8A")  #resim yüklenemezse mavi arka plan kullan

#API'den veriyi getiren fonksiyon
def update_city():
    global iftar_vakti
    city = city_entry.get().strip()
    iftar_vakti = get_iftar_time(city)
    if iftar_vakti:
        update_timer()


root = tk.Tk()
root.title("İftar Sayacı")
root.geometry("700x500")  
root.resizable(False, False)  

set_background()

label = tk.Label(root, text="Şehir giriniz", font=("Lato", 16, "bold"), fg="white", bg="black", padx=20, pady=10)
label.pack(pady=10)

city_entry = tk.Entry(root, font=("Lato", 14, "bold"), width=20, bd=2, relief="solid")
city_entry.pack(pady=10)
city_entry.bind("<Return>", lambda event: update_city())

button = tk.Button(root, text="İftara Kalan Süreyi Gör", font=("Lato", 14, "bold"), command=update_city,
                   relief="raised", bg="black", fg="white", width=20, height=2)
button.pack(pady=10)

iftar_vakti = None

root.mainloop()
