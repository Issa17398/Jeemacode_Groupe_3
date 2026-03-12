from django.db import models

# Create your models here.

class Produit(models.Model):
    nom       = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100, blank=True, null=True)
    prix      = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    magasin   = models.CharField(max_length=150, blank=True, null=True)
    date      = models.DateField(blank=True, null=True)

    class Meta:
        managed = False        # Django ne modifie pas la table
        db_table = 'produits'  # utilise la table existante

    def __str__(self):
        return f"{self.nom} - {self.prix} FCFA"