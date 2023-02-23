# Crawler Template cho khung thực thi ETL
***
## Môi trường
***
Tất cả mã nguồn xử lý và sử dụng tài nguyên đặt trong utils  
(Tài nguyên gồm: kho lưu trữ, tài nguyên tính toán, nhật ký, selenium)


#### Python Requirements
```angular2html
python 3.8
python -m venv env
env/Scripts/activate
pip install -r requirements.txt
```
#### Environment Variables   
Danh sách các biến môi trường được phép sử dụng liệt kê trong  ```.env.prod```  
Trong môi trường dev, thiết đặt trong ```.env.dev```

## Common Flowchart
***
### Run
Mã nguồn crawl thực thi theo task, tức là bắt đầu bởi các thiết đặt cho nhiệm vụ và kết thúc khi nhiệm vụ hoàn tất.  
VD:
* Thu thập các báo báo mới của trang abc.com vào hôm nay
* Thu thập các báo báo mới của trang abc.com từ ngày 12/2/2023-14/2/2023
* Thu thập các bài viết mới trong group abc/Facebook.com với tài khoản xyz 
***
Mỗi nhiệm vụ nên có thời gian thực thi dưới 5 tiếng  
Ghi các nhật ký bằng Diary Database, các nhật ký này có thể sử dụng cho các nhiệm vụ sau  
Mỗi nhiệm vụ đều có 1 DOMAIN. VD: kenh14.com, facebook.com/account1/group1, ...
***
### Datalake
Biến môi trường DATA_LAKE quy định kho lưu trữ là Mongo hay Kafka, trong DEV ENV, sử dụng mongo.  
Minio sử dụng để lưu trữ file.  
Mỗi file đều được kèm theo 1 bản ghi miêu tả và đường dẫn file.  

DataHandler là đối tượng sử dụng  
API:
* put(item, files): item là nội dung, files là list các file kèm theo nếu có  
ex: put(item={'title': 'Thoi su VTV1'}, files = [video.mp4, cc.txt])
***
## Example Kenh14
Mã nguồn này miêu tả một crawler cho trang báo điện tử kenh14  
Có 2 chế độ: crawl báo hôm nay (env var: ARGS=new), crawl báo cũ (env var: ARGS=old)  
(Crawl 2 chiều về tương lai và về quá khứ)   
* Crawl báo mới sử dụng setting là datetime.now để luôn cào ngày mới
* Crawl báo cũ sử dụng setting gồm các biến gồm ngày bắt đầu, ngày kết thúc, các biến này lưu trong Diary để nhiệm vụ tiếp theo sẽ dần về quá khứ


