from django.contrib import admin
from django.urls import path
from ersteApp import views as app_views

urlpatterns = [
    path("gruß", app_views.servus),
    path("template", app_views.seiteMitTemplate),
    path("dynhtml", app_views.dynHtmlSeite),
    path("plus", app_views.aPlusB),
    path("form", app_views.seiteMitForm),
    path("dinefind/home", app_views.bewertung_dine, name="Hauptseite"),
    path("dinefind/anmeldung", app_views.anmeldung_dine, name="login"),
    path("dinefind/registrieren", app_views.registrierung_dine, name="registr"),
    path("dinefind/favoriten", app_views.favoriten_dine, name="Favoriten"),
    path("dinefind/match", app_views.match_dine, name="Match"),
    path("dinefind/allesbewertet", app_views.allebewertet_dine, name="AlleB")
]