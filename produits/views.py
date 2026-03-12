from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg, Min, Max, Count, F
from .models import Produit


# ─── Vue 1 — Tous les produits ────────────────────────────────
@api_view(['GET'])
def get_produits(request):
    """Retourne la liste des produits"""
    produits = Produit.objects.all()[:50]
    data = []
    for p in produits:
        data.append({
            'nom': p.nom,
            'categorie': p.categorie,
            'prix': float(p.prix) if p.prix else 0,
            'magasin': p.magasin,
            'date': str(p.date)
        })
    return Response(data)


# ─── Vue 2 — Prix moyen par catégorie ─────────────────────────
@api_view(['GET'])
def stats_categories(request):
    """Prix moyen, min, max par catégorie"""
    stats = Produit.objects.values('categorie').annotate(
        prix_moyen=Avg('prix'),
        prix_min=Min('prix'),
        prix_max=Max('prix'),
        nb_produits=Count('id')
    ).order_by('-prix_moyen')

    data = []
    for s in stats:
        data.append({
            'categorie': s['categorie'],
            'prix_moyen': round(float(s['prix_moyen']), 2),
            'prix_min': float(s['prix_min']),
            'prix_max': float(s['prix_max']),
            'nb_produits': s['nb_produits']
        })
    return Response(data)


# ─── Vue 3 — Écart de prix entre magasins ─────────────────────
@api_view(['GET'])
def stats_magasins(request):
    """Prix moyen par magasin + magasin le plus compétitif"""
    stats = Produit.objects.values('magasin').annotate(
        prix_moyen=Avg('prix'),
        prix_min=Min('prix'),
        prix_max=Max('prix'),
        nb_produits=Count('id')
    ).order_by('prix_moyen')

    data = list(stats)

    # Calcul écart entre magasin le plus cher et moins cher
    if len(data) >= 2:
        ecart = float(data[-1]['prix_moyen']) - float(data[0]['prix_moyen'])
        ecart_pct = round(ecart / float(data[0]['prix_moyen']) * 100, 2)
    else:
        ecart = 0
        ecart_pct = 0

    result = []
    for s in data:
        result.append({
            'magasin': s['magasin'],
            'prix_moyen': round(float(s['prix_moyen']), 2),
            'prix_min': float(s['prix_min']),
            'prix_max': float(s['prix_max']),
            'nb_produits': s['nb_produits']
        })

    return Response({
        'magasins': result,
        'magasin_moins_cher': result[0]['magasin'] if result else None,
        'magasin_plus_cher': result[-1]['magasin'] if result else None,
        'ecart_prix': round(ecart, 2),
        'ecart_pourcentage': ecart_pct
    })


# ─── Vue 4 — Top produits les plus chers ──────────────────────
@api_view(['GET'])
def top_produits(request):
    """Top 10 produits les plus chers"""
    produits = Produit.objects.order_by('-prix')[:10]
    data = []
    for p in produits:
        data.append({
            'nom': p.nom,
            'categorie': p.categorie,
            'prix': float(p.prix) if p.prix else 0,
            'magasin': p.magasin,
        })
    return Response(data)


# ─── Vue 5 — Inflation par catégorie ──────────────────────────
@api_view(['GET'])
def inflation_categories(request):
    """
    Calcule l'écart entre prix min et max par catégorie
    comme indicateur d'inflation/variation
    """
    stats = Produit.objects.values('categorie').annotate(
        prix_min=Min('prix'),
        prix_max=Max('prix'),
        prix_moyen=Avg('prix'),
        nb_produits=Count('id')
    )

    data = []
    for s in stats:
        prix_min = float(s['prix_min'])
        prix_max = float(s['prix_max'])
        if prix_min > 0:
            variation = round((prix_max - prix_min) / prix_min * 100, 2)
        else:
            variation = 0
        data.append({
            'categorie': s['categorie'],
            'prix_min': prix_min,
            'prix_max': prix_max,
            'prix_moyen': round(float(s['prix_moyen']), 2),
            'variation_pct': variation,
        })

    # Trier par variation décroissante
    data.sort(key=lambda x: x['variation_pct'], reverse=True)
    return Response(data)


# ─── Vue 6 — Variations par date ──────────────────────────────
@api_view(['GET'])
def variations_date(request):
    """Prix moyen par date — pour voir les variations saisonnières"""
    stats = Produit.objects.values('date').annotate(
        prix_moyen=Avg('prix'),
        nb_produits=Count('id')
    ).order_by('date')

    data = []
    for s in stats:
        data.append({
            'date': str(s['date']),
            'prix_moyen': round(float(s['prix_moyen']), 2),
            'nb_produits': s['nb_produits']
        })
    return Response(data)


# ─── Vue 7 — KPIs principaux ──────────────────────────────────
@api_view(['GET'])
def kpis(request):
    """Tous les KPIs du projet"""

    # Données de base
    total = Produit.objects.count()
    prix_moyen = Produit.objects.aggregate(
        Avg('prix'))['prix__avg']
    nb_categories = Produit.objects.values(
        'categorie').distinct().count()
    nb_magasins = Produit.objects.values(
        'magasin').distinct().count()

    # Magasin le plus compétitif
    magasins = Produit.objects.values('magasin').annotate(
        prix_moyen=Avg('prix')
    ).order_by('prix_moyen')
    magasin_competitif = magasins[0]['magasin'] if magasins else None

    # Produit avec la plus forte fluctuation
    # (prix max - prix min par nom de produit)
    produits_stats = Produit.objects.values('nom').annotate(
        prix_min=Min('prix'),
        prix_max=Max('prix'),
    )
    produit_fluctuation = None
    max_fluctuation = 0
    for p in produits_stats:
        if p['prix_min'] and p['prix_max']:
            fluctuation = float(p['prix_max']) - float(p['prix_min'])
            if fluctuation > max_fluctuation:
                max_fluctuation = fluctuation
                produit_fluctuation = p['nom']

    # Indice de variation des prix global
    tous_prix = Produit.objects.aggregate(
        min=Min('prix'), max=Max('prix')
    )
    if tous_prix['min'] and float(tous_prix['min']) > 0:
        indice_variation = round(
            (float(tous_prix['max']) - float(tous_prix['min']))
            / float(tous_prix['min']) * 100, 2
        )
    else:
        indice_variation = 0

    return Response({
        'total_produits': total,
        'prix_moyen_global': round(float(prix_moyen), 2) if prix_moyen else 0,
        'nb_categories': nb_categories,
        'nb_magasins': nb_magasins,
        'magasin_plus_competitif': magasin_competitif,
        'produit_forte_fluctuation': produit_fluctuation,
        'indice_variation_prix': f"{indice_variation}%",
    })