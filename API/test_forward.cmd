@echo off
echo Sending test messages...

curl -G "http://localhost:8007/forward" ^
  --data-urlencode "msg=Your OTP is 482910" ^
  --data-urlencode "time=2026-03-04 08:00:00" ^
  --data-urlencode "in-number=MPESA" ^
  --data-urlencode "filter-name=safaricom"

curl -G "http://localhost:8007/forward" ^
  --data-urlencode "msg=You have received KES 1,500 from John Doe" ^
  --data-urlencode "time=2026-03-04 09:15:00" ^
  --data-urlencode "in-number=MPESA" ^
  --data-urlencode "filter-name=safaricom"

curl -G "http://localhost:8007/forward" ^
  --data-urlencode "msg=Your package has been dispatched" ^
  --data-urlencode "time=2026-03-04 10:30:00" ^
  --data-urlencode "in-number=+254700123456" ^
  --data-urlencode "filter-name=jumia"

echo.
echo Done! Check http://localhost:8007 to view messages.
pause