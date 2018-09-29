## Cài đặt môi trường

* OpenCV 3 (Tham khảo: https://bitbucket.org/snippets/banglh/zepeMo/compile-opencv-34-with-python-3-on-ubuntu)
* Tesseract 4.0 (Tham khảo: https://bitbucket.org/snippets/banglh/ne8ejb/compile-tesseract-40-on-ubuntu-1804). Download các file jpn.traineddata, jpn_vert.traineddata, eng.traineddata từ repo https://github.com/tesseract-ocr/tessdata_fast và lưu vào /usr/local/share/tessdata/
* Các package trong file requirements.txt

## Chạy chương trình

1. `cp .env.example .env`

2. Sửa đường dẫn gán cho biến DRIVER_LICENSE_TESSDATA_DIR trong file .env thành /usr/local/share/tessdata

3. Edit file driver_license_main.py
    * sửa danh sách đường dẫn tới ảnh bằng lái gán cho biến `image_paths`
    * sửa giá trị cho biến `debug_output_dir`
    * gán biến `debug = True`
    
    Trong quá trình chạy sẽ hiện lên cửa sổ hiển thị cho mục đích debug thì nhấn phím bất kỳ đề bỏ qua.
    Các box tên, ngày sinh, ... sẽ được export ra thư mục `debug_output_dir`, với mỗi ảnh bằng lái tên file lưu các box giống nhau nên nếu image_paths chứa nhiều ảnh thì các file ảnh box của ảnh bằng lái sau sẽ ghi đè bằng lái trước.

4. Run: `python driver_license_main.py`
    
