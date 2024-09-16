程式碼更新後(.ipynb轉成.py)，利用pyinstaller重新打包成.exe
cd到有American_Stock_Analysis_For_Sale.py的folder (C:\Users\mi83\workspace)


# 更新步驟：
1. 先刪掉原本的版本(dist中的相關資料夾、build中的相關資料夾、American_Stock_Analysis_For_Sale.spec檔)
2. pyinstaller American_Stock_Analysis_For_Sale.py --icon=ME_no_bg_96.ico
   (icon=... 設定.exe檔的圖示)
3. 轉換成功後，將相關的檔案放入新建立的folder中(ME_no_bg_96.ico、info.json、logout/open/stop/ME_bar.png、同edge版本的msedgedriver)
4. 自己建立results資料夾，當作爬蟲後存檔的folder



# 所需更新的內容：
1. extract_from_reports() 中的special_case
2. plot_data() 中關於結果圖的調整
3. expiration_date; 由於只設定年/月/日，所以時/分/秒皆為0，所以此為過期日(ie: search功能自這一天起不可用)
4. 其他