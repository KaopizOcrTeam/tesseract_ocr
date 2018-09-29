from decouple import config


tessdata_dir = config('DRIVER_LICENSE_TESSDATA_DIR', cast=str, default='/usr/local/share/tessdata')

