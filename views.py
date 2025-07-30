import os
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from datetime import datetime

def lade_json(pfad):
    if os.path.exists(pfad):
        try:
            with open(pfad, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Fehlerhafte JSON-Datei: {pfad}")
    return []

def speichere_json(pfad, daten):
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)

def servus(request):
    eben = datetime.now()
    return HttpResponse(f"servus! Uhrzeit eben: {eben:%Hh %Mm %Ss}")

def aPlusB(request):
    a = int(request.GET["a"])
    b = int(request.GET["b"])
    return HttpResponse(a + b)

def dynHtmlSeite(request):
    name = request.GET.get("name", "-")
    farbe = request.GET.get("color", "yellow")
    return HttpResponse(f'<h1 style="color:{farbe}">{name}</h1>')

def seiteMitTemplate(request):
    todo = ["Python lernen", "Django lernen", "Schummelzettel schreiben", "An Projekt arbeiten"]
    bildchen = {
        "katze": "https://cdn.pixabay.com/photo/2022/10/19/22/15/cat-7533717_1280.jpg",
        "hund": "https://cdn.pixabay.com/photo/2022/05/25/09/39/animal-7220153_1280.jpg"
    }
    vars = {
        "farbe": request.GET.get("color", "pink"),
        "name": request.GET.get("name", ""),
        "todos": todo,
        "bildchen": bildchen
    }
    return render(request, "ersteApp/template.html", vars)

def seiteMitForm(request):
    if request.method == "POST" and request.FILES["datei"]:
        datei = request.FILES["datei"]
        FileSystemStorage().save(datei.name, datei)
    return render(request, "ersteApp/form.html")

@csrf_exempt
def bewertung_dine(request):
    email = request.session.get("user_email")
    if not email:
        print("Anmeldung geht nicht")
        return redirect("login")

    bewertungen_path = os.path.join(settings.MEDIA_ROOT, "bewertungen.json")
    favoriten_path = os.path.join(settings.MEDIA_ROOT, "favoriten.json")
    restaurants_path = os.path.join(settings.MEDIA_ROOT, "restaurants.json")

    def load_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    if request.method == "POST":
        restaurant_id = request.POST.get("restaurant_id")
        bewertung = request.POST.get("bewertung")

        bewertungen = load_json(bewertungen_path)
        bewertungen.append({
            "email": email,
            "restaurant_id": str(restaurant_id),
            "bewertung": bewertung
        })
        with open(bewertungen_path, "w", encoding="utf-8") as f:
            json.dump(bewertungen, f, ensure_ascii=False, indent=2)

        if bewertung == "gut":
            favoriten = load_json(favoriten_path)
            favoriten.append({
                "email": email,
                "restaurant_id": str(restaurant_id)
            })
            with open(favoriten_path, "w", encoding="utf-8") as f:
                json.dump(favoriten, f, ensure_ascii=False, indent=2)
            return redirect("Match")
        return redirect("Hauptseite")

    restaurants = load_json(restaurants_path)
    bewertungen = load_json(bewertungen_path)

    bereits_bewertet_ids = []
    for b in bewertungen:
        if b["email"] == email:
            bereits_bewertet_ids.append(str(b["restaurant_id"]))

    print("DEBUG: Bewertet:", bereits_bewertet_ids)
    print("DEBUG: Alle:", [str(r["restaurant_id"]) for r in restaurants])

    naechstes_restaurant = None
    for r in restaurants:
        if str(r["restaurant_id"]) not in bereits_bewertet_ids:
            naechstes_restaurant = r
            break
    print("Test1")
    if naechstes_restaurant:
        print("Test2")
        return render(request, "ersteApp/dinefindhome.html", {"restaurant": naechstes_restaurant})
    else:
        print("Test3")
        return redirect("AlleB")
        

def favoriten_dine(request):
    email = request.session.get("user_email")
    if not email:
        return redirect("login")

    favoriten_path = os.path.join(settings.MEDIA_ROOT, "favoriten.json")
    restaurants_path = os.path.join(settings.MEDIA_ROOT, "restaurants.json")

    favoriten = lade_json(favoriten_path)
    restaurants = lade_json(restaurants_path)

    user_favoriten_ids = []
    for f in favoriten:
        if f["email"] == email:
            user_favoriten_ids.append(f["restaurant_id"])

    user_favoriten = []
    for r in restaurants:
        if r["restaurant_id"] in user_favoriten_ids:
            user_favoriten.append(r)

    return render(request, "ersteApp/dinefindfavoriten.html", {"favoriten": user_favoriten})

@csrf_exempt
def anmeldung_dine(request):
    if request.method == "POST":
        email = request.POST.get("email")
        passwort = request.POST.get("passwort")
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        file_path = os.path.join(fs.location, 'privatpersonen.json')

        daten = lade_json(file_path)

        nutzer = None
        for p in daten:
            if p["email"] == email and p["passwort"] == passwort:
                nutzer = p
                break

        if nutzer:
            print(f"[INFO] Login erfolgreich für {email}")
            request.session["user_email"] = email
            request.session.modified = True
            print("Session übergeben")
            return redirect("Hauptseite")
        else:
            print(f"[WARN] Falsche Zugangsdaten für {email}")
            return HttpResponse("Falsche E-Mail oder Passwort.", status=401)

    return render(request, "ersteApp/dinefindanmeldung.html")

@csrf_exempt
def registrierung_dine(request):
    if request.method == "POST":
        vorname = request.POST.get("vorname")
        nachname = request.POST.get("nachname")
        email = request.POST.get("email")
        passwort = request.POST.get("passwort")

        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        file_path = os.path.join(fs.location, 'privatpersonen.json')

        daten = lade_json(file_path)

        if any(p["email"] == email for p in daten):
            print(f"Registrierung: E-Mail schon verwendet {email}")
            return HttpResponse("E-Mail schon verwendet", status=400)

        daten.append({
            "vorname": vorname,
            "nachname": nachname,
            "email": email,
            "passwort": passwort
        })
        speichere_json(file_path, daten)
        print(f"[INFO] Registrierung erfolgreich für {email}")

        request.session["user_email"] = email
        request.session.modified = True
        request.session.save()

        return redirect("Hauptseite")

    return render(request, "ersteApp/dinefindregistrierung.html")

def match_dine(request):
    return render(request, "ersteApp/dinefindmatch.html")

def allebewertet_dine(request):
    return render(request, "ersteApp/dinefindallebewertet.html")

