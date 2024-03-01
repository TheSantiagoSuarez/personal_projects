from django.shortcuts import render

def home(request):
    images_list = ['static/images/sami.png', 'static/images/ruslan.png', 'static/images/shrey.png']
    table_data = [('Youssef E', 20), ('Willy', 45), ('Shrey', 56)]

    # Preprocess table_data
    processed_table_data = [{'index': index, 'manager': manager, 'points': points} for index, (manager, points) in enumerate(table_data)]

    context = {
        'images_list': images_list,
        'table_data_list': processed_table_data,
    }
    
    return render(request, 'home.html', context)


def points(request):
    return render(request, "points.html")

def players(request):
    return render(request, "players.html")

def draft(request):
    return render(request, "draft.html")
