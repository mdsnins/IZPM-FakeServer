# IZPM-FakeServer

The fake server project for keeping IZ\*ONE Private Mail application.

## Server Setup

1. Clone this repository

```bash
git clone https://github.com/mdsnins/IZPM-FakeServer
cd IZPM-FakeServer
```

2. Install python requirements

```bash
pip install -r requirements.txt
cd src
```

3. Write `config.py` with your own favor. Refer [config.py.sample](./src/app/config.py.sample)

4. Edit [\_\_init\_\_.py](./src/app/__init__.py) for initialize routine

5. Construct & Intialize database

```bash
python3 run.py initdb
python3 run.py testdb
```

6. Place the private mail data properly. In this manual, it doesn't care about where images are. Static serves such as Amazon S3 are strongly recommended.

- Place `pm.js` from [IZPM-Backup](https://github.com/mdsnins/izpm-backup) in same directory with `run.py`
- Place 'mail' folder from [IZPM-Backup](https://github.com/mdsnins/izpm-backup) as `app/static/web/mail`

Then, 

```bash
python3 run.py loadpm
```

It will parse `pm.js` and insert mails into database automatically.

7. Run. You can use [uwsgi.ini.sample](./src/uwsgi.ini.sample) if you need uWSGI configuration
 
```bash
python3 run.py run  
uwsgi uwsgi.ini 
```

### iOS Binary Patch

Since retail iOS IZPM application restrict WKWebView's domain using `decidePolicyForNagivationAction`, a few binary patches are needed. Followings are information of latest iOS application, DRM decrypted using frida.

```
0x26770: 81 06 00 B4 
0x267CC: 60 03 00 36
0x929F4: 41 01 00 54
0x9F500: C3 04 00 B4
0x9F54C: 93 01 00 36
```

To remove a restriction of WKWebView, please replace all of five hex values to `1F 20 03 D5` which is the opcode of **NOP**


### Android smali patch

There is a crash while processing a mail which doesn't have an integer in mail id (such as `config/*` in this project), a simple touch is required to handle this.

**com.camobile.akb48mail.f.d**
```smali

 method public static final c(Ljava/lang/String;)I
     .locals 2
     const-string v0, "$this$parseMailIdToInt"
     invoke-static {p0, v0}, Lf/y/d/k;->c(Ljava/lang/Object;Ljava/lang/String;)V
     new-instance v0, Lf/e0/h;
     const-string v1, "[^0-9]"
     invoke-direct {v0, v1}, Lf/e0/h;-><init>(Ljava/lang/String;)V
     const-string v1, "0"  #Edit this line from const-string v1, ""
```

Edit the line 7 of static function `c`, from `const-string v1, ""` to `const-string v1, "0"`
