from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from check_brenford import check_brenford

import os
import shutil


@view_config(
        route_name="home", 
        renderer="templates/home.jinja2"
)
def home_view(request):
    if request.method == "POST":
        filename = request.POST['CSVfile'].filename

        if filename.split(".")[-1].lower() == "csv":
            file_data = request.POST["CSVfile"].file

            file_path = os.path.join('uploads', filename)

            with open(file_path, 'wb') as output_file:
                shutil.copyfileobj(file_data, output_file)

            return HTTPFound(location=request.route_url("result", filename=filename))
        
        else:
            return HTTPFound(location=request.route_url("error", error_type="upload-error"))
    
    return {}

    

@view_config(
        route_name="result",
        renderer="json"
)
def result_view(request):
    filename = request.matchdict['filename']

    if filename == "random":
        brenford_proof, result = check_brenford(file=None, random_dist=True)
    else:
        file = os.path.join('uploads', filename)
        brenford_proof, result = check_brenford(file)

    if brenford_proof:
        return {
                "Success": True,
                "result": result
        }
    else:
        return HTTPFound(location=request.route_url("error", error_type="law-disproof"))


@view_config(
        route_name="error"
)
def file_upload_error_view(request):
    error_msg = request.matchdict["error_type"]
    if error_msg == "upload-error":
        raise HTTPForbidden("File should be of CSV format")
    elif error_msg == "law-disproof":
        return Response("<h3>The distribution doesnot follow Brenford Law.</h3>")