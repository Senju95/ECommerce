from django.shortcuts import render, get_object_or_404
from django.http import Http404
#from django.views import ListView
from django.views.generic import ListView, DetailView
from .models import Product

class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

class ProductFeaturedDetailView(DetailView):
    queryset = Product.objects.all().featured()
    template_name = "products/featured-detail.html"

    #def get_queryset(self, *args, **kwargs):
    #    request = self.request
    #    return Product.objects.featured()

class ProductListView(ListView):
    template_name = "products/list.html"

    #def get_context_data(self, *args, **kwargs):
     #   context = super(ProductListView, self).get_context_data(*args, **kwargs)
      #  print(context)
       # return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()

def product_list_view(request):
    print('puta')
    return render(request, "products/list.html",
        {"object_list": Product.objects.all()}
    )

class ProductDetailView(DetailView):
    #queryset = Product.objects.all()
    template_name = "products/detail.html"

    #def get_context_data(self, *args, **kwargs):
     #   context = super(ProductListView, self).get_context_data(*args, **kwargs)
      #  print(context)
       # return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist")
        return instance

    #def get_queryset(self, *args, **kwargs):
    #    request = self.request
    #    pk = self.kwargs.get('pk')
    #    return Product.objects.all().filter(pk = pk)

def product_detail_view(request, pk=None, *args, **kwargs):
    #instance = get_object_or_404(Product, pk=pk) 
    #try:
    #    instance = Product.objects.get(id=pk)
    #except Product.DoesNotExist:
    #    print('No product found')
    #    raise Http404("Product doesn't exist")
    #except:
    #    print('hub?')
    instance = Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404("Product doesn't exist")
    #qs = Product.objects.filter(id=pk)
    #if not qs.exists() or not qs.count() == 1:
     #   raise Http404("Product doesn't exist")

    return render(request, "products/detail.html",
        {"object": instance}
    )

class ProductDetailSlugView(DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        instance = get_object_or_404(Product, slug=slug, active=True)
        return instance
