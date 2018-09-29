from decouple import config


tessdata_dir = config('TEPCO_BILL_TESSDATA_DIR', cast=str, default='/usr/local/share/tessdata')

