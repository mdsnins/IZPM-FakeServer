# IZPM-FakeServer

The fake server project for keeping IZ\*ONE Private Mail application


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