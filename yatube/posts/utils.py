from django.core.paginator import Paginator
from django.conf import settings


def paginator(request, post_list):
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
