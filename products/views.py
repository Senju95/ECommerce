from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views.generic import ListView, DetailView

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart

from .models import Product

class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all().featured()
    template_name = "products/featured-detail.html"


class ProductListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args,**kwargs)
        request = self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context["cart"] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()

def product_list_view(request):
    return render(request, "products/list.html",
        {"object_list": Product.objects.all()}
    )

class ProductDetailView(ObjectViewedMixin, DetailView):

    template_name = "products/detail.html"



    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist")
        return instance


def product_detail_view(request, pk=None, *args, **kwargs):

    instance = Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404("Product doesn't exist")


    return render(request, "products/detail.html",
        {"object": instance}
    )

class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args,**kwargs)
        request = self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context["cart"] = cart_obj
        return context
    

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        instance = get_object_or_404(Product, slug=slug, active=True)
        return instance
