#from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name="ShopHome"),
    path("about/", views.about,name="aboutus"),
    path("contact/", views.contact,name="contactus"),
    path("tracker/", views.tracker,name="trackingstatus"),
    path("search/", views.search,name="Search"),
    path("products/<int:myid>", views.prodview,name="productview"),
    path("checkout/", views.checkout,name="checkout"),
    path("handlerequest/", views.handlerequest,name="handlerequest"),
]
