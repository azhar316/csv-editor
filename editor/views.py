import csv
import os

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404

from .models import File
from . import utils


def index(request):
    if request.method == 'GET':
        return render(request, 'editor/index.html', {})

    elif request.method == 'POST':
        file = request.FILES.get('file', None)

        if file is None or not file.name.endswith('.csv'):
            return render(request, 'editor/index.html', {'error': 'upload a valid csv file'})

        file_obj = File.objects.create(file=file)
        file_path = utils.get_abs_file_path(file_obj.file.url)

        try:
            file_data = utils.read_csv_file(file_path, 5)
        except csv.Error as e:
            return render(request, 'editor/index.html',
                          {'error': "an error occurred while reading the csv file"})

        header = file_data[0]
        content = file_data[1]
        if header is None:
            header = [i for i in range(len(content[0]))]

        pk = file_obj.pk
        context = {'header': header, 'content': content, 'pk': pk}
        return render(request, 'editor/index.html', context)


def update_view(request):
    if request.method == 'GET':
        return render(request, 'editor/index.html', {'error': 'select a valid csv file to edit'})

    elif request.method == 'POST':
        form_data = request.POST
        pk = form_data.get('pk')
        update_type = int(form_data.get('update_type'))
        column_id = int(form_data.get('column'))
        file_obj = get_object_or_404(File, pk=pk)
        file_path = utils.get_abs_file_path(file_obj.file.url)

        file_data = None

        if update_type == 1:
            value = form_data.get('value')
            try:
                utils.update_csv_with_given_value(file_path, column_id, value)
                file_data = utils.read_csv_file(file_path, 5)
            except csv.Error as e:
                return JsonResponse({'error': e})
        else:
            min_range = int(form_data.get('min_range'))
            max_range = int(form_data.get('max_range'))
            try:
                utils.update_csv_with_given_range(file_path, column_id, min_range, max_range)
                file_data = utils.read_csv_file(file_path, 5)
            except csv.Error:
                return JsonResponse({'error': "an error occurred while reading the csv file"})
            except TypeError:
                return JsonResponse({'error': "columns must be of numeric type for range updates"})

        header = file_data[0]
        content = file_data[1]
        return JsonResponse({'header': header, 'content': content})


def download(request, pk):
    file_obj = get_object_or_404(File, pk=pk)
    file_path = utils.get_abs_file_path(file_obj.file.url)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        return response
    raise Http404

