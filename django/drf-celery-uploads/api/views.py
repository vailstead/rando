import os
import tempfile
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from .tasks import process_csv, long_running_task

@api_view(['GET'])
def hello_world(request):
    long_running_task.delay()
    return Response({"message": "Hello, world!"})

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_csv(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    if not file_obj.name.endswith('.csv'):
        return Response({"error": "Only .csv files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, file_obj.name)

    with open(temp_file_path, 'wb+') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    process_csv.delay(temp_file_path)

    return Response({
        "message": "File uploaded successfully",
        "temp_path": temp_file_path
    }, status=status.HTTP_201_CREATED)
