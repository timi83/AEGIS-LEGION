
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000
curl -v http://127.0.0.1:8000/api/health
curl -v http://127.0.0.1:8000/
