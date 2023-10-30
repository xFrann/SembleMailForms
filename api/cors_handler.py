def add_headers_to_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
