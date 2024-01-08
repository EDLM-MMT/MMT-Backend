import random

from django.shortcuts import render
from django_renderpdf.views import PDFView


class RandomPDFView(PDFView):
    """Randomly generates PDFs to test behavior"""
    template_name = 'test.html'
    download_name = 'resume'
    # prompt_download = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['items'] = []
        num = random.randint(50, 100)
        for i in range(num):
            context['items'].append(
                {'first': 'one', 'second': 'two', 'third': i})
        return context


def html_view(request):
    context = {}
    context['items'] = []
    num = random.randint(50, 100)
    for i in range(num):
        context['items'].append(
            {'first': 'one', 'second': 'two', 'third': i})

    print(context)
    return render(request=request, template_name='test.html', context=context)
