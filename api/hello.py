def handler(request, response):
    response.status_code = 200
    response.set_header('Content-Type', 'application/json')
    response.write('{"ok": true, "message": "hello from api/hello"}')
