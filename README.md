# 大陸居民臺灣正體字講義（靜態網站生成器）

（注意，除來自中華民國教育部的公開內容外，本講義的其他內容均採用雙重授權協議發佈，原始碼和網站內容的授權條款分開。再利用、複製和改編前請仔細閱讀[LICENSE](LICENSE.md)檔案，並做好適當標注。）

## 歡迎來到《大陸居民臺灣正體字講義》

本倉庫是《大陸居民臺灣正體字講義》的靜態網站生成器倉庫，需要將此倉庫之根目錄置於[《大陸居民臺灣正體字講義》中央主倉庫](https://github.com/zhmgczh/Notes-on-Traditional-Chinese-Characters-in-Taiwan-for-Mainland-Chinese-Residents)的根目錄下。此倉庫生成的靜態網站應位於倉庫根目錄下之「NTCCTMCR」資料夾中，故使用時可將倉庫[NTCCTMCR](https://github.com/zhmgczh/NTCCTMCR)之根目錄置於本倉庫根目錄下。依據本倉庫內容構建的網站如下：

- [《大陸居民臺灣正體字講義》（靜態備用站）](https://static.zh-tw.top/) - static.zh-tw.top （純靜態構建）

## 主要檔案說明

- [front-end_files](front-end_files/): 此資料夾包含生成的靜態網站所需之前端依賴，運行生成器之前需將此資料夾中的所有檔案拷貝至「NTCCTMCR」目錄（即靜態網站根目錄）中；
- [generator.py](generator.py)：此Python程式為靜態網站生成器主程式，直接運行即可生成整個靜態網站；
- [server.py](server.py)：此Python程式為靜態網站的本地測試伺服器，運行後可在本地對網站進行測試；
- [content_database.pkl](content_database.pkl)：所有URL對應的內容儲存在此資料庫中，若存在直接從「NTCCTMCR」資料夾刪除舊頁面檔案的情形，則重新生成前必須刪除此檔案以避免舊有頁面持續留在分類和搜尋結果中。