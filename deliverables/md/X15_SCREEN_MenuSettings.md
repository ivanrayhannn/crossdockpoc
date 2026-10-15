# Screen – Menu Settings (X15)

Sumber: UISS-Screen `X15_UISS_Screen_MenuSettings.xlsx` (0.1 Initial Draft, 15-Oct-26). Prototype: menu **Common → Menu Settings** (https://ivanrayhannn.github.io/crossdockpoc/#/menu-settings).

## Tujuan
- Admin panel untuk memilih menu sidebar mana yang **ditampilkan** dan mana yang **disembunyikan**.

## Poin utama
- Satu kartu per grup sidebar (Ordering, ASN, Master, Common, …), satu checkbox per menu (tercentang = tampil).
- **Show all / Hide all** per grup, dan **Show all** di header untuk menampilkan semua menu.
- Perubahan **langsung berlaku** di sidebar, tanpa tombol Save.
- Grup yang semua menunya disembunyikan tidak tampil di sidebar.
- **Menu Settings selalu tampil** (checkbox disabled), supaya menu yang disembunyikan bisa ditampilkan lagi.
- Counter: "{n} of {m} menus shown".

## Tabel
- **TB_M_MENU_VISIBILITY** (usulan): ROLE_CD, MENU_GROUP, MENU_ITEM, SHOW_FLAG ('Y' / 'N'), CREATED_BY / DT, CHANGED_BY / DT.

## Catatan prototype
- Setting disimpan di browser (localStorage). Di NSP disimpan di tabel di atas.

## Open points
- Setting berlaku per role atau global (semua user)?
- Siapa yang boleh membuka layar ini (admin saja?).
