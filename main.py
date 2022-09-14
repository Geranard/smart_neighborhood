from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager, FadeTransition, SlideTransition
from kivymd.uix.list import TwoLineListItem, ThreeLineListItem, OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
import firebase_admin as firebase
from firebase_admin import db
import json
import datetime as dt
import re
import hashlib

cred = firebase.credentials.Certificate(f"./smartneighborhood-1-firebase-adminsdk-ganee-d52ac06006.json")
db_url = "https://smartneighborhood-1-default-rtdb.firebaseio.com/"
default_app = firebase.initialize_app(cred, {"databaseURL": db_url})
logged_in = ""
nomor_induk_kependudukan = ""

class Firebase:
    def __init__(self, ref):
        self.reference = db.reference(f"/{ref}")

    def is_registered(self, **kwargs):
        mode = kwargs["mode"]

        data = self.reference.get()
        try:
            for key in data:
                pass
        except:
            return False

        if mode == "login":
            global logged_in, nomor_induk_kependudukan
            username = str(kwargs["username"])
            password = str(kwargs["password"])
            for key in data:
                if (key == username or data[key]["email"] == username or data[key]["no_telepon"]) and str(data[key]["password"]) == str(self.encrypt(password)):
                    logged_in = str(data[key]["nama_lengkap"])
                    nomor_induk_kependudukan = str(key)
                    return True

        elif mode == "register":
            nik = str(kwargs["nik"])
            email = str(kwargs["email"])
            no_telepon = str(kwargs["no_telepon"])
            for key in data:
                if key == nik or str(data[key]["email"]) == email or str(data[key]["no_telepon"]) == no_telepon:
                    return True

        return False

    def encrypt(self, password):
        return str(hashlib.sha256(password.encode("utf-8")).hexdigest())

    def get_schedule(self):
        global nomor_induk_kependudukan
        prov = ""
        kab_kota = ""
        kec = ""
        kel = ""
        rw = ""
        rt = ""

        users = db.reference("/users")
        data = users.get()
        data = data[nomor_induk_kependudukan]
        prov = data["provinsi"]
        kab_kota = data["kab_kota"]
        kec = data["kecamatan"]
        kel = data["kelurahan"]
        rw = data["rw"]
        rt = data["rt"]

        refer = db.reference(f"/wilayah/{prov}/{kab_kota}/{kec}/{kel}/{rw}/{rt}/schedule")
        data = refer.get()
        try:
            for _ in data:
                return data
        except:
            return False

    def get_laporan(self):
        global nomor_induk_kependudukan

        laporan = db.reference(f"/laporan/{nomor_induk_kependudukan}")
        data = laporan.get()
        try:
            for _ in data:
                return data
        except:
            return False

    def get_kegiatan(self):
        global nomor_induk_kependudukan

    def get_riwayat_kas(self):
        global nomor_induk_kependudukan

        riwayat = self.reference.get()
        value = []
        for key, val in riwayat.items():
            val = val.replace("'", '"')
            val = json.loads(val)
            value.append(val)

        for item in value:
            try:
                return item[nomor_induk_kependudukan]
            except KeyError:
                pass

class TemplateWindow(MDFloatLayout):
    template_label = StringProperty("")
    template_source = StringProperty("")

class RegisterTextField(MDTextField):
    hint_text = StringProperty("")
    helper_text = StringProperty("")

# masih ngebug di pengurus itemnya, cek lagi nanti
class PengurusListItem(OneLineAvatarIconListItem):
    icon = StringProperty("")

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''custom right checkbox'''

class SplashWindow(MDScreen):
    def on_enter(self, *args):
        Clock.schedule_once(self.switch_to_home, 3)

    def switch_to_home(self, dt):
        self.manager.transition = FadeTransition()
        self.manager.current = "login"
        self.manager.transition = SlideTransition()

class LoginWindow(MDScreen):
    username = ObjectProperty(None)
    passwd = ObjectProperty(None)
    show_passwd_img = ObjectProperty(None)
    false_cred = ObjectProperty(None)
    fb = Firebase("users")

    def show_pass(self):
        if(self.ids.passwd.password == True):
            self.ids.show_passwd_img.icon = "eye-off"
            self.ids.passwd.password = False
        else:
            self.ids.show_passwd_img.icon = "eye"
            self.ids.passwd.password = True

    def login(self):
        valid = self.fb.is_registered(username=self.ids.username.text, password=self.ids.passwd.text, mode="login")
        if valid == True:
            self.ids.false_cred.text = ""
            self.ids.username.text = ""
            self.ids.passwd.text = ""
        else:
            self.ids.false_cred.text = "Username atau Password Salah"
            self.ids.username.text = ""
            self.ids.passwd.text = ""
        return valid

class RegisterWindow(MDScreen):
    full_name = ObjectProperty(None)
    passwd = ObjectProperty(None)
    verif_passwd = ObjectProperty(None)
    nik = ObjectProperty(None)
    email = ObjectProperty(None)
    telp = ObjectProperty(None)
    provinsi = ObjectProperty(None)
    kab_kota = ObjectProperty(None)
    kecamatan = ObjectProperty(None)
    kelurahan = ObjectProperty(None)
    rw = ObjectProperty(None)
    rt = ObjectProperty(None)
    show_passwd_img = ObjectProperty(None)
    show_verif_passwd_img = ObjectProperty(None)
    false_cred = ObjectProperty(None)
    fb = Firebase("users")

    def error_label(self, msg_label):
        self.ids.false_cred.text = f"{msg_label}"
        self.ids.false_cred.pos_hint = {"center": (0.5, 0.15)}
        return False

    def show_pass(self):
        if(self.ids.passwd.password == True):
            self.ids.show_passwd_img.icon = "eye-off"
            self.ids.passwd.password = False
        else:
            self.ids.show_passwd_img.icon = "eye"
            self.ids.passwd.password = True

    def show_verif_pass(self):
        if(self.ids.verif_passwd.password == True):
            self.ids.show_verif_passwd_img.icon = "eye-off"
            self.ids.verif_passwd.password = False
        else:
            self.ids.show_verif_passwd_img.icon = "eye"
            self.ids.verif_passwd.password = True

    def switch_to_login(self, dt):
        self.ids.full_name.text = ""
        self.ids.passwd.text = ""
        self.ids.verif_passwd.text = ""
        self.ids.nik.text = ""
        self.ids.email.text = ""
        self.ids.telp.text = ""
        self.ids.provinsi.text = ""
        self.ids.kab_kota.text = ""
        self.ids.kecamatan.text = ""
        self.ids.kelurahan.text = ""
        self.ids.rw.text = ""
        self.ids.rt.text = ""
        self.manager.transition.direction = "right"
        self.manager.current = "login"
        self.ids.false_cred.text = ""

    def register(self):
        new_full_name = str(self.ids.full_name.text)
        new_passwd = str(self.ids.passwd.text)
        new_verif_passwd = str(self.ids.verif_passwd.text)
        new_nik = str(self.ids.nik.text)
        new_email = str(self.ids.email.text)
        new_telp = str(self.ids.telp.text)
        new_prov = str(self.ids.provinsi.text)
        new_kab_kota = str(self.ids.kab_kota.text)
        new_kecamatan = str(self.ids.kecamatan.text)
        new_kelurahan = str(self.ids.kelurahan.text)
        new_rw = str(self.ids.rw.text)
        new_rt = str(self.ids.rt.text)

        if new_full_name != "" and new_passwd != "" and new_verif_passwd != "" and new_prov != "" and new_kab_kota != "" and new_kecamatan != "" and new_kelurahan != "" and new_rw != "" and new_rt != "" and new_email != "" and new_telp != "" and new_nik != "":
            if all(x.isalpha() or x.isspace() for x in new_full_name) and not new_full_name.startswith(" ") and not new_full_name.endswith(" "):
                if len(new_passwd) >= 8:
                    if new_passwd == new_verif_passwd:
                        if len(new_nik) == 16 and new_nik.isnumeric():
                            email_re = re.compile('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                            if email_re.fullmatch(new_email):
                                if len(new_telp) >= 11 and len(new_telp) <= 13 and new_telp.startswith("08") and new_telp.isnumeric():
                                    if self.fb.is_registered(nik=new_nik, email=new_email, no_telepon=new_telp, mode="register") == False:
                                        new_data = {
                                            'nama_lengkap': str(new_full_name.title()),
                                            'password': str(self.fb.encrypt(new_passwd)),
                                            'email': str(new_email.lower()),
                                            'no_telepon': str(new_telp),
                                            'provinsi': str(new_prov),
                                            'kab_kota': str(new_kab_kota),
                                            'kecamatan': str(new_kecamatan),
                                            'kelurahan': str(new_kelurahan),
                                            'rw': str(new_rw),
                                            'rt': str(new_rt),
                                            'remember_me': "False",
                                            'last_login': f'{dt.datetime.now()}'
                                        }

                                        refer = db.reference(f"/users/{str(new_nik)}")
                                        refer.set(new_data)

                                        self.ids.full_name.text = ""
                                        self.ids.passwd.text = ""
                                        self.ids.verif_passwd.text = ""
                                        self.ids.nik.text = ""
                                        self.ids.email.text = ""
                                        self.ids.telp.text = ""
                                        self.ids.provinsi.text = ""
                                        self.ids.kab_kota.text = ""
                                        self.ids.kecamatan.text = ""
                                        self.ids.kelurahan.text = ""
                                        self.ids.rw.text = ""
                                        self.ids.rt.text = ""
                                        self.ids.false_cred.text = "Akun Berhasil Dibuat"
                                        self.ids.false_cred.color = (0.1, 0.8, 0.1)
                                        Clock.schedule_once(self.switch_to_login, 3)
                                        return True

                                    return self.error_label("Kredensial Sudah Terdaftar")
                                return self.error_label("Nomor Telepon Harus Angka Dan Terdiri Dari 12-14 Digit")
                            return self.error_label("Email Tidak Boleh Ada Spasi dan Harus Diakhiri Dengan @gmail.com")
                        return self.error_label("NIK Harus 16 Angka")
                    return self.error_label("Password Tidak Sama")
                return self.error_label("Password Harus Lebih Dari 8 Karakter")
            return self.error_label("Masukan Nama Dengan Benar")
        return self.error_label("Masukan Data Dengan Benar")

class MenuWindow(MDScreen):
    welcome = ObjectProperty(None)
    schedule = ObjectProperty(None)
    fb = Firebase("schedule")

    def on_enter(self, *args):
        global logged_in
        self.ids.welcome.text = f"      [color=#FFFFFF]Halo, {logged_in}![/color]"

        self.ids.schedule.clear_widgets()

        schedule_data = self.fb.get_schedule()
        if schedule_data != False:
            for key in schedule_data:
                for item in schedule_data[key]:
                    self.ids.schedule.add_widget(
                        TwoLineListItem(
                            text=f"{item}",
                            secondary_text=f"{key}",
                        )
                    )

class UmumWindow(MDScreen):
    pass

class PersonalWindow(MDScreen):
    status_laporan = ObjectProperty(None)
    fb = Firebase("laporan")

    def on_enter(self, *args):
        self.ids.status_laporan.clear_widgets()

        laporan_data = self.fb.get_laporan()

        if laporan_data != False:
            for tanggal in laporan_data:
                for waktu in laporan_data[tanggal]:
                    for laporan in laporan_data[tanggal][waktu]:
                        self.ids.status_laporan.add_widget(
                            ThreeLineListItem(
                                text=f"{laporan}",
                                secondary_text=f"{laporan_data[tanggal][waktu][laporan]}",
                                tertiary_text=f"Diajukan Sejak {tanggal}",
                            )
                        )

class KegiatanWindow(MDScreen):
    tabel_kegiatan = ObjectProperty(None)

    def on_enter(self, *args):

        temp = [["Pemilu Ketua RT", "10-8-2022"],
            ["Lomba Perayaan Kemerdekaan", "18-8-2022"],
            ["Gotong Royong Pembersihan Got", "25-8-2022"],
            ["Fogging", "26-8-2022"],
            ["Perkawinan Andi dan Siti", "30-8-2022"]
        ]
        self.ids.tabel_kegiatan.clear_widgets()
        for i in range(5):
            self.ids.tabel_kegiatan.add_widget(
                TwoLineListItem(
                    text=temp[i][0],
                    secondary_text=temp[i][1]
                )
            )

class KasWindow(MDScreen):
    riwayat_kas = ObjectProperty(None)
    fb = Firebase("riwayat_kas")

    def on_enter(self, *args):
        self.ids.riwayat_kas.clear_widgets()

        riwayat_kas_data = self.fb.get_riwayat_kas()

        for key in riwayat_kas_data:
            for item in riwayat_kas_data[key]:
                self.ids.riwayat_kas.add_widget(
                    ThreeLineListItem(
                        text=f"{item}",
                        secondary_text=f"{key}",
                        tertiary_text=f"{riwayat_kas_data[key][item]}"
                    )
                )

class TagihanWindow(MDScreen):
    total_tagihan = ObjectProperty(None)
    deadline = ObjectProperty(None)

    def on_enter(self, *args):
        self.ids.total_tagihan.text = f"[color=#FFFFFF]Rp 1.000.000,00[/color]"
        self.ids.deadline.text = f"[color=#FFFFFF]Deadline: 01/01/1970[/color]"

class VotingWindow(MDScreen):
    pass

class DaruratWindow(MDScreen):
    nomor_darurat = ObjectProperty(None)

    def on_enter(self, *args):
        temp = [["112", "Polisi"],
            ["118", "Ambulans"],
            ["113", "Pemadam Kebakaran"],
            ["115", "SAR/BASARNAS"],
            ["129", "Posko Bencana Alam"],
            ["122", "Posko Kewaspadaan Nasional"],
            ["123", "Informasi dan Perbaikan Kerusakan dan Gangguan Listrik"],
            ["119", "Hotline Covid-19"]
        ]
        self.ids.nomor_darurat.clear_widgets()
        for i in range(len(temp)):
            self.ids.nomor_darurat.add_widget(
                TwoLineListItem(
                    text=temp[i][0],
                    secondary_text=temp[i][1]
                )
            )

class TugasManagementWindow(MDScreen):
    list_tugas = ObjectProperty(None)

    def on_enter(self, *args):
        self.ids.list_tugas.clear_widgets()
        temp = [["Bapak Sutarmo dengan jabatan RT", "Bertugas untuk memerintah di RT"], 
            ["Ibu Suharti dengan jabatan RW", "Bertugas untuk memerintah di RW"],
            ["Ibu Siti dengan jabatan Bendahara", "Bertugas untuk menghitung uang kas RW"]
        ]
        for i in range(3):
            self.ids.list_tugas.add_widget(
                TwoLineListItem(
                    text=temp[i][0],
                    secondary_text=temp[i][1]
                )
            )

class BeritaWargaWindow(MDScreen):
    list_berita = ObjectProperty(None)

    def on_enter(self, *args):
        self.ids.list_berita.clear_widgets()
        temp = [["Ditemukan Ular di Selokan", "Ditemukan ular sepanjang 2 meter dalam selokan jalan supratman", "24-7-2022"], 
            ["Bapak Armin meninggal", "Bapak Armin meninggal 2 hari yang lalu dengan umur 92 tahun", "30-7-2022"]
        ]
        for i in range(2):
            self.ids.list_berita.add_widget(
                ThreeLineListItem(
                    text=temp[i][0],
                    secondary_text=temp[i][1],
                    tertiary_text = temp[i][2]
                )
            )

class DaftarWargaWindow(MDScreen):
    pass

class PengajuanDokumenWindow(MDScreen):
    pengajuanktp = ObjectProperty(None)
    kalendar = ObjectProperty(None)

    def on_enter(self, *args):
        self.ids.kalendar.text = "Pertemuan akan diselenggarakan pada: "

    def ajukan(self):
        pass

    def on_checkbox_active(self, checkbox, value):
        if value:
            print(f"{checkbox} active, {checkbox.state} state")
        else:
            print(f"{checkbox} not active, {checkbox.state} state")

    def on_save(self, instance, value, date_range):
        self.ids.kalendar.text = f"Pertemuan akan diselenggarakan pada: {value}"

    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self):
        now = dt.datetime.now()
        date_dialog = MDDatePicker(
            title="Pilih Tanggal",
            title_input="Masukan Tanggal",
            year=now.year,
            month=now.month,
            day=now.day
        )
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

class PelaporanMasalahWindow(MDScreen):
    nama_masalah = ObjectProperty(None)
    tanggal_kejadian = ObjectProperty(None)
    deskripsi = ObjectProperty(None)

    def on_enter(self, *args):
        self.ids.nama_masalah.text = ""
        self.ids.tanggal_kejadian.text = ""
        self.ids.deskripsi.text = ""
    
    def laporkan(self):
        pass

class PengurusVoteWindow(MDScreen):
    pengurus_list = ObjectProperty(None)
    icon = StringProperty()

    def on_enter(self, *args):
        self.ids.pengurus_list.clear_widgets()
        for i in range(3):
            self.ids.pengurus_list.add_widget(
                PengurusListItem(text=f"Pengurus Ke-{i}", icon=f"./images/test_pengurus{i+1}.png")
            )

class SolusiVoteWindow(MDScreen):
    solusi_list = ObjectProperty(None)

class WindowManager(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        return Builder.load_file("main.kv")

if __name__ == "__main__":
    MainApp().run()