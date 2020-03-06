# OCR
Optical Character Recognition to read float numbers and ON/OFF text from GUI.

Not every GUI may be controlled using Selenium or other tools.
Sometimes OCR functionality may help in such difficult situation.

This library allows to read float numbers and ON/OFF string for later pressing GUI buttons and adjusting values.
Library reads values by comparing captured numbers with reference image, saved in the reference_images folder.

Use get_number() method to get float number or ON/OFF value.
Use get_background() method to get button's background.
