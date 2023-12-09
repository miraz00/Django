from django.core.paginator import Paginator


def paging(posts, page_num):
    return Paginator(posts, 10).get_page(page_num)


def paging_has_prev(posts, page_num):
    return Paginator(posts, 10).get_page(page_num).has_previous()


def paging_has_next(posts, page_num):
    return Paginator(posts, 10).get_page(page_num).has_next()

